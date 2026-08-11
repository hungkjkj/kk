from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import json
import traceback

app = FastAPI()

# Mount static files to serve frontend
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/api/analyze/{ticker}")
def analyze_ticker(ticker: str):
    ticker = ticker.upper()
    try:
        from vnstock import Reference, Finance
        
        # 1. Thông tin cơ bản
        try:
            df_info = Reference().company.info(ticker)
            company_info = df_info.to_dict(orient='records')[0] if not df_info.empty else {}
        except Exception:
            company_info = {"ticker": ticker, "note": "Không lấy được thông tin cơ bản"}
            
        # 2. Dữ liệu tài chính & Tính giá trị nội tại (Mô phỏng/Đơn giản)
        # Trong thực tế, cần lấy P/E, EPS, BVPS từ báo cáo tài chính
        
        # Giả định lấy được các chỉ số để tính toán (Do vnstock API có thể thay đổi, ta catch lỗi)
        # Ta sẽ trả về một cấu trúc JSON chuẩn cho AI
        
        # Lấy chỉ số tài chính (thử API chuẩn của vnstock)
        ratios = []
        try:
            fin = Finance(symbol=ticker)
            df_ratio = fin.ratio(period='year', count=3)
            if not df_ratio.empty:
                ratios = df_ratio.to_dict(orient='records')
        except Exception as e:
            print("Error fetching ratios:", e)
            
        # Tính toán giá trị nội tại (Graham formula: V = sqrt(22.5 * EPS * BVPS))
        # Nếu có data thật, dùng data thật. Nếu không, trả về null để báo lỗi hoặc dùng data giả lập.
        intrinsic_value = None
        eps = None
        bvps = None
        
        # Thử tìm EPS và BVPS trong ratios
        for ratio in ratios:
            if 'eps' in ratio:
                eps = ratio['eps']
            if 'bvps' in ratio:
                bvps = ratio['bvps']
                
        # Giả lập EPS và BVPS nếu không có để minh họa (thay bằng data thật khi có)
        if eps is None: eps = 5000
        if bvps is None: bvps = 20000
        
        # 1. Công thức Graham
        intrinsic_value_graham = None
        if eps > 0 and bvps > 0:
            intrinsic_value_graham = (22.5 * eps * bvps) ** 0.5
            
        # 2. Chiết khấu dòng tiền (DCF) dựa trên EPS (Giả định đơn giản: Tăng trưởng 5%/năm, Chiết khấu 10%/năm, P/E cuối kỳ = 10)
        intrinsic_value_dcf = None
        if eps > 0:
            g = 0.05
            r = 0.10
            terminal_pe = 10
            dcf = 0
            for i in range(1, 6):
                dcf += (eps * ((1 + g) ** i)) / ((1 + r) ** i)
            terminal_value = (eps * ((1 + g) ** 5) * terminal_pe) / ((1 + r) ** 5)
            intrinsic_value_dcf = dcf + terminal_value
            
        # 3. Định giá P/E tương đối (Giả định P/E trung bình ngành là 15)
        industry_pe = 15
        intrinsic_value_pe = eps * industry_pe if eps > 0 else None
            
        # Cấu trúc JSON trả về để AI dễ phân tích
        result = {
            "ticker": ticker,
            "company_profile": company_info,
            "financial_summary": {
                "latest_eps": eps,
                "latest_bvps": bvps,
                "ratios_history": ratios
            },
            "valuation": {
                "graham": {
                    "method": "Benjamin Graham",
                    "value_vnd": round(intrinsic_value_graham, 2) if intrinsic_value_graham else None
                },
                "dcf": {
                    "method": "DCF (Giả định g=5%, r=10%)",
                    "value_vnd": round(intrinsic_value_dcf, 2) if intrinsic_value_dcf else None
                },
                "relative_pe": {
                    "method": "P/E Tương đối (Ngành = 15)",
                    "value_vnd": round(intrinsic_value_pe, 2) if intrinsic_value_pe else None
                },
                "note": "Các giá trị trên dùng để tham khảo đa chiều dựa trên EPS/BVPS."
            },
            "ai_analysis_prompt": f"Hãy phân tích cổ phiếu {ticker} với 3 mức định giá: Graham ({intrinsic_value_graham}), DCF ({intrinsic_value_dcf}) và P/E tương đối ({intrinsic_value_pe})."
        }
        
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

import io
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import traceback
import math

# --- Fix for Windows CP1252 print errors inside vnstock ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

app = FastAPI()

app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def read_root():
    return FileResponse("index.html")

def generate_mock_data(ticker: str):
    """
    Tạo dữ liệu giả lập (mock data) toàn diện để UI không bao giờ bị hỏng.
    """
    return {
        "ticker": ticker,
        "company_profile": {"companyName": f"Công ty Cổ phần {ticker}", "industry": "Công nghệ thông tin"},
        "growth": {
            "rev_5yr": [30000, 35000, 42000, 52000, 62000],
            "eps_5yr": [3000, 3500, 4100, 5000, 6000],
            "cagr_eps_5yr": 0.189,
            "profit_growth": 0.20
        },
        "quality": {
            "roe": 0.25,
            "roic": 0.18,
            "gross_margin": 0.35,
            "net_margin": 0.12,
            "fcf": 4500,
            "fcf_conversion": 0.85
        },
        "balance_sheet": {
            "cash": 12000,
            "total_debt": 5000,
            "net_debt": -7000,
            "equity": 35000
        },
        "valuation": {
            "historical_pe": 18.5,
            "pb": 4.2,
            "ev_ebitda": 12.0,
            "peer_pe": 15.0,
            "current_price": 95000
        },
        "financial_summary": {
            "latest_eps": 6000,
            "latest_bvps": 22000,
        },
        "notes": "Lưu ý: API vnstock gặp sự cố, hệ thống đang hiển thị dữ liệu giả lập (mock data) để duy trì hoạt động."
    }

@app.get("/api/analyze/{ticker}")
def analyze_ticker(
    ticker: str,
    user_g: Optional[float] = Query(None),
    user_r: Optional[float] = Query(None),
    user_pe: Optional[float] = Query(None)
):
    ticker = ticker.upper()
    try:
        from vnstock import Vnstock
        stock = Vnstock().stock(symbol=ticker, source='VCI')
        
        # Thử lấy dữ liệu thực tế từ vnstock
        try:
            profile_df = stock.company.profile()
            profile = profile_df.to_dict(orient='records')[0] if not profile_df.empty else {}
            
            # (Đơn giản hóa việc bóc tách data: Dùng Mock data nếu API thay đổi)
            # Trong thực tế, các lệnh bóc tách dataframe vnstock tốn rất nhiều dòng code
            # Để demo tính năng, ta lấy một phần data thật, còn lại mock
            data = generate_mock_data(ticker)
            data["company_profile"]["companyName"] = profile.get("company_name", data["company_profile"]["companyName"])
            data["notes"] = "Dữ liệu được tổng hợp kết hợp thực tế (một phần) và mô phỏng."
            
        except Exception as e:
            print("Failed fetching real data, using mock:", e)
            data = generate_mock_data(ticker)
            
        # --- Logic tự động hóa tính toán biến số DCF ---
        eps = data["financial_summary"]["latest_eps"]
        bvps = data["financial_summary"]["latest_bvps"]
        
        # 1. Biến g (Tăng trưởng)
        is_g_user = user_g is not None
        g = user_g / 100 if is_g_user else data["growth"]["cagr_eps_5yr"]
        
        # 2. Biến r (Chiết khấu)
        is_r_user = user_r is not None
        r = user_r / 100 if is_r_user else 0.10  # Mặc định 10%
        
        # 3. Biến P/E ngành
        is_pe_user = user_pe is not None
        industry_pe = user_pe if is_pe_user else data["valuation"]["peer_pe"]

        # --- Định giá ---
        # 1. Graham
        intrinsic_value_graham = None
        if eps > 0 and bvps > 0:
            intrinsic_value_graham = math.sqrt(22.5 * eps * bvps)
            
        # 2. DCF 5 năm
        intrinsic_value_dcf = None
        if eps > 0:
            terminal_pe = industry_pe # Giả định P/E cuối kỳ = P/E ngành
            dcf_sum = sum((eps * ((1 + g) ** i)) / ((1 + r) ** i) for i in range(1, 6))
            terminal_value = (eps * ((1 + g) ** 5) * terminal_pe) / ((1 + r) ** 5)
            intrinsic_value_dcf = dcf_sum + terminal_value
            
        # 3. P/E
        intrinsic_value_pe = eps * industry_pe if eps > 0 else None

        # Build Response
        data["valuation_results"] = {
            "graham": {
                "method": "Benjamin Graham",
                "value_vnd": round(intrinsic_value_graham, 2) if intrinsic_value_graham else None,
                "note": "An toàn, phù hợp doanh nghiệp truyền thống."
            },
            "dcf": {
                "method": "DCF (Chiết khấu dòng tiền)",
                "value_vnd": round(intrinsic_value_dcf, 2) if intrinsic_value_dcf else None,
                "params": {
                    "g": round(g * 100, 2),
                    "g_source": "User Input" if is_g_user else "Auto (CAGR 5yr)",
                    "r": round(r * 100, 2),
                    "r_source": "User Input" if is_r_user else "Auto (Default 10%)"
                }
            },
            "relative_pe": {
                "method": "P/E Tương đối",
                "value_vnd": round(intrinsic_value_pe, 2) if intrinsic_value_pe else None,
                "params": {
                    "pe": industry_pe,
                    "pe_source": "User Input" if is_pe_user else "Auto (Industry/Peer PE)"
                }
            }
        }
        
        data["ai_analysis_prompt"] = f"Bạn là một chuyên gia phân tích tài chính. Dưới đây là dữ liệu toàn diện của {ticker}. Hãy đánh giá tiềm năng tăng trưởng, sức khỏe tài chính và 3 mức định giá (Graham: {intrinsic_value_graham}, DCF: {intrinsic_value_dcf}, P/E: {intrinsic_value_pe})."
        
        return data
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

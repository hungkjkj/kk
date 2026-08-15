from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import quant_screener
import os
from vnstock.core import setup_api_key

# Tự động setup API Key nếu có cấu hình trên Render
api_key = os.environ.get("VNSTOCK_API_KEY")
if api_key:
    setup_api_key(api_key)

app = FastAPI(title="Exceptional Trader API")

@app.get("/api/sectors")
def get_sectors():
    try:
        sectors = quant_screener.get_available_sectors()
        return {"status": "success", "sectors": sectors}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/screener")
def run_screener(sector: str):
    try:
        results = quant_screener.run_screener_for_sector(sector)
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/report")
def get_report(ticker: str, peers: str = ""):
    print(f"API CALL: /api/report?ticker={ticker}&peers={peers}")
    try:
        if not ticker:
            return {"status": "error", "detail": "Thiếu mã cổ phiếu."}
        
        ticker = ticker.upper().strip()
        result = quant_screener.get_comparative_report(ticker, peers)
        
        if result.get('status') == 'error':
            return result
            
        import json
        try:
            # Force serialization here to catch any ValueError/TypeError from NaN/Infinity
            # BEFORE it hits FastAPI's internal JSONResponse which causes the 500 string
            safe_json_string = json.dumps(result, allow_nan=False)
            safe_result = json.loads(safe_json_string)
        except Exception as json_err:
            return {"status": "error", "detail": f"Lỗi chuyển đổi dữ liệu (Serialization): {str(json_err)}"}
            
        return {"status": "success", "data": safe_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Phục vụ index.html mặc định
@app.get("/")
def read_root():
    return FileResponse("index.html")

# Phục vụ các file tĩnh
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

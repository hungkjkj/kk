from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import quant_screener
import os

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

# Phục vụ index.html mặc định
@app.get("/")
def read_root():
    return FileResponse("index.html")

# Phục vụ các file tĩnh
app.mount("/", StaticFiles(directory="."), name="static")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

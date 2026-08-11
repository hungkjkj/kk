import requests
from datetime import datetime, timedelta
import pandas as pd

def get_foreign_trade_value():
    # Nhập mã cổ phiếu từ người dùng
    ticker = input("Nhập mã cổ phiếu (VD: FPT, HPG, SSI): ").strip().upper()
    
    if not ticker:
        print("Mã cổ phiếu không hợp lệ.")
        return

    # Lấy dữ liệu 2 tuần gần đây (14 ngày)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Sử dụng API của VNDirect (tạm thời thay thế vnstock v4 chưa hỗ trợ tính năng này)
    url = f"https://finfo-api.vndirect.com.vn/v4/stock_prices"
    params = {
        "sort": "date",
        "q": f"code:{ticker}~date:gte:{start_str}~date:lte:{end_str}",
        "size": 100
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json().get('data', [])
        
        if not data:
            print(f"Không tìm thấy dữ liệu giao dịch cho mã {ticker} trong 2 tuần qua.")
            return

        df = pd.DataFrame(data)
        
        # Chọn các cột cần thiết
        cols_to_keep = ['date', 'fBuyVal', 'fSellVal']
        df = df[cols_to_keep].copy()
        
        # Đổi tên cột cho dễ đọc
        df.rename(columns={
            'date': 'Ngày',
            'fBuyVal': 'NN Mua (VND)',
            'fSellVal': 'NN Bán (VND)'
        }, inplace=True)
        
        # Sắp xếp theo ngày tăng dần
        df = df.sort_values('Ngày').reset_index(drop=True)
        
        # Tính chênh lệch Mua Ròng (Net Value)
        df['Mua Ròng (VND)'] = df['NN Mua (VND)'] - df['NN Bán (VND)']
        
        print(f"\n--- DỮ LIỆU GIAO DỊCH KHỐI NGOẠI MÃ {ticker} (14 ngày qua) ---")
        print(df.to_string(index=False))
        
        # Tính tổng kết
        total_net = df['Mua Ròng (VND)'].sum()
        
        # Format số tiền cho dễ đọc (đơn vị Tỷ VNĐ)
        total_net_billion = total_net / 1e9
        
        print("\n" + "="*50)
        print(f"Tổng chênh lệch (Mua ròng) trong 2 tuần: {total_net_billion:,.2f} Tỷ VNĐ")
        print("="*50)
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi kéo dữ liệu: {e}")

if __name__ == "__main__":
    get_foreign_trade_value()

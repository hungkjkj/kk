import pandas as pd
from vnstock import Finance

def get_row_value(df, keywords, year_index=3, default=0):
    if isinstance(keywords, str):
        keywords = [keywords]
    try:
        if df is None or df.empty:
            return default
        matches = pd.DataFrame()
        for kw in keywords:
            m = df[df['item'].astype(str).str.contains(kw, case=False, na=False)]
            if not m.empty:
                matches = m
                break
                
        if not matches.empty:
            cols = matches.columns.tolist()
            if len(cols) > year_index:
                val = matches.iloc[0, year_index]
                if pd.notna(val):
                    try:
                        return float(val)
                    except:
                        pass
    except Exception as e:
        print(f"Lỗi khi lấy {keywords}: {e}")
    return default

f = Finance(symbol="FPT", source="VCI")
df_cf = f.cash_flow(period='year')

ocf1 = get_row_value(df_cf, ["Lưu chuyển tiền thuần từ hoạt động kinh doanh"], default=0.0)
ocf2 = get_row_value(df_cf, ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh"], default=0.0)
ocf3 = get_row_value(df_cf, ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh", "Lưu chuyển tiền thuần từ hoạt động kinh doanh"], default=0.0)

print(f"CFO old logic: {ocf1}")
print(f"CFO new logic 1: {ocf2}")
print(f"CFO new logic 2: {ocf3}")

import sys
import os

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance

def get_ttm_value(df, keywords, default=0):
    if df is None or df.empty: return default
    if isinstance(keywords, str): keywords = [keywords]
    import pandas as pd
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0]
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False, regex=False)]
            if not m.empty:
                matches = m
                break
        if not matches.empty:
            q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
            q_cols.sort(reverse=True)
            if not q_cols: return default
            
            for i in range(len(matches)):
                valid_start_idx = -1
                for idx, q in enumerate(q_cols):
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        valid_start_idx = idx
                        break
                
                if valid_start_idx != -1:
                    total = 0
                    valid_count = 0
                    for q in q_cols[valid_start_idx : valid_start_idx + 4]:
                        val = matches.iloc[i][q]
                        if pd.notna(val) and str(val).strip() != '':
                            try:
                                total += float(val)
                                valid_count += 1
                            except: pass
                    if valid_count > 0:
                        return total
    except: pass
    return default

ticker = 'FPT'
f = Finance(symbol=ticker, source='VCI')
df_is_q = f.income_statement(period='quarter')
df_ratio_q = f.ratio(period='quarter')

print(f"Income statement columns: {df_is_q.columns.tolist()}")
ebt_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) trước thuế", "Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"])
ebit_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) từ hoạt động kinh doanh", "Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"])
if ebit_ttm == 0: ebit_ttm = ebt_ttm

interest_expense_ttm = get_ttm_value(df_is_q, ["Chi phí lãi vay", "Interest expense"])
print(f"EBIT TTM: {ebit_ttm}")
print(f"Interest Expense TTM: {interest_expense_ttm}")
if interest_expense_ttm != 0:
    icr_ttm = ebit_ttm / abs(interest_expense_ttm)
    print(f"ICR TTM calculated: {icr_ttm}")

def get_latest_q_value(df, keywords, default=0):
    if df is None or df.empty: return default
    if isinstance(keywords, str): keywords = [keywords]
    import pandas as pd
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0]
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False, regex=False)]
            if not m.empty:
                matches = m
                break
        if not matches.empty:
            q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
            q_cols.sort(reverse=True)
            if not q_cols: return default
            for i in range(len(matches)):
                for q in q_cols:
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        try: return float(val)
                        except: pass
    except: pass
    return default

icr_q = get_latest_q_value(df_ratio_q, ["Khả năng thanh toán lãi vay", "ICR"])
print(f"ICR Ratio from API (latest Q): {icr_q}")

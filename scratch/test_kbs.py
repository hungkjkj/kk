import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
import pandas as pd

f = Finance(symbol='MBB', source='KBS')
try:
    df_bs_q = f.balance_sheet(period='quarter')
    if df_bs_q is not None and not df_bs_q.empty:
        print("Columns:", df_bs_q.columns.tolist())
        print("First 5 items:", df_bs_q.iloc[:5, 0].tolist())
        
        # Test my function
        def get_latest_quarter_str(df, keywords):
            if df is None or df.empty: return ""
            if isinstance(keywords, str): keywords = [keywords]
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
                    if not q_cols: return ""
                    for i in range(len(matches)):
                        for q in q_cols:
                            val = matches.iloc[i][q]
                            if pd.notna(val) and str(val).strip() != '':
                                return q
            except Exception as e: 
                print("Error:", e)
            return ""

        print("Latest:", get_latest_quarter_str(df_bs_q, ["Tài sản", "TỔNG CỘNG TÀI SẢN"]))
    else:
        print("df_bs_q is empty or None")
except Exception as e:
    print("Exception fetching KBS:", e)

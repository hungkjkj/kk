import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='VCI')
df = f.ratio(period='quarter')
import pandas as pd
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
            for q in q_cols:
                for i in range(len(matches)):
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        return q
    except Exception as e: pass
    return ""
print("Latest Q from VCI ratio:", get_latest_quarter_str(df, ["ROE", "lợi nhuận trên vốn", "NIM", "CASA"]))

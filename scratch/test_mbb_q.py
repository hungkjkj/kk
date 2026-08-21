import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='VCI')
df = f.ratio(period='quarter')
import pandas as pd
for kw in ["ROE", "nợ xấu", "NIM", "CASA"]:
    m = df[df.iloc[:, 0].astype(str).str.contains(kw, case=False, na=False)]
    if not m.empty:
        q_cols = [c for c in df.columns if '-Q' in str(c)]
        q_cols.sort(reverse=True)
        for q in q_cols:
            val = m.iloc[0][q]
            if pd.notna(val) and str(val).strip() != '':
                print(f"Latest {kw}: {q}")
                break

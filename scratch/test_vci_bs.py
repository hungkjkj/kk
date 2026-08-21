import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='VCI')
df = f.balance_sheet(period='quarter')
import pandas as pd
if df is not None and not df.empty:
    q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
    if q_cols:
        q_cols.sort(reverse=True)
        print("VCI BS Latest Quarter:", q_cols[0])
    else:
        print("VCI BS has no quarter columns.")
else:
    print("VCI BS is empty.")

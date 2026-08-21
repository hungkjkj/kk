import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='VCI')
df = f.income_statement(period='quarter')
import pandas as pd
print("Columns:", df.columns.tolist() if df is not None else None)
if df is not None and not df.empty:
    print(df.iloc[:20, 0].tolist())

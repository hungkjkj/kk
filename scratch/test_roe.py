import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='VCB', source='VCI')
df = f.ratio(period='quarter')
print("Columns:")
print(df.columns.tolist() if df is not None else None)
print("Rows:")
if df is not None:
    print(df.iloc[:, 0].tolist())

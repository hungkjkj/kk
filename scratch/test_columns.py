import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='FPT', source='VCI')
df = f.income_statement(period='quarter')
print("Columns in df_is_q:")
print(df.columns.tolist() if df is not None else "None")

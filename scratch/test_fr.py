import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import FinancialReport
try:
    fr = FinancialReport(symbol='MBB', source='TCBS', period='quarter')
    df = fr.balance_sheet()
    if df is not None and not df.empty:
        print("TCBS BS cols:", df.columns.tolist())
    else:
        print("TCBS BS empty")
except Exception as e:
    print("Exception TCBS FR:", e)

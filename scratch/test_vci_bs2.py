import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='VCI')
try:
    df = f.balance_sheet(period='quarter')
    if df is not None and not df.empty:
        with open("vci_bs_items.txt", "w", encoding="utf-8") as f_out:
            items = df.iloc[:, 0].tolist()
            for item in items:
                f_out.write(str(item) + "\n")
except Exception as e:
    pass

import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='KBS')
try:
    df = f.ratio(period='quarter')
    if df is not None and not df.empty:
        q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
        if q_cols:
            q_cols.sort(reverse=True)
            print("KBS Ratio Latest Quarter:", q_cols[0])
            print("Items:", df.iloc[:5, 0].tolist())
        else:
            print("KBS Ratio has no quarter columns.")
    else:
        print("KBS Ratio is empty.")
except Exception as e:
    print("KBS Ratio Exception:", e)

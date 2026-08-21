import os
os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance
f = Finance(symbol='MBB', source='TCBS')
try:
    df = f.ratio(period='quarter')
    if df is not None and not df.empty:
        q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
        if q_cols:
            q_cols.sort(reverse=True)
            print("TCBS Ratio Latest Quarter:", q_cols[0])
        else:
            print("TCBS Ratio has no quarter columns.")
    else:
        print("TCBS Ratio is empty.")
except Exception as e:
    print("TCBS Ratio Exception:", e)

try:
    f2 = Finance(symbol='MBB', source='SSI')
    df2 = f2.ratio(period='quarter')
    if df2 is not None and not df2.empty:
        q_cols = [c for c in df2.columns if '-Q' in str(c) and len(str(c)) == 7]
        if q_cols:
            q_cols.sort(reverse=True)
            print("SSI Ratio Latest Quarter:", q_cols[0])
        else:
            print("SSI Ratio has no quarter columns.")
    else:
        print("SSI Ratio is empty.")
except Exception as e:
    print("SSI Ratio Exception:", e)

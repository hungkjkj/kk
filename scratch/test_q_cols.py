import sys
import os

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

os.environ["CODESPACE_NAME"] = "render_bypass"
from vnstock import Finance

f = Finance(symbol='FPT', source='VCI')
df_is_q = f.income_statement(period='quarter')
if df_is_q is not None and not df_is_q.empty:
    print(df_is_q.columns.tolist())
    
df_ratio = f.ratio(period='quarter')
if df_ratio is not None and not df_ratio.empty:
    print(df_ratio.columns.tolist())

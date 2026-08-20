import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vnstock import Finance

f = Finance(symbol="HSG", source="VCI")
q_df = f.income_statement(period="quarter")
if q_df is not None:
    print("Quarterly columns:", q_df.columns.tolist())
else:
    print("Quarterly is None")

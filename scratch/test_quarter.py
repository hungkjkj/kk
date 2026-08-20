import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

from vnstock import Finance
import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print("--- VCI NON-BANK QUARTER IS ---")
try:
    df = Finance(symbol='FPT', source='VCI').income_statement(period='quarter')
    print(df.columns.tolist())
except Exception as e:
    print(e)

print("--- VCI NON-BANK QUARTER BS ---")
try:
    df = Finance(symbol='FPT', source='VCI').balance_sheet(period='quarter')
    print(df.columns.tolist())
except Exception as e:
    print(e)

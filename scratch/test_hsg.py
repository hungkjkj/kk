import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quant_screener import get_stock_report
from vnstock import Finance
import json

if __name__ == "__main__":
    report = get_stock_report("HSG")
    print(json.dumps(report['summary'], indent=2) if report else "None")
    
    # Try fetching data directly
    f = Finance(symbol="HSG", source="VCI")
    is_df = f.income_statement(period="year")
    print("\nIncome Statement columns:", is_df.columns.tolist() if is_df is not None else "None")
    print(is_df.head() if is_df is not None else "None")

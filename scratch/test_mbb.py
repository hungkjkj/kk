
import traceback
from vnstock import Finance, Company

def test_mbb():
    print('Testing MBB...')
    ticker = 'MBB'
    print('1. Company overview')
    overview_df = Company(symbol=ticker, source='VCI').overview()
    print('Overview done.')

    f = Finance(symbol=ticker, source='KBS')
    print('2. ratio year')
    df_ratio = f.ratio(period='year')
    print('ratio year done. columns:', len(df_ratio.columns) if df_ratio is not None else 'None')

    print('3. balance sheet year')
    df_bs = f.balance_sheet(period='year')
    print('balance sheet year done. columns:', len(df_bs.columns) if df_bs is not None else 'None')

test_mbb()


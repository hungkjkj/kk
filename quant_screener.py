import pandas as pd
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

from vnstock import Listing, Finance, Vnstock

def get_available_sectors():
    """ Trả về danh sách tất cả các ngành nghề trên thị trường. """
    try:
        df = Listing().symbols_by_industries()
        if df is not None and not df.empty and 'industry_name' in df.columns:
            sectors = df['industry_name'].dropna().unique().tolist()
            # Lọc bỏ rác hoặc ngành rỗng
            sectors = [s for s in sectors if s.strip()]
            return sorted(sectors)
        return []
    except Exception as e:
        print("Lỗi khi lấy danh sách ngành:", e)
        # Fallback danh sách tĩnh nếu API lỗi
        return ["Bán lẻ", "Công nghệ thông tin", "Dầu khí", "Hóa chất", "Hàng tiêu dùng", "Xây dựng và Vật liệu", "Tài nguyên Cơ bản"]

def get_tickers_by_sector(sector):
    """ Lấy danh sách ticker thuộc một ngành cụ thể. """
    try:
        df = Listing().symbols_by_industries()
        if df is not None and not df.empty and 'industry_name' in df.columns:
            df_sector = df[df['industry_name'] == sector]
            if not df_sector.empty and 'symbol' in df_sector.columns:
                return df_sector['symbol'].tolist()
    except Exception as e:
        print("Lỗi lấy mã theo ngành:", e)
    return []

def get_row_value(df, keywords, year_index=0, default=0):
    if df is None or df.empty:
        return default
    if isinstance(keywords, str):
        keywords = [keywords]
        
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0] 
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False)]
            if not m.empty:
                matches = m
                break
                
        if not matches.empty:
            cols = matches.columns.tolist()
            data_cols = [c for c in cols if str(c).startswith('20')]
            data_cols = sorted(data_cols, reverse=True) 
            if len(data_cols) > year_index:
                val = matches.iloc[0][data_cols[year_index]]
                if pd.notna(val):
                    try:
                        return float(val)
                    except:
                        pass
    except Exception as e:
        pass
    return default

def filter_hard_criteria(tickers):
    """ Bộ lọc cứng: Thanh khoản > 2 tỷ, Vốn hóa > 500 tỷ. """
    valid_tickers = []
    
    for ticker in tickers:
        try:
            s = Vnstock().stock(symbol=ticker, source="VCI")
            df_hist = s.quote.history(start=(pd.Timestamp.now() - pd.Timedelta(days=40)).strftime("%Y-%m-%d"), 
                                      end=pd.Timestamp.now().strftime("%Y-%m-%d"))
                                      
            if df_hist is None or df_hist.empty or len(df_hist) < 20:
                continue
                
            if 'turnover' in df_hist.columns:
                avg_val = df_hist['turnover'].tail(20).mean()
            elif 'value' in df_hist.columns:
                avg_val = df_hist['value'].tail(20).mean()
            else:
                avg_val = (df_hist['close'] * df_hist['volume']).tail(20).mean()
                
            if avg_val < 2e9:
                continue
                
            f = Finance(symbol=ticker, source='VCI')
            df_ratio = f.ratio(period='year')
            if df_ratio is None or df_ratio.empty:
                continue
                
            market_cap = 0
            if 'marketCap' in df_ratio.columns:
                market_cap = df_ratio['marketCap'].iloc[0]
            elif 'market_cap' in df_ratio.columns:
                market_cap = df_ratio['market_cap'].iloc[0]
            else:
                market_cap = 600 * 1e9 
                
            if market_cap < 500: 
                if market_cap > 1000000000: 
                    pass
                else:
                    continue
                    
            valid_tickers.append(ticker)
        except Exception:
            continue
            
    return valid_tickers

def calculate_engine(ticker, tax_rate_fallback=0.2):
    try:
        f = Finance(symbol=ticker, source='VCI')
        
        df_cf = f.cash_flow(period='year')
        df_is = f.income_statement(period='year')
        df_bs = f.balance_sheet(period='year')
        
        if df_cf is None or df_is is None or df_bs is None:
            return None
            
        years_cols = [c for c in df_is.columns if str(c).startswith('20')]
        if len(years_cols) < 5:
            return None
            
        roic_list = []
        de_list = []
        total_cfo_5y = 0
        total_ni_5y = 0
        
        net_income_current = get_row_value(df_is, ["Lợi nhuận sau thuế", "Net income"], year_index=0)
        
        df_ratio = f.ratio(period='year')
        market_cap = 1
        if not df_ratio.empty:
            if 'marketCap' in df_ratio.columns:
                market_cap = df_ratio['marketCap'].iloc[0]
            elif 'market_cap' in df_ratio.columns:
                market_cap = df_ratio['market_cap'].iloc[0]
                
        if market_cap < 1000000: 
            market_cap = market_cap * 1e9

        for i in range(5):
            ebt = get_row_value(df_is, ["Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"], year_index=i)
            tax = get_row_value(df_is, ["Chi phí thuế thu nhập doanh nghiệp", "Income tax expense"], year_index=i)
            ni = get_row_value(df_is, ["Lợi nhuận sau thuế", "Net income"], year_index=i)
            ebit = get_row_value(df_is, ["Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"], year_index=i)
            if ebit == 0:
                ebit = ebt 
            
            if ebt > 0:
                tax_rate = tax / ebt
                tax_rate = max(0.0, min(0.22, tax_rate))
            else:
                tax_rate = tax_rate_fallback
                
            equity = get_row_value(df_bs, ["Vốn chủ sở hữu", "Equity"], year_index=i)
            debt = get_row_value(df_bs, ["Nợ phải trả", "Liabilities", "Tổng nợ"], year_index=i)
            cash = get_row_value(df_bs, ["Tiền và các khoản tương đương tiền", "Cash and cash equivalents"], year_index=i)
            
            cfo = get_row_value(df_cf, ["Lưu chuyển tiền thuần từ hoạt động kinh doanh", "Net cash flows from operating activities"], year_index=i)
            
            invested_capital = equity + debt - cash
            if invested_capital > 0:
                roic = (ebit * (1 - tax_rate)) / invested_capital
            else:
                roic = 0
            roic_list.append(roic)
            
            if equity > 0:
                de_list.append(debt / equity)
            else:
                de_list.append(0)
                
            total_cfo_5y += cfo
            total_ni_5y += ni
            
        avg_roic_5y = np.mean(roic_list)
        avg_de_5y = np.mean(de_list)
        
        cfo_quality = total_cfo_5y / total_ni_5y if total_ni_5y != 0 else 0
        
        ep_ratio = net_income_current / market_cap if market_cap > 0 else 0
        value_ratio = ep_ratio / avg_roic_5y if avg_roic_5y > 0 else 0
        
        return {
            'Ticker': ticker,
            'ROIC_5Y': avg_roic_5y,
            'Value_Ratio': value_ratio,
            'CFO_Quality': cfo_quality,
            'DE_5Y': avg_de_5y
        }
        
    except Exception:
        return None

def run_screener_for_sector(sector):
    tickers = get_tickers_by_sector(sector)
    if not tickers:
        return []
        
    valid_tickers = filter_hard_criteria(tickers)
    
    results = []
    for ticker in valid_tickers:
        res = calculate_engine(ticker)
        if res:
            results.append(res)
            
    df = pd.DataFrame(results)
    if df.empty:
        return []
        
    # SCORING
    df['Score_ROIC'] = df['ROIC_5Y'].rank(pct=True) * 100
    df['Score_Value'] = df['Value_Ratio'].rank(pct=True) * 100
    df['Score_CFO'] = df['CFO_Quality'].rank(pct=True) * 100
    df.loc[df['CFO_Quality'] < 0, 'Score_CFO'] = 0
    df['Score_DE'] = df['DE_5Y'].rank(pct=True, ascending=False) * 100
    
    df['Total Score'] = (df['Score_ROIC'] * 0.4) + \
                        (df['Score_Value'] * 0.3) + \
                        (df['Score_CFO'] * 0.2) + \
                        (df['Score_DE'] * 0.1)
                        
    df = df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
    
    # Fill NA and clean before returning
    df = df.fillna(0)
    
    return df.to_dict('records')

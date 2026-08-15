import pandas as pd
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

from vnstock import Listing, Finance, Vnstock, Company

def get_available_sectors():
    """ Trả về danh sách tất cả các ngành nghề trên thị trường. """
    try:
        df = Listing().symbols_by_industries()
        if df is not None and not df.empty and 'industry_name' in df.columns:
            sectors = df['industry_name'].dropna().unique().tolist()
            blacklist = ["chứng khoán", "bất động sản", "dịch vụ tài chính"]
            filtered_sectors = []
            for s in sectors:
                if not s.strip(): continue
                if not any(b in s.lower() for b in blacklist):
                    filtered_sectors.append(s)
            return sorted(filtered_sectors)
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

def get_row_value(df, keywords, year_str, default=0):
    if df is None or df.empty:
        return default
    if isinstance(keywords, str):
        keywords = [keywords]
        
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0] 
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False, regex=False)]
            if not m.empty:
                matches = m
                break
                
        if not matches.empty:
            if year_str in matches.columns:
                val = matches.iloc[0][year_str]
                if pd.notna(val):
                    try:
                        return float(val)
                    except:
                        pass
    except Exception as e:
        pass
    return default

def get_ttm_value(df, keywords, default=0):
    if df is None or df.empty: return default
    if isinstance(keywords, str): keywords = [keywords]
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0]
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False, regex=False)]
            if not m.empty:
                matches = m
                break
        if not matches.empty:
            q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
            q_cols.sort(reverse=True)
            if not q_cols: return default
            q_cols = q_cols[:4]
            total = 0
            for q in q_cols:
                val = matches.iloc[0][q]
                if pd.notna(val):
                    try: total += float(val)
                    except: pass
            return total
    except: pass
    return default

def get_latest_q_value(df, keywords, default=0):
    if df is None or df.empty: return default
    if isinstance(keywords, str): keywords = [keywords]
    try:
        matches = pd.DataFrame()
        item_col = df.columns[0]
        for kw in keywords:
            m = df[df[item_col].astype(str).str.contains(kw, case=False, na=False, regex=False)]
            if not m.empty:
                matches = m
                break
        if not matches.empty:
            q_cols = [c for c in df.columns if '-Q' in str(c) and len(str(c)) == 7]
            q_cols.sort(reverse=True)
            if not q_cols: return default
            val = matches.iloc[0][q_cols[0]]
            if pd.notna(val):
                try: return float(val)
                except: pass
    except: pass
    return default

def get_top_market_cap(tickers, limit=10):
    """ Lấy danh sách Top 10 mã (ưu tiên vốn hóa lớn nhất) bằng cách đối chiếu với VN100. Tốc độ ánh sáng, không gọi API tài chính. """
    try:
        vn100_df = Listing().symbols_by_group('VN100')
        if vn100_df is not None and not vn100_df.empty:
            vn100_symbols = vn100_df['symbol'].tolist()
            # Lọc các mã trong ngành có mặt trong rổ VN100 (những công ty đầu ngành)
            top_tickers = [t for t in tickers if t in vn100_symbols]
            
            # Nếu ngành nhỏ không đủ 10 mã trong VN100, lấy thêm các mã ngoài cho đủ limit
            for t in tickers:
                if t not in top_tickers:
                    top_tickers.append(t)
                if len(top_tickers) >= limit:
                    break
                    
            return top_tickers[:limit]
    except Exception as e:
        print("Lỗi khi đối chiếu VN100:", e)
        
    return tickers[:limit]

def calculate_engine_bank(ticker):
    try:
        f = Finance(symbol=ticker, source='KBS')
        df_ratio = f.ratio(period='year')
        df_bs = f.balance_sheet(period='year')
        
        try:
            df_ratio_q = Finance(symbol=ticker, source='VCI').ratio(period='quarter')
            df_bs_q = f.balance_sheet(period='quarter')
        except:
            df_ratio_q, df_bs_q = None, None
        
        if df_ratio is None or df_ratio.empty:
            return None
            
        years_cols = [c for c in df_ratio.columns if str(c).startswith('20') and '-Năm' in str(c)]
        if not years_cols:
            years_cols = [c for c in df_ratio.columns if str(c).startswith('20')]
            if not years_cols:
                return None
        
        years_cols = sorted(years_cols, reverse=True)
        latest_year_str = years_cols[0]
        
        import re
        match = re.search(r'\d{4}', str(latest_year_str))
        if not match:
            return None
            
        latest_year = int(match.group(0))
        current_year = pd.Timestamp.now().year
        if latest_year < current_year - 2:
            return None
            
        npl = get_latest_q_value(df_ratio_q, ["nợ xấu", "NPL", "tỷ lệ nợ xấu"])
        if npl == 0: npl = get_row_value(df_ratio, ["nợ xấu", "NPL", "tỷ lệ nợ xấu"], latest_year_str)
        if npl == 0 and df_bs_q is not None: npl = get_latest_q_value(df_bs_q, ["nợ xấu", "NPL", "tỷ lệ nợ xấu"])
        if npl == 0 and df_bs is not None: npl = get_row_value(df_bs, ["nợ xấu", "NPL", "tỷ lệ nợ xấu"], latest_year_str)
             
        nim = get_latest_q_value(df_ratio_q, ["NIM", "lãi thuần", "thu nhập lãi thuần"])
        if nim == 0: nim = get_row_value(df_ratio, ["NIM", "lãi thuần", "thu nhập lãi thuần"], latest_year_str)
        if nim and abs(nim) > 0.5: nim = nim / 100
            
        llr = get_latest_q_value(df_ratio_q, ["Bao phủ", "LLR", "dự phòng bao nợ xấu"])
        if llr == 0: llr = get_row_value(df_ratio, ["Bao phủ", "LLR", "dự phòng bao nợ xấu"], latest_year_str)
        if llr: llr = abs(llr)
            
        pb = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
        if pb == 0: pb = get_row_value(df_ratio, ["P/B", "giá trị sổ sách (P/B)"], latest_year_str)
        
        casa = get_latest_q_value(df_ratio_q, ["CASA", "không kỳ hạn"])
        if casa == 0: casa = get_row_value(df_ratio, ["CASA", "không kỳ hạn"], latest_year_str)
        if casa == 0 and df_bs_q is not None: casa = get_latest_q_value(df_bs_q, ["CASA", "không kỳ hạn"])
        if casa == 0 and df_bs is not None: casa = get_row_value(df_bs, ["CASA", "không kỳ hạn"], latest_year_str)
            
        return {
            'Ticker': ticker,
            'CASA': float(casa) if casa else 0.0,
            'NIM': float(nim) if nim else 0.0,
            'LLR': float(llr) if llr else 0.0,
            'NPL': float(npl) if npl else 0.0,
            'PB': float(pb) if pb else 0.0
        }
    except Exception as e:
        return None

def calculate_engine(ticker, tax_rate_fallback=0.2):
    try:
        f = Finance(symbol=ticker, source='VCI')
        
        df_cf = f.cash_flow(period='year')
        df_is = f.income_statement(period='year')
        df_bs = f.balance_sheet(period='year')
        
        if df_cf is None or df_is is None or df_bs is None:
            return None
            
        years_cols = [c for c in df_is.columns if str(c).startswith('20')]
        years_cols = sorted(years_cols, reverse=True)
        if len(years_cols) < 3:
            return None
            
        import re
        latest_year_str = years_cols[0]
        match = re.search(r'\d{4}', str(latest_year_str))
        if not match:
            return None
            
        latest_year = int(match.group(0))
        current_year = pd.Timestamp.now().year
        
        # Chống lỗi lấy data quá cũ (ví dụ data từ 2018)
        if latest_year < current_year - 2:
            return None
            
        roic_list = []
        de_list = []
        total_cfo_5y = 0
        total_ni_5y = 0
        
        net_income_current = get_row_value(df_is, ["Lợi nhuận sau thuế", "Net income"], year_str=str(latest_year))
        
        df_ratio = f.ratio(period='year')
        market_cap = 1
        if not df_ratio.empty:
            if 'marketCap' in df_ratio.columns:
                market_cap = df_ratio['marketCap'].iloc[0]
            elif 'market_cap' in df_ratio.columns:
                market_cap = df_ratio['market_cap'].iloc[0]
                
        if market_cap < 1000000: 
            market_cap = market_cap * 1e9

        num_years = min(len(years_cols), 5)
        for i in range(num_years):
            target_year_str = str(latest_year - i)
            ebt = get_row_value(df_is, ["Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"], year_str=target_year_str)
            tax = get_row_value(df_is, ["thuế thu nhập doanh nghiệp", "Income tax expense"], year_str=target_year_str)
            ni = get_row_value(df_is, ["Lợi nhuận sau thuế", "Net income"], year_str=target_year_str)
            ebit = get_row_value(df_is, ["Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"], year_str=target_year_str)
            if ebit == 0:
                ebit = ebt 
            
            if ebt > 0:
                tax_rate = tax / ebt
                tax_rate = max(0.0, min(0.22, tax_rate))
            else:
                tax_rate = tax_rate_fallback
                
            equity = get_row_value(df_bs, ["Vốn chủ sở hữu", "Equity"], year_str=target_year_str)
            debt = get_row_value(df_bs, ["Nợ phải trả", "Liabilities", "Tổng nợ"], year_str=target_year_str)
            cash = get_row_value(df_bs, ["Tiền và các khoản tương đương tiền", "Cash and cash equivalents"], year_str=target_year_str)
            
            cfo = get_row_value(df_cf, ["Lưu chuyển tiền thuần từ hoạt động kinh doanh", "Net cash flows from operating activities"], year_str=target_year_str)
            
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
        
        try:
            df_cf_q = f.cash_flow(period='quarter')
            df_is_q = f.income_statement(period='quarter')
            df_bs_q = f.balance_sheet(period='quarter')
        except:
            df_cf_q, df_is_q, df_bs_q = None, None, None

        roic_ttm = 0
        cfo_quality_ttm = 0
        de_current = 0
        
        if df_is_q is not None and not df_is_q.empty and df_bs_q is not None and not df_bs_q.empty:
            ebt_ttm = get_ttm_value(df_is_q, ["Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"])
            tax_ttm = get_ttm_value(df_is_q, ["thuế thu nhập doanh nghiệp", "Income tax expense"])
            ni_ttm = get_ttm_value(df_is_q, ["Lợi nhuận sau thuế", "Net income"])
            ebit_ttm = get_ttm_value(df_is_q, ["Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"])
            if ebit_ttm == 0: ebit_ttm = ebt_ttm
            
            cfo_ttm = get_ttm_value(df_cf_q, ["Lưu chuyển tiền thuần từ hoạt động kinh doanh", "Net cash flows from operating activities"]) if df_cf_q is not None else 0
            
            tax_rate_ttm = tax_ttm / ebt_ttm if ebt_ttm > 0 else tax_rate_fallback
            tax_rate_ttm = max(0.0, min(0.22, tax_rate_ttm))
            
            equity_q = get_latest_q_value(df_bs_q, ["Vốn chủ sở hữu", "Equity"])
            debt_q = get_latest_q_value(df_bs_q, ["Nợ phải trả", "Liabilities", "Tổng nợ"])
            cash_q = get_latest_q_value(df_bs_q, ["Tiền và các khoản tương đương tiền", "Cash and cash equivalents"])
            
            invested_capital_q = equity_q + debt_q - cash_q
            if invested_capital_q > 0:
                roic_ttm = (ebit_ttm * (1 - tax_rate_ttm)) / invested_capital_q
                
            if equity_q > 0:
                de_current = debt_q / equity_q
                
            if ni_ttm != 0:
                cfo_quality_ttm = cfo_ttm / ni_ttm

        return {
            'Ticker': ticker,
            'ROIC_5Y': avg_roic_5y,
            'Value_Ratio': value_ratio,
            'CFO_Quality': cfo_quality,
            'DE_5Y': avg_de_5y,
            'ROIC_TTM': roic_ttm,
            'CFO_Quality_TTM': cfo_quality_ttm,
            'DE_Current': de_current
        }
        
    except Exception:
        return None

def run_screener_for_sector(sector):
    tickers = get_tickers_by_sector(sector)
    if not tickers:
        return []
        
    top_tickers = get_top_market_cap(tickers, limit=10)
    
    results = []
    
    if sector.lower() in ['ngân hàng', 'banks']:
        for ticker in top_tickers:
            res = calculate_engine_bank(ticker)
            if res:
                results.append(res)
                
        df = pd.DataFrame(results)
        if df.empty:
            return []
            
        df['Score_CASA'] = df['CASA'].rank(pct=True) * 20
        df['Score_NIM'] = df['NIM'].rank(pct=True) * 20
        df['Score_LLR'] = df['LLR'].rank(pct=True) * 15
        df['Score_NPL'] = df['NPL'].rank(pct=True, ascending=False) * 25
        df['Score_PB'] = df['PB'].rank(pct=True, ascending=False) * 20
        
        df['Total Score'] = df['Score_CASA'] + df['Score_NIM'] + df['Score_LLR'] + df['Score_NPL'] + df['Score_PB']
        df = df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
        df = df.fillna(0)
        return df.to_dict('records')
    else:
        for ticker in top_tickers:
            res = calculate_engine(ticker)
            if res:
                results.append(res)
                
        df = pd.DataFrame(results)
        if df.empty:
            return []
            
        # SCORING
        df['Score_ROIC'] = df['ROIC_5Y'].rank(pct=True) * 100
        df['Score_ROIC_TTM'] = df['ROIC_TTM'].rank(pct=True) * 100
        df['Score_Value'] = df['Value_Ratio'].rank(pct=True) * 100
        
        df['Score_CFO'] = df['CFO_Quality'].rank(pct=True) * 100
        df.loc[df['CFO_Quality'] < 0, 'Score_CFO'] = 0
        df['Score_CFO_TTM'] = df['CFO_Quality_TTM'].rank(pct=True) * 100
        df.loc[df['CFO_Quality_TTM'] < 0, 'Score_CFO_TTM'] = 0
        
        df['Score_DE'] = df['DE_5Y'].rank(pct=True, ascending=False) * 100
        df['Score_DE_Current'] = df['DE_Current'].rank(pct=True, ascending=False) * 100
        
        df['Total Score'] = (df['Score_ROIC'] * 0.15) + (df['Score_ROIC_TTM'] * 0.25) + \
                            (df['Score_Value'] * 0.20) + \
                            (df['Score_CFO'] * 0.10) + (df['Score_CFO_TTM'] * 0.15) + \
                            (df['Score_DE'] * 0.05) + (df['Score_DE_Current'] * 0.10)
                            
        df = df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
        
        # Fill NA and clean before returning
        df = df.fillna(0)
        
        return df.to_dict('records')

def get_stock_report(ticker, tax_rate_fallback=0.2):
    try:
        try:
            overview_df = Company(symbol=ticker, source='VCI').overview()
            if not overview_df.empty:
                company_name = overview_df.iloc[0].get('organ_name', ticker)
                sector = overview_df.iloc[0].get('sector', '')
            else:
                company_name = ticker
                sector = ""
        except:
            company_name = ticker
            sector = ""
            
        if sector.lower() in ['ngân hàng', 'banks']:
            f = Finance(symbol=ticker, source='KBS')
            df_ratio = f.ratio(period='year')
            df_bs = f.balance_sheet(period='year')
            
            if df_ratio is None or df_ratio.empty:
                return None
                
            years_cols = [c for c in df_ratio.columns if str(c).startswith('20') and '-Năm' in str(c)]
            if not years_cols:
                years_cols = [c for c in df_ratio.columns if str(c).startswith('20')]
                if not years_cols: return None
                
            years_cols = sorted(years_cols, reverse=True)
            latest_year_str = years_cols[0]
            
            import re
            match = re.search(r'\d{4}', str(latest_year_str))
            if not match: return None
            latest_year = int(match.group(0))
            
            history = []
            num_years = min(len(years_cols), 5)
            
            try:
                f_vci = Finance(symbol=ticker, source='VCI')
                df_vci = f_vci.ratio(period='year')
            except:
                df_vci = None
                
            for i in range(num_years):
                target_year_str = str(latest_year - i)
                ratio_year_str = f"{target_year_str}-Năm" if f"{target_year_str}-Năm" in df_ratio.columns else target_year_str
                bs_year_str = target_year_str
                
                nim = get_row_value(df_ratio, ["NIM", "lãi thuần", "thu nhập lãi thuần"], ratio_year_str)
                if nim and abs(nim) > 0.5: nim = nim / 100
                    
                llr = get_row_value(df_ratio, ["Bao phủ", "LLR", "dự phòng bao nợ xấu"], ratio_year_str)
                if llr: llr = abs(llr)
                    
                pb = get_row_value(df_ratio, ["P/B", "giá trị sổ sách (P/B)"], ratio_year_str)
                
                casa = 0.0
                npl = 0.0
                
                if df_vci is not None and not df_vci.empty and df_vci.shape[1] > 3 + i:
                    try:
                        c_match = df_vci[df_vci.iloc[:,0].astype(str).str.contains('CASA', case=False, na=False)]
                        if not c_match.empty:
                            casa = float(c_match.iloc[0, 3+i])
                            
                        n_match = df_vci[df_vci.iloc[:,0].astype(str).str.contains('Nợ xấu', case=False, na=False)]
                        if not n_match.empty:
                            npl = float(n_match.iloc[0, 3+i])
                            
                        l_match = df_vci[df_vci.iloc[:,0].astype(str).str.contains('DP rủi ro/Nợ xấu', case=False, na=False)]
                        if not l_match.empty:
                            l_val = float(l_match.iloc[0, 3+i])
                            if l_val:
                                llr = abs(l_val)
                    except:
                        pass
                
                history.append({
                    'year': target_year_str,
                    'casa': casa,
                    'nim': float(nim) if nim else 0.0,
                    'llr': float(llr) if llr else 0.0,
                    'npl': npl,
                    'pb': float(pb) if pb else 0.0
                })
            
            history.reverse()
            
            try:
                df_ratio_q = Finance(symbol=ticker, source='VCI').ratio(period='quarter')
                df_bs_q = f.balance_sheet(period='quarter')
            except:
                df_ratio_q, df_bs_q = None, None
                
            npl_q = get_latest_q_value(df_ratio_q, ["nợ xấu", "NPL", "tỷ lệ nợ xấu"])
            if npl_q == 0: npl_q = history[-1]['npl'] if history else 0
            
            nim_q = get_latest_q_value(df_ratio_q, ["NIM", "lãi thuần", "thu nhập lãi thuần"])
            if nim_q == 0: nim_q = history[-1]['nim'] if history else 0
            if nim_q and abs(nim_q) > 0.5: nim_q = nim_q / 100
                
            llr_q = get_latest_q_value(df_ratio_q, ["Bao phủ", "LLR", "dự phòng bao nợ xấu"]) # removed "Dự phòng rủi ro tín dụng/Tổng dư nợ" because it fetches provision expense, not NPL coverage
            if llr_q == 0: llr_q = history[-1]['llr'] if history else 0
            else:
                llr_q = abs(llr_q)
                
            pb_q = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
            if pb_q == 0: pb_q = history[-1]['pb'] if history else 0
            
            casa_q = get_latest_q_value(df_ratio_q, ["CASA", "không kỳ hạn"])
            if casa_q == 0 and df_bs_q is not None: casa_q = get_latest_q_value(df_bs_q, ["CASA", "không kỳ hạn"])
            if casa_q == 0: casa_q = history[-1]['casa'] if history else 0

            return {
                'ticker': ticker,
                'company_name': company_name,
                'sector': 'Ngân hàng',
                'summary': {
                    'CASA_Current': float(casa_q) if casa_q else 0,
                    'NIM_Current': float(nim_q) if nim_q else 0,
                    'LLR_Current': float(llr_q) if llr_q else 0,
                    'NPL_Current': float(npl_q) if npl_q else 0,
                    'PB_Current': float(pb_q) if pb_q else 0
                },
                'history': history
            }
            
        f = Finance(symbol=ticker, source='VCI')
        
        df_cf = f.cash_flow(period='year')
        df_is = f.income_statement(period='year')
        df_bs = f.balance_sheet(period='year')
        
        if df_cf is None or df_is is None or df_bs is None:
            return None
            
        years_cols = [c for c in df_is.columns if str(c).startswith('20')]
        years_cols = sorted(years_cols, reverse=True)
        if len(years_cols) == 0:
            return None
            
        import re
        latest_year_str = years_cols[0]
        match = re.search(r'\d{4}', str(latest_year_str))
        if not match:
            return None
            
        latest_year = int(match.group(0))
        
        try:
            f_ratio = Finance(symbol=ticker, source='KBS')
            df_ratio = f_ratio.ratio(period='year')
        except:
            df_ratio = pd.DataFrame()
            
        num_years = min(len(years_cols), 5)
        
        history = []
        
        for i in range(num_years):
            target_year_str = str(latest_year - i)
            ebt = get_row_value(df_is, ["Lãi/(lỗ) trước thuế", "Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"], year_str=target_year_str)
            tax = get_row_value(df_is, ["thuế thu nhập doanh nghiệp", "Income tax expense"], year_str=target_year_str)
            ni = get_row_value(df_is, ["Lãi/(lỗ) thuần sau thuế", "Lợi nhuận của Cổ đông của Công ty mẹ", "Lợi nhuận sau thuế", "Net income"], year_str=target_year_str)
            ebit = get_row_value(df_is, ["Lãi/(lỗ) từ hoạt động kinh doanh", "Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"], year_str=target_year_str)
            if ebit == 0:
                ebit = ebt 
            
            if ebt > 0:
                tax_rate = tax / ebt
                tax_rate = max(0.0, min(0.22, tax_rate))
            else:
                tax_rate = tax_rate_fallback
                
            equity = get_row_value(df_bs, ["Vốn chủ sở hữu", "Equity"], year_str=target_year_str)
            debt = get_row_value(df_bs, ["Nợ phải trả", "Liabilities", "Tổng nợ"], year_str=target_year_str)
            cash = get_row_value(df_bs, ["Tiền và tương đương tiền", "Tiền và các khoản tương đương tiền", "Cash and cash equivalents"], year_str=target_year_str)
            
            cfo = get_row_value(df_cf, ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh", "Lưu chuyển tiền thuần từ hoạt động kinh doanh", "Net cash flows from operating activities"], year_str=target_year_str)
            
            invested_capital = equity + debt - cash
            roic = (ebit * (1 - tax_rate)) / invested_capital if invested_capital > 0 else 0
            de = debt / equity if equity > 0 else 0
            
            # Tính B/P
            ratio_year_str = f"{target_year_str}-Năm"
            pb = get_row_value(df_ratio, ["P/B", "Chỉ số giá thị trường trên giá trị sổ sách (P/B)"], year_str=ratio_year_str)
            bp = 1 / pb if pb > 0 else 0
            
            # Tính ICR
            icr = get_row_value(df_ratio, ["Khả năng thanh toán lãi vay", "ICR"], year_str=ratio_year_str)
                
            history.append({
                'year': target_year_str,
                'roic': roic,
                'de': de,
                'cfo': cfo,
                'ni': ni,
                'bp': bp,
                'icr': icr
            })
            
        # Reverse history so it is chronological (oldest to newest)
        history.reverse()
        
        # Calculate averages for summary
        roic_list = [h['roic'] for h in history]
        de_list = [h['de'] for h in history]
        total_cfo = sum(h['cfo'] for h in history)
        total_ni = sum(h['ni'] for h in history)
        
        avg_roic_5y = np.mean(roic_list) if roic_list else 0
        avg_de_5y = np.mean(de_list) if de_list else 0
        cfo_quality = total_cfo / total_ni if total_ni != 0 else 0
        
        net_income_current = history[-1]['ni'] if history else 0
        
        bp_list = [h['bp'] for h in history if h['bp'] > 0]
        avg_bp = np.mean(bp_list) if bp_list else 0
        value_ratio = avg_bp / avg_roic_5y if avg_roic_5y > 0 else 0
        
        ed_list = [1 / h['de'] if h['de'] > 0 else 1000 for h in history]
        avg_ed_5y = np.mean(ed_list) if ed_list else 0
        
        current_icr = history[-1]['icr'] if history else 0

        try:
            df_cf_q = f.cash_flow(period='quarter')
            df_is_q = f.income_statement(period='quarter')
            df_bs_q = f.balance_sheet(period='quarter')
        except:
            df_cf_q, df_is_q, df_bs_q = None, None, None

        roic_ttm = 0
        cfo_quality_ttm = 0
        de_current = 0
        if df_is_q is not None and not df_is_q.empty and df_bs_q is not None and not df_bs_q.empty:
            ebt_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) trước thuế", "Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"])
            tax_ttm = get_ttm_value(df_is_q, ["thuế thu nhập doanh nghiệp", "Income tax expense"])
            ni_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) thuần sau thuế", "Lợi nhuận của Cổ đông của Công ty mẹ", "Lợi nhuận sau thuế", "Net income"])
            ebit_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) từ hoạt động kinh doanh", "Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"])
            if ebit_ttm == 0: ebit_ttm = ebt_ttm
            cfo_ttm = get_ttm_value(df_cf_q, ["Lưu chuyển tiền tệ ròng từ các hoạt động sản xuất kinh doanh", "Lưu chuyển tiền thuần từ hoạt động kinh doanh", "Net cash flows from operating activities"]) if df_cf_q is not None else 0
            tax_rate_ttm = tax_ttm / ebt_ttm if ebt_ttm > 0 else tax_rate_fallback
            tax_rate_ttm = max(0.0, min(0.22, tax_rate_ttm))
            equity_q = get_latest_q_value(df_bs_q, ["Vốn chủ sở hữu", "Equity"])
            debt_q = get_latest_q_value(df_bs_q, ["Nợ phải trả", "Liabilities", "Tổng nợ"])
            cash_q = get_latest_q_value(df_bs_q, ["Tiền và tương đương tiền", "Tiền và các khoản tương đương tiền", "Cash and cash equivalents"])
            invested_capital_q = equity_q + debt_q - cash_q
            if invested_capital_q > 0: roic_ttm = (ebit_ttm * (1 - tax_rate_ttm)) / invested_capital_q
            if equity_q > 0: de_current = debt_q / equity_q
            if ni_ttm != 0: cfo_quality_ttm = cfo_ttm / ni_ttm

        return {
            'ticker': ticker,
            'company_name': company_name,
            'sector': sector,
            'summary': {
                'ROIC_5Y': avg_roic_5y,
                'Value_Ratio': value_ratio,
                'BP_5Y': avg_bp,
                'ED_5Y': avg_ed_5y,
                'CFO_Quality': cfo_quality,
                'DE_5Y': avg_de_5y,
                'ICR_Current': current_icr,
                'ROIC_TTM': roic_ttm,
                'CFO_Quality_TTM': cfo_quality_ttm,
                'DE_Current': de_current
            },
            'history': history
        }
    except Exception as e:
        try:
            print(f"Loi khi lay du lieu cho {ticker}: {str(e)[:50]}...")
        except:
            pass
        return None

def get_comparative_report(main_ticker, peers_str="", tax_rate_fallback=0.2):
    import re
    tickers = [main_ticker]
    if peers_str:
        peer_list = [p.strip().upper() for p in re.split(r'[,\s]+', peers_str) if p.strip()]
        for p in peer_list:
            if p not in tickers:
                tickers.append(p)
                
    reports = {}
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_ticker = {executor.submit(get_stock_report, t, tax_rate_fallback): t for t in tickers}
        for future in concurrent.futures.as_completed(future_to_ticker):
            t = future_to_ticker[future]
            try:
                rep = future.result()
                if rep:
                    reports[t] = rep
            except Exception as exc:
                print(f"Lỗi khi lấy {t} song song: {exc}")
            
    if main_ticker not in reports:
        return {'status': 'error', 'detail': f'Không tìm thấy dữ liệu cho mã chính {main_ticker}'}
        
    rank_data = []
    is_bank = False
    for t, rep in reports.items():
        summary = rep['summary']
        if rep['sector'].lower() in ['ngân hàng', 'banks']:
            is_bank = True
            rank_data.append({
                'ticker': t,
                'CASA_Current': summary.get('CASA_Current', 0),
                'NIM_Current': summary.get('NIM_Current', 0),
                'LLR_Current': summary.get('LLR_Current', 0),
                'NPL_Current': summary.get('NPL_Current', 0),
                'PB_Current': summary.get('PB_Current', 0)
            })
        else:
            rank_data.append({
                'ticker': t,
                'ROIC_5Y': summary.get('ROIC_5Y', 0),
                'ROIC_TTM': summary.get('ROIC_TTM', 0),
                'BP_5Y': summary.get('BP_5Y', 0),
                'CFO_Quality': summary.get('CFO_Quality', 0),
                'CFO_Quality_TTM': summary.get('CFO_Quality_TTM', 0),
                'ED_5Y': summary.get('ED_5Y', 0),
                'DE_Current': summary.get('DE_Current', 0),
                'ICR_Current': summary.get('ICR_Current', 0)
            })
    
    df_rank = pd.DataFrame(rank_data)
    if not df_rank.empty:
        if is_bank:
            df_rank['Score_CASA'] = df_rank['CASA_Current'].rank(pct=True) * 20
            df_rank['Score_NIM'] = df_rank['NIM_Current'].rank(pct=True) * 20
            df_rank['Score_LLR'] = df_rank['LLR_Current'].rank(pct=True) * 15
            df_rank['Score_NPL'] = df_rank['NPL_Current'].rank(pct=True, ascending=False) * 25
            df_rank['Score_PB'] = df_rank['PB_Current'].rank(pct=True, ascending=False) * 20
            df_rank['Total_Score'] = df_rank['Score_CASA'] + df_rank['Score_NIM'] + df_rank['Score_LLR'] + df_rank['Score_NPL'] + df_rank['Score_PB']
        else:
            df_rank['Score_ROIC'] = df_rank['ROIC_5Y'].rank(pct=True) * 15
            df_rank['Score_ROIC_TTM'] = df_rank['ROIC_TTM'].rank(pct=True) * 25
            df_rank['Score_BP'] = df_rank['BP_5Y'].rank(pct=True) * 20
            df_rank['Score_CFO'] = df_rank['CFO_Quality'].rank(pct=True) * 10
            df_rank['Score_CFO_TTM'] = df_rank['CFO_Quality_TTM'].rank(pct=True) * 15
            df_rank['Score_DE'] = df_rank['ED_5Y'].rank(pct=True) * 5
            df_rank['Score_DE_Current'] = df_rank['DE_Current'].rank(pct=True, ascending=False) * 10
            df_rank['Score_ICR'] = df_rank['ICR_Current'].rank(pct=True) * 5
            df_rank['Total_Score'] = df_rank['Score_ROIC'] + df_rank['Score_ROIC_TTM'] + df_rank['Score_BP'] + df_rank['Score_CFO'] + df_rank['Score_CFO_TTM'] + df_rank['Score_DE'] + df_rank['Score_DE_Current'] + df_rank['Score_ICR']
        
        df_rank = df_rank.fillna(0)
        df_rank = df_rank.sort_values(by='Total_Score', ascending=False)
        ranking = df_rank.to_dict('records')
    else:
        ranking = []
        
    result_dict = {
        'status': 'success',
        'main_ticker': main_ticker,
        'reports': reports,
        'ranking': ranking
    }
    
    import math
    def sanitize(obj):
        import math
        import pandas as pd
        import numpy as np
        
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
            
        if isinstance(obj, bool):
            return obj
            
        try:
            if pd.isna(obj):
                return 0
        except Exception:
            pass
            
        try:
            if isinstance(obj, (float, np.floating)):
                if np.isinf(obj) or np.isnan(obj):
                    return 0
                return float(obj)
            elif isinstance(obj, (int, np.integer)):
                return int(obj)
        except Exception:
            pass
            
        return obj
        
    return sanitize(result_dict)

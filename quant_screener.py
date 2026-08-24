import pandas as pd
import numpy as np
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

import os
os.environ["CODESPACE_NAME"] = "render_bypass" # Fix bug hosting_service của vnstock trên server Render
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
                for i in range(len(matches)):
                    val = matches.iloc[i][year_str]
                    if pd.notna(val) and str(val).strip() != '':
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
            
            for i in range(len(matches)):
                valid_start_idx = -1
                for idx, q in enumerate(q_cols):
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        valid_start_idx = idx
                        break
                
                if valid_start_idx != -1:
                    total = 0
                    valid_count = 0
                    for q in q_cols[valid_start_idx : valid_start_idx + 4]:
                        val = matches.iloc[i][q]
                        if pd.notna(val) and str(val).strip() != '':
                            try:
                                total += float(val)
                                valid_count += 1
                            except: pass
                    if valid_count > 0:
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
            for i in range(len(matches)):
                for q in q_cols:
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        try: return float(val)
                        except: pass
    except: pass
    return default

def get_latest_quarter_str(df, keywords):
    if df is None or df.empty: return ""
    if isinstance(keywords, str): keywords = [keywords]
    import pandas as pd
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
            if not q_cols: return ""
            for q in q_cols:
                for i in range(len(matches)):
                    val = matches.iloc[i][q]
                    if pd.notna(val) and str(val).strip() != '':
                        return q
    except: pass
    return ""

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
        
        try:
            df_ratio_q = f.ratio(period='quarter')
        except:
            df_ratio_q = None
        
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
            
        roa = get_latest_q_value(df_ratio_q, ["ROA bình quân 4 quý", "roa_trailling", "ROAA", "ROA", "sinh lợi trên tổng tài sản"])
        if roa == 0: roa = get_row_value(df_ratio, ["ROAA", "ROA", "sinh lợi trên tổng tài sản"], latest_year_str)
        if roa and abs(roa) < 100: roa = roa / 100
             
        roe = get_latest_q_value(df_ratio_q, ["ROE bình quân 4 quý", "roe_trailling", "ROEA", "ROE", "lợi nhuận trên vốn chủ sở hữu"])
        if roe == 0: roe = get_row_value(df_ratio, ["ROEA", "ROE", "lợi nhuận trên vốn chủ sở hữu"], latest_year_str)
        if roe and abs(roe) > 1 and abs(roe) < 100: roe = roe / 100
             
        nim = get_latest_q_value(df_ratio_q, ["NIM", "lãi thuần", "thu nhập lãi thuần"])
        if nim == 0: nim = get_row_value(df_ratio, ["NIM", "lãi thuần", "thu nhập lãi thuần"], latest_year_str)
        if nim and abs(nim) > 0.5 and abs(nim) < 100: nim = nim / 100
            
        try:
            overview_df = Company(symbol=ticker, source='VCI').overview()
            current_price = overview_df.iloc[0].get('current_price', 0) if not overview_df.empty else 0
        except:
            current_price = 0
            
        pb = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
        if pb == 0: pb = get_row_value(df_ratio, ["P/B", "giá trị sổ sách (P/B)"], latest_year_str)
        
        if not roa or not roe or not nim or not pb:
            return None
            
        value_ratio = roe / pb if pb > 0 else 0

        return {
            'Ticker': ticker,
            'ROA': float(roa),
            'ROE': float(roe),
            'NIM': float(nim),
            'PB': float(pb),
            'Value_Ratio': float(value_ratio),
            'Current_Price': float(current_price)
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
        
        try:
            overview_df = Company(symbol=ticker, source='VCI').overview()
            market_cap_overview = overview_df.iloc[0].get('market_cap', 0) if not overview_df.empty else 0
            current_price = overview_df.iloc[0].get('current_price', 0) if not overview_df.empty else 0
        except:
            market_cap_overview = 0
            current_price = 0
            
        market_cap = market_cap_overview * 1e9 if market_cap_overview > 0 and market_cap_overview < 1000000 else market_cap_overview

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
        value_ratio = (ep_ratio / avg_roic_5y) if avg_roic_5y != 0 else 0
        
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

        equity_q_val = get_latest_q_value(df_bs_q, ["của công ty mẹ", "Vốn chủ sở hữu", "Equity"]) if df_bs_q is not None else 0
        if equity_q_val == 0 and df_bs is not None:
            equity_q_val = get_row_value(df_bs, ["của công ty mẹ", "Vốn chủ sở hữu", "Equity"], str(latest_year))

        if market_cap_overview > 0 and equity_q_val > 0:
            mc = market_cap_overview * 1e9 if market_cap_overview < 1000000 else market_cap_overview
            pb_q = mc / equity_q_val
        else:
            return None

        if not pb_q or not avg_roic_5y or not ep_ratio:
            return None

        return {
            'summary': {
                'ROIC_5Y': avg_roic_5y,
                'Value_Ratio': value_ratio,
                'CFO_Quality_TTM': cfo_quality_ttm,
                'DE_Current': de_current,
                'ROIC_TTM': roic_ttm,
                'PB_Current': float(pb_q),
                'Current_Price': float(current_price)
            },
            'Ticker': ticker,
            'ROIC_5Y': avg_roic_5y,
            'Value_Ratio': value_ratio,
            'CFO_Quality': cfo_quality,
            'DE_5Y': avg_de_5y,
            'ROIC_TTM': roic_ttm,
            'CFO_Quality_TTM': cfo_quality_ttm,
            'DE_Current': de_current,
            'PB_Current': float(pb_q),
            'Current_Price': float(current_price)
        }
        
    except Exception:
        return None

def run_screener_for_sector(sector):
    import json
    import os
    from datetime import datetime
    
    CACHE_DIR = "cache"
    if not os.path.exists(CACHE_DIR):
        try:
            os.makedirs(CACHE_DIR)
        except:
            pass
            
    safe_sector = "".join([c if c.isalnum() else "_" for c in sector])
    today = datetime.now().strftime("%Y-%m-%d")
    screener_cache_file = os.path.join(CACHE_DIR, f"screener_{safe_sector}_{today}.json")
    medians_cache_file = os.path.join(CACHE_DIR, f"medians_{safe_sector}_{today}.json")
    
    if os.path.exists(screener_cache_file):
        try:
            with open(screener_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
            
    # Clean old caches occasionally
    try:
        for filename in os.listdir(CACHE_DIR):
            if filename.endswith(".json") and today not in filename:
                os.remove(os.path.join(CACHE_DIR, filename))
    except:
        pass

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
            
        # Tính trung vị (Median) của Top 10 Ngân hàng lớn nhất để làm quy chuẩn chung
        median_roa = df['ROA'].median()
        median_nim = df['NIM'].median()
        median_value = df['Value_Ratio'].median()
        
        # Fallback nếu trung vị lỗi hoặc bằng 0
        if pd.isna(median_roa) or median_roa == 0: median_roa = 0.02
        if pd.isna(median_nim) or median_nim == 0: median_nim = 0.035
        if pd.isna(median_value) or median_value == 0: median_value = 10.0
            
        try:
            with open(medians_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'median_roa': float(median_roa),
                    'median_nim': float(median_nim),
                    'median_value': float(median_value)
                }, f)
        except:
            pass

        df['Score_ROA'] = (df['ROA'] / median_roa) * 100
        df['Score_NIM'] = (df['NIM'] / median_nim) * 100
        df['Score_Value'] = (df['Value_Ratio'] / median_value) * 100
        
        df['Total Score'] = (df['Score_ROA'] * 0.50) + (df['Score_NIM'] * 0.15) + (df['Score_Value'] * 0.35)
        df = df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
        df = df.fillna(0)
        
        final_results = df.to_dict('records')
        try:
            df.to_json(screener_cache_file, orient='records', force_ascii=False)
        except Exception as e:
            print("CACHE ERROR:", e)
        return final_results
    else:
        for ticker in top_tickers:
            res = calculate_engine(ticker)
            if res:
                results.append(res)
                
        df = pd.DataFrame(results)
        if df.empty:
            return []
            
        # SCORING - Absolute Median Normalization
        median_roic = df['ROIC_5Y'].median()
        median_roic_ttm = df['ROIC_TTM'].median()
        median_value = df['Value_Ratio'].median()
        median_bp = df['BP_5Y'].median() if 'BP_5Y' in df.columns else 10.0
        median_cfo = df['CFO_Quality'].median()
        median_cfo_ttm = df['CFO_Quality_TTM'].median()
        median_de = df['DE_5Y'].median()
        median_de_curr = df['DE_Current'].median()
        
        if pd.isna(median_roic) or median_roic == 0: median_roic = 0.10
        if pd.isna(median_roic_ttm) or median_roic_ttm == 0: median_roic_ttm = 0.10
        if pd.isna(median_value) or median_value == 0: median_value = 10.0
        if pd.isna(median_bp) or median_bp == 0: median_bp = 10.0
        if pd.isna(median_cfo) or median_cfo == 0: median_cfo = 1.0
        if pd.isna(median_cfo_ttm) or median_cfo_ttm == 0: median_cfo_ttm = 1.0
        if pd.isna(median_de) or median_de == 0: median_de = 1.0
        if pd.isna(median_de_curr) or median_de_curr == 0: median_de_curr = 1.0
        
        try:
            with open(medians_cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'median_roic': float(median_roic),
                    'median_roic_ttm': float(median_roic_ttm),
                    'median_value': float(median_value),
                    'median_bp': float(median_bp),
                    'median_cfo': float(median_cfo),
                    'median_cfo_ttm': float(median_cfo_ttm),
                    'median_de': float(median_de),
                    'median_de_curr': float(median_de_curr)
                }, f)
        except:
            pass

        df['Score_ROIC'] = (df['ROIC_5Y'] / median_roic) * 100
        df['Score_ROIC_TTM'] = (df['ROIC_TTM'] / median_roic_ttm) * 100
        df['Score_Value'] = (df['Value_Ratio'] / median_value) * 100
        
        df['Score_CFO'] = (df['CFO_Quality'] / median_cfo) * 100
        df.loc[df['CFO_Quality'] < 0, 'Score_CFO'] = 0
        df['Score_CFO_TTM'] = (df['CFO_Quality_TTM'] / median_cfo_ttm) * 100
        df.loc[df['CFO_Quality_TTM'] < 0, 'Score_CFO_TTM'] = 0
        
        df['Score_DE'] = np.maximum(0, 2 - (df['DE_5Y'] / median_de)) * 100
        df['Score_DE_Current'] = np.maximum(0, 2 - (df['DE_Current'] / median_de_curr)) * 100
        
        df['Total Score'] = (df['Score_ROIC'] * 0.15) + (df['Score_ROIC_TTM'] * 0.25) + \
                            (df['Score_Value'] * 0.20) + \
                            (df['Score_CFO'] * 0.10) + (df['Score_CFO_TTM'] * 0.15) + \
                            (df['Score_DE'] * 0.05) + (df['Score_DE_Current'] * 0.10)
                            
        df = df.sort_values(by='Total Score', ascending=False).reset_index(drop=True)
        df = df.fillna(0)
        
        final_results = df.to_dict('records')
        try:
            df.to_json(screener_cache_file, orient='records', force_ascii=False)
        except Exception as e:
            print("CACHE ERROR:", e)
        return final_results

def get_stock_report(ticker, tax_rate_fallback=0.2):
    try:
        try:
            overview_df = Company(symbol=ticker, source='VCI').overview()
            if not overview_df.empty:
                company_name = overview_df.iloc[0].get('organ_name', ticker)
                sector = overview_df.iloc[0].get('sector', '')
                market_cap_overview = overview_df.iloc[0].get('market_cap', 0)
                current_price = overview_df.iloc[0].get('current_price', 0)
            else:
                company_name = ticker
                sector = ""
                market_cap_overview = 0
                current_price = 0
        except:
            company_name = ticker
            sector = ""
            market_cap_overview = 0
            current_price = 0
            
        if sector.lower() in ['ngân hàng', 'banks']:
            f_ratio = Finance(symbol=ticker, source='KBS')
            df_ratio = f_ratio.ratio(period='year')
            
            f_bs = Finance(symbol=ticker, source='VCI')
            df_bs = f_bs.balance_sheet(period='year')
            
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
                
            for i in range(num_years):
                target_year_str = str(latest_year - i)
                ratio_year_str = f"{target_year_str}-Năm" if f"{target_year_str}-Năm" in df_ratio.columns else target_year_str
                bs_year_str = target_year_str
                
                nim = get_row_value(df_ratio, ["NIM", "lãi thuần", "thu nhập lãi thuần"], ratio_year_str)
                if nim and abs(nim) > 0.5: nim = nim / 100
                    
                llr = get_row_value(df_ratio, ["Bao phủ", "LLR", "dự phòng bao nợ xấu"], ratio_year_str)
                if llr: llr = abs(llr)
                    
                pb = get_row_value(df_ratio, ["P/B", "giá trị sổ sách (P/B)"], ratio_year_str)
                pe = get_row_value(df_ratio, ["P/E", "Chỉ số giá thị trường trên thu nhập (P/E)"], ratio_year_str)
                ep = 1 / pe if pe and pe != 0 else 0
                roe = get_row_value(df_ratio, ["ROE", "lợi nhuận trên vốn chủ sở hữu"], ratio_year_str)
                if roe and abs(roe) < 100: roe = roe / 100
                
                roa = get_row_value(df_ratio, ["ROAA", "ROA", "sinh lợi trên tổng tài sản"], ratio_year_str)
                if roa and abs(roa) < 100: roa = roa / 100
                
                value_ratio = (roe / pb) if pb and pb > 0 and roe else 0.0

                history.append({
                    'year': target_year_str,
                    'roa': float(roa) if roa else 0.0,
                    'nim': float(nim) if nim else 0.0,
                    'pb': float(pb) if pb else 0.0,
                    'ep': float(ep) if ep else 0.0,
                    'roe': float(roe) if roe else 0.0,
                    'value_ratio': float(value_ratio)
                })
            
            history.reverse()
            
            try:
                df_ratio_q = Finance(symbol=ticker, source='KBS').ratio(period='quarter')
            except:
                df_ratio_q = None
                
            latest_q_str = ""
            if df_ratio_q is not None and not df_ratio_q.empty:
                latest_q_str = get_latest_quarter_str(df_ratio_q, ["ROE", "P/B"])
            latest_y_str = str(history[-1]['year']) if history else ""
                
            roa_q = get_latest_q_value(df_ratio_q, ["ROA bình quân 4 quý", "roa_trailling", "ROAA", "ROA", "sinh lợi trên tổng tài sản"])
            if roa_q == 0: roa_q = history[-1].get('roa', 0) if history else 0
            if roa_q and abs(roa_q) < 100: roa_q = roa_q / 100
                
            roe_q = get_latest_q_value(df_ratio_q, ["ROE bình quân 4 quý", "roe_trailling", "ROEA", "ROE", "lợi nhuận trên vốn chủ sở hữu"])
            if roe_q == 0: roe_q = history[-1].get('roe', 0) if history else 0
            if roe_q and abs(roe_q) > 1 and abs(roe_q) < 100: roe_q = roe_q / 100
            
            nim_q = get_latest_q_value(df_ratio_q, ["NIM bình quân 4 quý", "nim_trailling"])
            if nim_q == 0:
                nim_q = get_latest_q_value(df_ratio_q, ["NIM", "lãi thuần", "thu nhập lãi thuần"])
                if nim_q != 0: nim_q = nim_q * 4 # Thường niên hóa (Annualize) nếu chỉ có data của 1 quý
                
            if nim_q == 0: nim_q = history[-1].get('nim', 0) if history else 0
            if nim_q and abs(nim_q) > 0.5 and abs(nim_q) < 100: nim_q = nim_q / 100
                
            pb_q = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
            if pb_q == 0: pb_q = history[-1].get('pb', 0) if history else 0
            
            value_ratio_q = (roe_q / pb_q) if pb_q and pb_q > 0 else 0

            return {
                'ticker': ticker,
                'company_name': company_name,
                'sector': 'Ngân hàng',
                'summary': {
                    'ROA_Current': float(roa_q) if roa_q else 0,
                    'ROE_Current': float(roe_q) if roe_q else 0,
                    'NIM_Current': float(nim_q) if nim_q else 0,
                    'PB_Current': float(pb_q) if pb_q else 0,
                    'Value_Ratio_Current': float(value_ratio_q) if value_ratio_q else 0,
                    'Current_Price': float(current_price) if current_price else 0,
                    'Latest_Quarter': latest_q_str,
                    'Latest_Year': latest_y_str
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
            pe = get_row_value(df_ratio, ["P/E", "Chỉ số giá thị trường trên thu nhập (P/E)"], year_str=ratio_year_str)
            ep = 1 / pe if pe and pe != 0 else 0
            
            # Tính ICR
            interest = get_row_value(df_is, ["Chi phí lãi vay", "Interest expense"], year_str=target_year_str)
            if interest and interest != 0:
                icr = ebit / abs(interest)
            else:
                icr = get_row_value(df_ratio, ["Khả năng thanh toán lãi vay", "ICR"], year_str=ratio_year_str)
                
            history.append({
                'year': target_year_str,
                'roic': roic,
                'de': de,
                'cfo': cfo,
                'ni': ni,
                'bp': bp,
                'icr': icr,
                'ep': ep
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
        
        ep_list = [h['ep'] for h in history if h['ep'] > 0]
        avg_ep = np.mean(ep_list) if ep_list else 0
        value_ratio = (avg_ep / avg_roic_5y) if avg_roic_5y != 0 else 0
        
        bp_list = [h['bp'] for h in history if h['bp'] > 0]
        avg_bp = np.mean(bp_list) if bp_list else 0
        
        ed_list = [1 / h['de'] if h['de'] > 0 else 1000 for h in history]
        avg_ed_5y = np.mean(ed_list) if ed_list else 0
        
        current_icr = history[-1]['icr'] if history else 0

        try:
            df_cf_q = f.cash_flow(period='quarter')
            df_is_q = f.income_statement(period='quarter')
            df_bs_q = f.balance_sheet(period='quarter')
            df_ratio_q = f.ratio(period='quarter')
        except:
            df_cf_q, df_is_q, df_bs_q, df_ratio_q = None, None, None, None

        roic_ttm = 0
        cfo_quality_ttm = 0
        de_current = 0
        pb_current = 0
        
        equity_q_val = get_latest_q_value(df_bs_q, ["của công ty mẹ", "Vốn chủ sở hữu", "Equity"]) if df_bs_q is not None else 0
        if equity_q_val == 0 and df_bs is not None:
            equity_q_val = get_row_value(df_bs, ["của công ty mẹ", "Vốn chủ sở hữu", "Equity"], str(latest_year))

        if market_cap_overview > 0 and equity_q_val > 0:
            mc = market_cap_overview * 1e9 if market_cap_overview < 1000000 else market_cap_overview
            pb_current = mc / equity_q_val
        else:
            if df_ratio_q is not None and not df_ratio_q.empty:
                pb_q = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
                if pb_q:
                    pb_current = float(pb_q)
            if pb_current == 0 and history:
                pb_current = 1 / history[-1]['bp'] if history[-1]['bp'] > 0 else 0

        latest_q_str = ""
        if df_is_q is not None and not df_is_q.empty and df_bs_q is not None and not df_bs_q.empty:
            latest_q_str = get_latest_quarter_str(df_is_q, ["Lãi/(lỗ) từ hoạt động kinh doanh", "Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"])
            ebt_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) trước thuế", "Tổng lợi nhuận kế toán trước thuế", "Lợi nhuận trước thuế", "Profit before tax"])
            tax_ttm = get_ttm_value(df_is_q, ["thuế thu nhập doanh nghiệp", "Income tax expense"])
            ni_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) thuần sau thuế", "Lợi nhuận của Cổ đông của Công ty mẹ", "Lợi nhuận sau thuế", "Net income"])
            ebit_ttm = get_ttm_value(df_is_q, ["Lãi/(lỗ) từ hoạt động kinh doanh", "Lợi nhuận thuần từ hoạt động kinh doanh", "Operating profit"])
            if ebit_ttm == 0: ebit_ttm = ebt_ttm
            
            interest_ttm = get_ttm_value(df_is_q, ["Chi phí lãi vay", "Interest expense"])
            if interest_ttm != 0:
                current_icr = ebit_ttm / abs(interest_ttm)
            elif df_ratio_q is not None and not df_ratio_q.empty:
                icr_q = get_latest_q_value(df_ratio_q, ["Khả năng thanh toán lãi vay", "ICR"])
                if icr_q: current_icr = float(icr_q)
                
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
                'DE_Current': de_current,
                'PB_Current': pb_current,
                'Current_Price': float(current_price) if current_price else 0,
                'Latest_Quarter': latest_q_str,
                'Latest_Year': str(history[-1]['year']) if history else ""
            },
            'history': history
        }
    except Exception as e:
        try:
            print(f"Loi khi lay du lieu cho {ticker}: {str(e)[:50]}...")
        except:
            pass
        return None

def get_sector_medians(sector):
    if not sector: return {}
    import os, json
    from datetime import datetime
    
    CACHE_DIR = "cache"
    safe_sector = "".join([c if c.isalnum() else "_" for c in sector])
    today = datetime.now().strftime("%Y-%m-%d")
    medians_cache_file = os.path.join(CACHE_DIR, f"medians_{safe_sector}_{today}.json")
    
    if os.path.exists(medians_cache_file):
        try:
            with open(medians_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
            
    # Nếu chưa có cache, gọi hàm để fetch top 10 và tạo cache
    run_screener_for_sector(sector)
    
    if os.path.exists(medians_cache_file):
        try:
            with open(medians_cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

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
                'ROA_Current': summary.get('ROA_Current', 0),
                'ROE_Current': summary.get('ROE_Current', 0),
                'NIM_Current': summary.get('NIM_Current', 0),
                'PB_Current': summary.get('PB_Current', 0),
                'Value_Ratio_Current': summary.get('Value_Ratio_Current', 0),
                'Current_Price': summary.get('Current_Price', 0)
            })
        else:
            rank_data.append({
                'ticker': t,
                'ROIC_5Y': summary.get('ROIC_5Y', 0),
                'ROIC_TTM': summary.get('ROIC_TTM', 0),
                'Value_Ratio': summary.get('Value_Ratio', 0),
                'CFO_Quality': summary.get('CFO_Quality', 0),
                'CFO_Quality_TTM': summary.get('CFO_Quality_TTM', 0),
                'DE_5Y': summary.get('DE_5Y', 0),
                'DE_Current': summary.get('DE_Current', 0),
                'PB_Current': summary.get('PB_Current', 0)
            })
    
    df_rank = pd.DataFrame(rank_data)
    if not df_rank.empty:
        # Lấy median của sector từ main_ticker
        main_sector = reports[main_ticker]['sector'] if main_ticker in reports else ""
        medians = get_sector_medians(main_sector)
        
        if is_bank:
            m_roa = medians.get('median_roa', 0.02)
            m_nim = medians.get('median_nim', 0.035)
            m_value = medians.get('median_value', 10.0)
            
            df_rank['Score_ROA'] = (df_rank['ROA_Current'] / m_roa) * 100
            df_rank['Score_NIM'] = (df_rank['NIM_Current'] / m_nim) * 100
            df_rank['Score_Value'] = (df_rank['Value_Ratio_Current'] / m_value) * 100
            df_rank['Total_Score'] = (df_rank['Score_ROA'] * 0.50) + (df_rank['Score_NIM'] * 0.15) + (df_rank['Score_Value'] * 0.35)
        else:
            m_roic = medians.get('median_roic', 0.10)
            m_roic_ttm = medians.get('median_roic_ttm', 0.10)
            m_value = medians.get('median_value', 10.0)
            m_cfo = medians.get('median_cfo', 1.0)
            m_cfo_ttm = medians.get('median_cfo_ttm', 1.0)
            m_de = medians.get('median_de', 1.0)
            m_de_curr = medians.get('median_de_curr', 1.0)

            df_rank['Score_ROIC'] = (df_rank['ROIC_5Y'] / m_roic) * 100
            df_rank['Score_ROIC_TTM'] = (df_rank['ROIC_TTM'] / m_roic_ttm) * 100
            df_rank['Score_Value'] = (df_rank['Value_Ratio'] / m_value) * 100
            
            df_rank['Score_CFO'] = (df_rank['CFO_Quality'] / m_cfo) * 100
            df_rank.loc[df_rank['CFO_Quality'] < 0, 'Score_CFO'] = 0
            df_rank['Score_CFO_TTM'] = (df_rank['CFO_Quality_TTM'] / m_cfo_ttm) * 100
            df_rank.loc[df_rank['CFO_Quality_TTM'] < 0, 'Score_CFO_TTM'] = 0
            
            df_rank['Score_DE'] = np.maximum(0, 2 - (df_rank['DE_5Y'] / m_de)) * 100
            df_rank['Score_DE_Current'] = np.maximum(0, 2 - (df_rank['DE_Current'] / m_de_curr)) * 100
            
            df_rank['Total_Score'] = (df_rank['Score_ROIC'] * 0.15) + (df_rank['Score_ROIC_TTM'] * 0.25) + \
                                     (df_rank['Score_Value'] * 0.20) + \
                                     (df_rank['Score_CFO'] * 0.10) + (df_rank['Score_CFO_TTM'] * 0.15) + \
                                     (df_rank['Score_DE'] * 0.05) + (df_rank['Score_DE_Current'] * 0.10)
        
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

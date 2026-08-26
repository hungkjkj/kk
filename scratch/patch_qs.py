import re

with open(r'c:\Users\DMX\Downloads\New folder\web\NEW\data\quant_screener.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Insert after bank logic
target_str = """            return {
                'ticker': ticker,
                'company_name': company_name,
                'sector': 'Ngân hàng',
                'summary': {
                    'ROA_Current': float(roa_q) if roa_q else 0,
                    'ROE_Current': float(roe_q) if roe_q else 0,
                    'NIM_Current': float(nim_q) if nim_q else 0,
                    'PB_Current': float(pb_q) if pb_q else 0,
                    'Value_Ratio_Current': float(value_ratio_q) if value_ratio_q else 0,
                    'Equity_Ratio_Current': float(equity_ratio_q) if equity_ratio_q else 0,
                    'Current_Price': float(current_price) if current_price else 0,
                    'Latest_Quarter': latest_q_str,
                    'Latest_Year': latest_y_str
                },
                'history': history
            }"""

replacement_str = target_str + """
            
        elif sector.lower() in ['chứng khoán', 'securities', 'dịch vụ tài chính', 'dịch vụ tài chính (mở rộng)']:
            f_ratio = Finance(symbol=ticker, source='KBS')
            df_ratio = f_ratio.ratio(period='year')
            
            try:
                df_ratio_q = f_ratio.ratio(period='quarter')
            except:
                df_ratio_q = None
                
            if df_ratio is None or df_ratio.empty:
                return None
                
            years_cols = [c for c in df_ratio.columns if str(c).startswith('20') and '-Năm' in str(c)]
            if not years_cols:
                years_cols = [c for c in df_ratio.columns if str(c).startswith('20')]
                if not years_cols: return None
                
            years_cols = sorted(years_cols, reverse=True)
            latest_year_str = years_cols[0]
            
            import re
            match = re.search(r'\\d{4}', str(latest_year_str))
            if not match: return None
            latest_year = int(match.group(0))
            
            history = []
            num_years = min(len(years_cols), 5)
            
            for i in range(num_years):
                target_year_str = str(latest_year - i)
                ratio_year_str = f"{target_year_str}-Năm" if f"{target_year_str}-Năm" in df_ratio.columns else target_year_str
                
                roe = get_row_value(df_ratio, ["ROEA", "ROE", "lợi nhuận trên vốn chủ sở hữu"], ratio_year_str)
                if roe and abs(roe) > 1 and abs(roe) < 100: roe = roe / 100
                
                pb = get_row_value(df_ratio, ["P/B", "giá trị sổ sách (P/B)"], ratio_year_str)
                pe = get_row_value(df_ratio, ["P/E", "thu nhập trên cổ phần (P/E)", "Chỉ số giá thị trường trên thu nhập (P/E)"], ratio_year_str)
                roa = get_row_value(df_ratio, ["ROAA", "ROA", "sinh lợi trên tổng tài sản"], ratio_year_str)
                if roa and abs(roa) < 100: roa = roa / 100
                
                equity_ratio = (roa / roe) if (roe and roe > 0) else 0
                
                history.append({
                    'year': target_year_str,
                    'roe': float(roe) if roe else 0.0,
                    'pb': float(pb) if pb else 0.0,
                    'pe': float(pe) if pe else 0.0,
                    'roa': float(roa) if roa else 0.0,
                    'equity_ratio': float(equity_ratio)
                })
                
            history.reverse()
            roe_list = [h['roe'] for h in history if h['roe'] != 0]
            avg_roe_5y = sum(roe_list) / len(roe_list) if roe_list else 0
            
            latest_q_str = ""
            if df_ratio_q is not None and not df_ratio_q.empty:
                latest_q_str = get_latest_quarter_str(df_ratio_q, ["ROE", "P/B"])
            latest_y_str = str(history[-1]['year']) if history else ""
            
            pb_q = get_latest_q_value(df_ratio_q, ["P/B", "giá trị sổ sách (P/B)"])
            if pb_q == 0: pb_q = history[-1].get('pb', 0) if history else 0
            
            pe_q = get_latest_q_value(df_ratio_q, ["P/E", "thu nhập trên cổ phần (P/E)", "Chỉ số giá thị trường trên thu nhập (P/E)"])
            if pe_q == 0: pe_q = history[-1].get('pe', 0) if history else 0
            
            roe_ttm = get_latest_q_value(df_ratio_q, ["ROE bình quân 4 quý", "roe_trailling", "ROEA", "ROE", "lợi nhuận trên vốn chủ sở hữu"])
            if roe_ttm == 0: roe_ttm = history[-1].get('roe', 0) if history else 0
            if roe_ttm and abs(roe_ttm) > 1 and abs(roe_ttm) < 100: roe_ttm = roe_ttm / 100
            
            roa_q = get_latest_q_value(df_ratio_q, ["ROA bình quân 4 quý", "roa_trailling", "ROAA", "ROA", "sinh lợi trên tổng tài sản"])
            if roa_q == 0: roa_q = history[-1].get('roa', 0) if history else 0
            if roa_q and abs(roa_q) < 100: roa_q = roa_q / 100
            
            equity_ratio_q = (roa_q / roe_ttm) if (roe_ttm and roe_ttm > 0) else 0
            
            return {
                'ticker': ticker,
                'company_name': company_name,
                'sector': 'Chứng khoán',
                'summary': {
                    'PB_Current': float(pb_q) if pb_q else 0,
                    'PE_Current': float(pe_q) if pe_q else 0,
                    'ROE_TTM': float(roe_ttm) if roe_ttm else 0,
                    'ROE_5Y': float(avg_roe_5y),
                    'Equity_Ratio_Current': float(equity_ratio_q),
                    'Current_Price': float(current_price) if current_price else 0,
                    'Latest_Quarter': latest_q_str,
                    'Latest_Year': latest_y_str
                },
                'history': history
            }
"""

content = content.replace(target_str, replacement_str)

target_str2 = """
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
                'Equity_Ratio_Current': summary.get('Equity_Ratio_Current', 0),
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
                'PB_Current': summary.get('PB_Current', 0),
                'BP_5Y': summary.get('BP_5Y', 0),
                'Current_Price': summary.get('Current_Price', 0)
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
            m_eq = medians.get('median_eq', 0.1)
            
            df_rank['Score_ROA'] = (df_rank['ROA_Current'] / m_roa) * 100
            df_rank['Score_NIM'] = (df_rank['NIM_Current'].clip(upper=0.045) / m_nim) * 100
            df_rank['Score_Value'] = (df_rank['Value_Ratio_Current'] / m_value) * 100
            df_rank['Score_EQ'] = (df_rank['Equity_Ratio_Current'] / m_eq) * 100
            df_rank['Total_Score'] = (df_rank['Score_Value'] * 0.30) + (df_rank['Score_EQ'] * 0.25) + (df_rank['Score_ROA'] * 0.25) + (df_rank['Score_NIM'] * 0.20)
        else:"""

replacement_str2 = """
    rank_data = []
    is_bank = False
    is_securities = False
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
                'Equity_Ratio_Current': summary.get('Equity_Ratio_Current', 0),
                'Current_Price': summary.get('Current_Price', 0)
            })
        elif rep['sector'].lower() in ['chứng khoán', 'securities', 'dịch vụ tài chính', 'dịch vụ tài chính (mở rộng)']:
            is_securities = True
            rank_data.append({
                'ticker': t,
                'PB_Current': summary.get('PB_Current', 0),
                'PE_Current': summary.get('PE_Current', 0),
                'ROE_TTM': summary.get('ROE_TTM', 0),
                'ROE_5Y': summary.get('ROE_5Y', 0),
                'Equity_Ratio_Current': summary.get('Equity_Ratio_Current', 0),
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
                'PB_Current': summary.get('PB_Current', 0),
                'BP_5Y': summary.get('BP_5Y', 0),
                'Current_Price': summary.get('Current_Price', 0)
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
            m_eq = medians.get('median_eq', 0.1)
            
            df_rank['Score_ROA'] = (df_rank['ROA_Current'] / m_roa) * 100
            df_rank['Score_NIM'] = (df_rank['NIM_Current'].clip(upper=0.045) / m_nim) * 100
            df_rank['Score_Value'] = (df_rank['Value_Ratio_Current'] / m_value) * 100
            df_rank['Score_EQ'] = (df_rank['Equity_Ratio_Current'] / m_eq) * 100
            df_rank['Total_Score'] = (df_rank['Score_Value'] * 0.30) + (df_rank['Score_EQ'] * 0.25) + (df_rank['Score_ROA'] * 0.25) + (df_rank['Score_NIM'] * 0.20)
        elif is_securities:
            import numpy as np
            m_pb = medians.get('median_pb', 1.5)
            m_pe = medians.get('median_pe', 15.0)
            m_roe = medians.get('median_roe_ttm', 0.1)
            m_roe5 = medians.get('median_roe_5y', 0.1)
            m_eq = medians.get('median_eq', 0.3)
            
            df_rank['Score_PB'] = np.where(df_rank['PB_Current'] > 0, (m_pb / df_rank['PB_Current']) * 100, 0)
            df_rank['Score_PE'] = np.where(df_rank['PE_Current'] > 0, (m_pe / df_rank['PE_Current']) * 100, 0)
            df_rank['Score_ROE_TTM'] = (df_rank['ROE_TTM'] / m_roe) * 100
            df_rank['Score_ROE_5Y'] = (df_rank['ROE_5Y'] / m_roe5) * 100
            df_rank['Score_EQ'] = (df_rank['Equity_Ratio_Current'] / m_eq) * 100
            
            df_rank['Total_Score'] = (df_rank['Score_PB'] * 0.30) + (df_rank['Score_PE'] * 0.20) + \
                                     (df_rank['Score_ROE_TTM'] * 0.20) + (df_rank['Score_ROE_5Y'] * 0.15) + \
                                     (df_rank['Score_EQ'] * 0.15)
        else:"""

content = content.replace(target_str2, replacement_str2)

with open(r'c:\Users\DMX\Downloads\New folder\web\NEW\data\quant_screener.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("quant_screener.py updated successfully.")

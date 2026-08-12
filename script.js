let currentData = null;

// Settings toggle
document.getElementById('showSettings').addEventListener('change', (e) => {
    const box = document.getElementById('settingsBox');
    if (e.target.checked) box.classList.remove('hidden');
    else box.classList.add('hidden');
});

document.getElementById('analyzeBtn').addEventListener('click', () => {
    const ticker = document.getElementById('tickerInput').value.trim();
    if (!ticker) {
        showError("Vui lòng nhập mã cổ phiếu.");
        return;
    }
    
    // Get settings
    const rf = document.getElementById('inputRf').value;
    const beta = document.getElementById('inputBeta').value;
    const erp = document.getElementById('inputErp').value;
    const pe = document.getElementById('inputPE').value;
    
    // Build query params
    const params = new URLSearchParams();
    if (rf) params.append('user_rf', rf);
    if (beta) params.append('user_beta', beta);
    if (erp) params.append('user_erp', erp);
    if (pe) params.append('user_pe', pe);
    
    const qs = params.toString();
    const url = `/api/analyze/${ticker}` + (qs ? `?${qs}` : '');

    // Hide previous results/errors
    document.getElementById('resultContainer').classList.add('hidden');
    document.getElementById('errorContainer').classList.add('hidden');
    document.getElementById('loadingIndicator').classList.remove('hidden');
    
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error("Lỗi khi tải dữ liệu từ server.");
            return response.json();
        })
        .then(data => {
            document.getElementById('loadingIndicator').classList.add('hidden');
            currentData = data;
            
            // Basic
            document.getElementById('companyName').textContent = data.company_profile.companyName || ticker;
            document.getElementById('tickerBadge').textContent = data.ticker;
            if (data.company_profile.industry) {
                document.getElementById('industryBadge').textContent = data.company_profile.industry;
                document.getElementById('industryBadge').style.display = 'inline-block';
            } else {
                document.getElementById('industryBadge').style.display = 'none';
            }
            document.getElementById('valuationNote').textContent = data.notes;
            
            // Format functions
            const formatVND = (num) => new Intl.NumberFormat('vi-VN').format(num);
            const formatPercent = (num) => (num * 100).toFixed(1) + "%";
            
            // Current Price
            if (data.valuation && data.valuation.current_price) {
                document.getElementById('currentPrice').textContent = "Giá HT: " + formatVND(data.valuation.current_price) + " ₫";
            } else {
                document.getElementById('currentPrice').textContent = "Giá HT: N/A";
            }
            
            // 1. Valuation
            document.getElementById('grahamValue').textContent = data.valuation_results.graham.value_vnd ? formatVND(data.valuation_results.graham.value_vnd) + " ₫" : "N/A";
            document.getElementById('dcfValue').textContent = data.valuation_results.dcf.value_vnd ? formatVND(data.valuation_results.dcf.value_vnd) + " ₫" : "N/A";
            document.getElementById('peValue').textContent = data.valuation_results.relative_pe.value_vnd ? formatVND(data.valuation_results.relative_pe.value_vnd) + " ₫" : "N/A";
            
            // Source tags
            document.getElementById('dcfSource').textContent = `g: ${data.valuation_results.dcf.params.g}% (${data.valuation_results.dcf.params.g_source}) | r: ${data.valuation_results.dcf.params.r}% (${data.valuation_results.dcf.params.r_source})`;
            document.getElementById('peSource').textContent = `P/E: ${data.valuation_results.relative_pe.params.pe} (${data.valuation_results.relative_pe.params.pe_source})`;
            
            // 2. Growth
            document.getElementById('valCagr').textContent = formatPercent(data.growth.cagr_eps_5yr);
            document.getElementById('valProfitGrowth').textContent = formatPercent(data.growth.profit_growth);
            
            // 3. Quality
            document.getElementById('valRoe').textContent = formatPercent(data.quality.roe);
            document.getElementById('valNetMargin').textContent = formatPercent(data.quality.net_margin);
            document.getElementById('valFcf').textContent = formatVND(data.quality.fcf / 1e9) + " Tỷ";
            
            // 4. Balance Sheet
            document.getElementById('valCash').textContent = formatVND(data.balance_sheet.cash / 1e9) + " Tỷ";
            document.getElementById('valEquity').textContent = formatVND(data.balance_sheet.equity / 1e9) + " Tỷ";
            if (data.financial_summary && data.financial_summary.latest_bvps) {
                document.getElementById('valBvps').textContent = formatVND(data.financial_summary.latest_bvps) + " ₫";
            } else {
                document.getElementById('valBvps').textContent = "N/A";
            }
            
            // 5. Hist Valuation
            document.getElementById('valHistPe').textContent = data.valuation.historical_pe.toFixed(1);
            document.getElementById('valHistPb').textContent = data.valuation.pb.toFixed(1);
            
            // 6. Foreign Trade
            if (data.foreign_trade && data.foreign_trade.net_value_14d !== undefined) {
                const net = data.foreign_trade.net_value_14d;
                const el = document.getElementById('valForeignNet');
                if (net === 0) {
                    el.textContent = "--";
                    el.style.color = "";
                } else {
                    el.textContent = (net / 1e9).toFixed(2) + " Tỷ";
                    if (net > 0) el.style.color = '#4CAF50';
                    else el.style.color = '#F44336';
                }
            } else {
                document.getElementById('valForeignNet').textContent = "N/A";
            }
            
            document.getElementById('resultContainer').classList.remove('hidden');
        })
        .catch(err => {
            document.getElementById('loadingIndicator').classList.add('hidden');
            showError(err.message);
        });
});

document.getElementById('tickerInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') document.getElementById('analyzeBtn').click();
});

document.getElementById('exportBtn').addEventListener('click', () => {
    if (!currentData) return;
    const dataStr = JSON.stringify(currentData, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Vnstock_Analysis_${currentData.ticker}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

function showError(msg) {
    const errContainer = document.getElementById('errorContainer');
    document.getElementById('errorMsg').textContent = msg;
    errContainer.classList.remove('hidden');
}

let currentData = null;

document.getElementById('analyzeBtn').addEventListener('click', () => {
    const ticker = document.getElementById('tickerInput').value.trim();
    if (!ticker) {
        showError("Vui lòng nhập mã cổ phiếu.");
        return;
    }
    
    // Hide previous results/errors
    document.getElementById('resultContainer').classList.add('hidden');
    document.getElementById('errorContainer').classList.add('hidden');
    
    // Show loading
    document.getElementById('loadingIndicator').classList.remove('hidden');
    
    // Fetch data from API
    fetch(`/api/analyze/${ticker}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Lỗi khi tải dữ liệu từ server. Vui lòng thử lại sau.");
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('loadingIndicator').classList.add('hidden');
            currentData = data;
            
            // Populate UI
            const companyName = data.company_profile.companyName || data.company_profile.organName || data.ticker;
            document.getElementById('companyName').textContent = companyName;
            document.getElementById('tickerBadge').textContent = data.ticker;
            
            // Format numbers
            const formatVND = (num) => new Intl.NumberFormat('vi-VN').format(num);
            
            if (data.valuation.graham.value_vnd) {
                document.getElementById('grahamValue').textContent = formatVND(data.valuation.graham.value_vnd) + " ₫";
            } else {
                document.getElementById('grahamValue').textContent = "N/A";
            }

            if (data.valuation.dcf.value_vnd) {
                document.getElementById('dcfValue').textContent = formatVND(data.valuation.dcf.value_vnd) + " ₫";
            } else {
                document.getElementById('dcfValue').textContent = "N/A";
            }

            if (data.valuation.relative_pe.value_vnd) {
                document.getElementById('peValue').textContent = formatVND(data.valuation.relative_pe.value_vnd) + " ₫";
            } else {
                document.getElementById('peValue').textContent = "N/A";
            }
            document.getElementById('epsValue').textContent = formatVND(data.financial_summary.latest_eps);
            document.getElementById('bvpsValue').textContent = formatVND(data.financial_summary.latest_bvps);
            
            document.getElementById('resultContainer').classList.remove('hidden');
        })
        .catch(err => {
            document.getElementById('loadingIndicator').classList.add('hidden');
            showError(err.message);
        });
});

document.getElementById('tickerInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('analyzeBtn').click();
    }
});

document.getElementById('exportBtn').addEventListener('click', () => {
    if (!currentData) return;
    
    // Create blob and download
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

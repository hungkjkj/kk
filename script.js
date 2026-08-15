document.addEventListener('DOMContentLoaded', () => {
    const tickerInput = document.getElementById('ticker-input');
    const runBtn = document.getElementById('run-btn');
    const statusMessage = document.getElementById('status-message');
    const reportContainer = document.getElementById('report-container');
    const summaryCards = document.getElementById('summary-cards');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');

    let charts = {}; // Store chart instances to destroy them later

    runBtn.addEventListener('click', () => {
        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            showError('Vui lòng nhập mã cổ phiếu.');
            return;
        }
        runReport(ticker);
    });
    
    tickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') runBtn.click();
    });

    async function runReport(ticker) {
        // UI Loading state
        runBtn.disabled = true;
        tickerInput.disabled = true;
        btnText.textContent = 'Đang phân tích...';
        spinner.style.display = 'block';
        reportContainer.style.display = 'none';
        statusMessage.textContent = `Hệ thống đang tải dữ liệu cho mã "${ticker}". Vui lòng đợi...`;
        statusMessage.style.color = '#38bdf8';

        try {
            const response = await fetch(`/api/report?ticker=${encodeURIComponent(ticker)}`);
            const data = await response.json();

            if (data.status === 'success' && data.data) {
                renderReport(data.data);
                statusMessage.textContent = `Đã phân tích xong dữ liệu cho ${ticker}!`;
                statusMessage.style.color = 'var(--success-color)';
            } else {
                showError(data.detail || 'Có lỗi xảy ra trong quá trình lấy dữ liệu.');
            }
        } catch (error) {
            showError('Lỗi kết nối hoặc mã cổ phiếu không tồn tại.');
            console.error(error);
        } finally {
            // Restore UI
            runBtn.disabled = false;
            tickerInput.disabled = false;
            btnText.textContent = 'Phân tích';
            spinner.style.display = 'none';
        }
    }

    function renderReport(data) {
        const { summary, history } = data;
        
        // Render Summary
        const formatPct = (val) => (val * 100).toFixed(2) + '%';
        const formatNum = (val) => val.toFixed(2);
        
        summaryCards.innerHTML = `
            <div class="card">
                <h3>ROIC (5Y Avg)</h3>
                <p>${formatPct(summary.ROIC_5Y)}</p>
            </div>
            <div class="card">
                <h3>Value Ratio</h3>
                <p>${formatNum(summary.Value_Ratio)}</p>
            </div>
            <div class="card">
                <h3>CFO Quality</h3>
                <p>${formatNum(summary.CFO_Quality)}</p>
            </div>
            <div class="card">
                <h3>D/E (5Y Avg)</h3>
                <p>${formatNum(summary.DE_5Y)}</p>
            </div>
            <div class="card">
                <h3>ICR (Current)</h3>
                <p>${formatNum(summary.ICR_Current)}</p>
            </div>
        `;
        
        // Destroy old charts if exist
        Object.values(charts).forEach(chart => chart.destroy());
        charts = {};
        
        const labels = history.map(h => h.year);
        
        // Setup Charts
        Chart.defaults.color = 'rgba(255, 255, 255, 0.7)';
        Chart.defaults.font.family = 'Inter';
        
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                x: { 
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    offset: true
                }
            }
        };

        // ROIC Chart
        const ctxRoic = document.getElementById('roicChart').getContext('2d');
        charts.roic = new Chart(ctxRoic, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'ROIC (%)',
                    data: history.map(h => (h.roic * 100).toFixed(2)),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: commonOptions
        });

        // D/E Chart
        const ctxDe = document.getElementById('deChart').getContext('2d');
        charts.de = new Chart(ctxDe, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'D/E Ratio',
                    data: history.map(h => h.de.toFixed(2)),
                    backgroundColor: '#fbbf24',
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, beginAtZero: true }
                }
            }
        });

        // CFO vs NI Chart
        const ctxCf = document.getElementById('cfChart').getContext('2d');
        charts.cf = new Chart(ctxCf, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'CFO (Tỷ VNĐ)',
                        data: history.map(h => (h.cfo / 1e9).toFixed(1)),
                        backgroundColor: '#10b981',
                    },
                    {
                        label: 'Net Income (Tỷ VNĐ)',
                        data: history.map(h => (h.ni / 1e9).toFixed(1)),
                        backgroundColor: '#f43f5e',
                    }
                ]
            },
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, beginAtZero: true }
                }
            }
        });

        // B/P Chart
        const ctxBp = document.getElementById('bpChart').getContext('2d');
        charts.bp = new Chart(ctxBp, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'B/P Ratio',
                    data: history.map(h => h.bp.toFixed(2)),
                    borderColor: '#a855f7',
                    backgroundColor: 'rgba(168, 85, 247, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, beginAtZero: true }
                }
            }
        });

        // ICR Chart
        const ctxIcr = document.getElementById('icrChart').getContext('2d');
        charts.icr = new Chart(ctxIcr, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Interest Coverage Ratio (ICR)',
                    data: history.map(h => h.icr.toFixed(2)),
                    backgroundColor: '#14b8a6', // Teal color
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: { ...commonOptions.scales.y, beginAtZero: true }
                }
            }
        });

        reportContainer.style.display = 'block';
    }

    function showError(msg) {
        statusMessage.textContent = msg;
        statusMessage.style.color = 'var(--danger-color)';
        tickerInput.disabled = false;
        runBtn.disabled = false;
    }
});

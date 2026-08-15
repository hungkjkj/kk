document.addEventListener('DOMContentLoaded', () => {
    const tickerInput = document.getElementById('ticker-input');
    const peerInput = document.getElementById('peer-input');
    const runBtn = document.getElementById('run-btn');
    const statusMessage = document.getElementById('status-message');
    const reportContainer = document.getElementById('report-container');
    const summaryCards = document.getElementById('summary-cards');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');
    const rankingContainer = document.getElementById('ranking-container');
    const rankingBody = document.getElementById('ranking-body');

    let charts = {}; // Store chart instances to destroy them later

    // Color palette for different companies
    const chartColors = [
        { border: '#38bdf8', bg: 'rgba(56, 189, 248, 0.1)' }, // Main (Blue)
        { border: '#fbbf24', bg: 'rgba(251, 191, 36, 0.1)' }, // Yellow
        { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' }, // Green
        { border: '#f43f5e', bg: 'rgba(244, 63, 94, 0.1)' }, // Pink
        { border: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)' }  // Purple
    ];

    runBtn.addEventListener('click', () => {
        const ticker = tickerInput.value.trim().toUpperCase();
        const peers = peerInput.value.trim().toUpperCase();
        if (!ticker) {
            showError('Vui lòng nhập mã cổ phiếu chính.');
            return;
        }
        runReport(ticker, peers);
    });
    
    tickerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') runBtn.click();
    });
    peerInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') runBtn.click();
    });

    async function runReport(ticker, peers) {
        // UI Loading state
        runBtn.disabled = true;
        tickerInput.disabled = true;
        peerInput.disabled = true;
        btnText.textContent = 'Đang phân tích...';
        spinner.style.display = 'block';
        reportContainer.style.display = 'none';
        statusMessage.textContent = `Hệ thống đang tải dữ liệu cho mã "${ticker}"${peers ? ` và các mã so sánh` : ''}. Vui lòng đợi...`;
        statusMessage.style.color = '#38bdf8';

        try {
            const queryParams = new URLSearchParams({ ticker: ticker, peers: peers });
            const response = await fetch(`/api/report?${queryParams.toString()}`);
            const data = await response.json();

            if (data.status === 'success' && data.data) {
                renderReport(data.data);
                statusMessage.textContent = `Đã phân tích xong dữ liệu!`;
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
            peerInput.disabled = false;
            btnText.textContent = 'Phân tích';
            spinner.style.display = 'none';
        }
    }

    function renderReport(data) {
        const { main_ticker, reports, ranking } = data;
        
        const mainReport = reports[main_ticker];
        if (!mainReport) {
            showError('Không lấy được dữ liệu cho mã chính.');
            return;
        }

        const { company_name, sector, summary, history } = mainReport;
        
        // Render Company Info
        const companyInfo = document.getElementById('company-info');
        if (companyInfo) {
            companyInfo.innerHTML = `
                <h2 style="color: var(--text-color); font-size: 1.8rem; margin-bottom: 0.5rem; font-weight: 700;">${company_name || main_ticker}</h2>
                <p style="color: #94a3b8; font-size: 1.1rem; letter-spacing: 0.05em; text-transform: uppercase;">Lĩnh vực: <span style="color: var(--primary-color);">${sector || 'Chưa phân loại'}</span></p>
            `;
        }
        
        // Render Ranking Table
        if (ranking && ranking.length > 1) {
            rankingContainer.style.display = 'block';
            let html = '';
            ranking.forEach((r, idx) => {
                const isMain = r.ticker === main_ticker;
                const rowStyle = isMain ? 'background: rgba(56, 189, 248, 0.15); font-weight: bold; color: #fff;' : '';
                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); ${rowStyle}">
                        <td style="padding: 12px;">${idx + 1}</td>
                        <td style="padding: 12px; color: ${isMain ? '#38bdf8' : 'inherit'}">${r.ticker}</td>
                        <td style="padding: 12px; color: #fbbf24;">${r.Total_Score.toFixed(1)}</td>
                        <td style="padding: 12px;">${(r.ROIC_5Y * 100).toFixed(1)}%</td>
                        <td style="padding: 12px;">${r.BP_5Y.toFixed(2)}</td>
                        <td style="padding: 12px;">${r.CFO_Quality.toFixed(2)}</td>
                        <td style="padding: 12px;">${r.ED_5Y.toFixed(2)}</td>
                        <td style="padding: 12px;">${r.ICR_Current.toFixed(2)}</td>
                    </tr>
                `;
            });
            rankingBody.innerHTML = html;
        } else {
            rankingContainer.style.display = 'none';
        }

        // Render Summary (Always for main ticker)
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
        
        // Prepare datasets for charts
        const labels = history.map(h => h.year);
        
        let datasetsRoic = [];
        let datasetsDe = [];
        let datasetsCfo = [];
        let datasetsBp = [];
        let datasetsIcr = [];

        let colorIndex = 0;
        
        // We want main ticker to be first
        const tickersToPlot = [main_ticker, ...Object.keys(reports).filter(t => t !== main_ticker)];

        for (const t of tickersToPlot) {
            const rep = reports[t];
            if (!rep || !rep.history) continue;
            
            const hist = rep.history;
            const c = chartColors[colorIndex % chartColors.length];
            const isMain = t === main_ticker;
            const borderWidth = isMain ? 3 : 2;

            datasetsRoic.push({
                label: `${t} ROIC (%)`,
                data: hist.map(h => (h.roic * 100).toFixed(2)),
                borderColor: c.border,
                backgroundColor: c.bg,
                borderWidth: borderWidth,
                tension: 0.4
            });

            datasetsDe.push({
                label: `${t} D/E`,
                data: hist.map(h => h.de.toFixed(2)),
                borderColor: c.border,
                backgroundColor: c.bg,
                borderWidth: borderWidth,
                tension: 0.4
            });
            
            // CFO Quality = CFO / NI
            datasetsCfo.push({
                label: `${t} CFO/NI`,
                data: hist.map(h => (h.ni !== 0 ? (h.cfo / h.ni) : 0).toFixed(2)),
                borderColor: c.border,
                backgroundColor: c.bg,
                borderWidth: borderWidth,
                tension: 0.4
            });

            datasetsBp.push({
                label: `${t} B/P`,
                data: hist.map(h => h.bp.toFixed(2)),
                borderColor: c.border,
                backgroundColor: c.bg,
                borderWidth: borderWidth,
                tension: 0.4
            });

            datasetsIcr.push({
                label: `${t} ICR`,
                data: hist.map(h => h.icr.toFixed(2)),
                borderColor: c.border,
                backgroundColor: c.bg,
                borderWidth: borderWidth,
                tension: 0.4
            });

            colorIndex++;
        }

        // Setup Charts
        Chart.defaults.color = 'rgba(255, 255, 255, 0.7)';
        Chart.defaults.font.family = 'Inter';
        
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                tooltip: { mode: 'index', intersect: false }
            },
            interaction: { mode: 'nearest', axis: 'x', intersect: false },
            scales: {
                y: { grid: { color: 'rgba(255, 255, 255, 0.1)' } },
                x: { 
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    offset: true
                }
            }
        };

        const createLineChart = (ctxId, datasets) => {
            return new Chart(document.getElementById(ctxId).getContext('2d'), {
                type: 'line',
                data: { labels: labels, datasets: datasets },
                options: commonOptions
            });
        };

        charts.roic = createLineChart('roicChart', datasetsRoic);
        charts.de = createLineChart('deChart', datasetsDe);
        charts.cf = createLineChart('cfChart', datasetsCfo);
        charts.bp = createLineChart('bpChart', datasetsBp);
        charts.icr = createLineChart('icrChart', datasetsIcr);

        // Update titles if necessary (CFO vs NI is now CFO/NI)
        document.querySelector('#cfChart').parentElement.querySelector('h3').textContent = 'CFO / Net Income (CFO Quality)';

        reportContainer.style.display = 'block';
    }

    function showError(msg) {
        statusMessage.textContent = msg;
        statusMessage.style.color = 'var(--danger-color)';
        tickerInput.disabled = false;
        peerInput.disabled = false;
        runBtn.disabled = false;
    }
});

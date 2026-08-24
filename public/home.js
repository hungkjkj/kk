document.addEventListener('DOMContentLoaded', () => {
    const homeGrid = document.getElementById('home-grid');
    const targetSectors = ['Ngân hàng', 'Bán lẻ', 'Công nghệ thông tin', 'Xây dựng và Vật liệu'];

    // Initialize UI with skeletons
    targetSectors.forEach(sector => {
        const safeId = sector.replace(/\s+/g, '-').toLowerCase();
        const cardHtml = `
            <div class="sector-card glass" id="card-${safeId}">
                <h2>${sector}</h2>
                <div class="table-container">
                    <table class="sector-table">
                        <thead>
                            <tr style="background: rgba(255,255,255,0.05);">
                                <th>#</th>
                                <th>Mã CP</th>
                                <th>Điểm</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-${safeId}">
                            <tr><td colspan="3"><div class="skeleton-row"></div></td></tr>
                            <tr><td colspan="3"><div class="skeleton-row"></div></td></tr>
                            <tr><td colspan="3"><div class="skeleton-row"></div></td></tr>
                            <tr><td colspan="3"><div class="skeleton-row"></div></td></tr>
                            <tr><td colspan="3"><div class="skeleton-row"></div></td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        homeGrid.insertAdjacentHTML('beforeend', cardHtml);
    });

    // Fetch data sequentially to avoid API rate limits
    async function loadAllSectors() {
        for (const sector of targetSectors) {
            const safeId = sector.replace(/\s+/g, '-').toLowerCase();
            await fetchDataForSector(sector, safeId);
        }
    }
    
    loadAllSectors();

    async function fetchDataForSector(sector, elementId) {
        try {
            // Using a cache buster but relying on backend caching for speed
            const response = await fetch(`/api/screener?sector=${encodeURIComponent(sector)}`);
            if (!response.ok) throw new Error('API server error');
            const data = await response.json();

            const tbody = document.getElementById(`tbody-${elementId}`);
            tbody.innerHTML = ''; // clear skeletons

            if (data.status === 'success' && data.data && data.data.length > 0) {
                const isBank = sector.toLowerCase().includes('ngân hàng') || sector.toLowerCase().includes('bank');
                
                // Add more headers if we have actual data
                const thead = document.querySelector(`#card-${elementId} thead`);
                let headers = '';
                if (isBank) {
                    headers = `
                        <tr style="background: rgba(255,255,255,0.05); color: #94a3b8;">
                            <th class="py-3 px-4">#</th>
                            <th class="py-3 px-4">Mã CP</th>
                            <th class="py-3 px-4">Điểm</th>
                            <th class="py-3 px-4">ROA</th>
                            <th class="py-3 px-4">NIM</th>
                            <th class="py-3 px-4">Value</th>
                            <th class="py-3 px-4">EQ</th>
                        </tr>
                    `;
                } else {
                    headers = `
                        <tr style="background: rgba(255,255,255,0.05); color: #94a3b8;">
                            <th>#</th>
                            <th>Mã CP</th>
                            <th>Điểm</th>
                            <th>ROIC(TTM)</th>
                            <th>CFO/NI</th>
                            <th>Value</th>
                        </tr>
                    `;
                }
                thead.innerHTML = headers;

                data.data.slice(0, 10).forEach((r, idx) => {
                    const t = r.ticker || r.Ticker || r.TICKER;
                    const score = r['Total Score'] || r.Total_Score || 0;
                    
                    if (isBank) {
                        const roa = r.ROA ? (r.ROA * 100).toFixed(1) + '%' : '-';
                        const nim = r.NIM ? (r.NIM * 100).toFixed(1) + '%' : '-';
                        const value = r.Value_Ratio ? (r.Value_Ratio * 100).toFixed(1) : '-';
                        const eq = r.Equity_Ratio ? (r.Equity_Ratio * 100).toFixed(1) + '%' : '-';
                        
                        tbody.innerHTML += `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <td class="py-3 px-4 font-bold text-white">${idx + 1}</td>
                                <td class="py-3 px-4 font-bold text-blue-400 cursor-pointer ticker-link hover:text-blue-300">${t}</td>
                                <td class="py-3 px-4 font-bold text-yellow-500">${score.toFixed(1)}</td>
                                <td class="py-3 px-4 text-gray-300">${roa}</td>
                                <td class="py-3 px-4 text-gray-300">${nim}</td>
                                <td class="py-3 px-4 text-emerald-400">${value}</td>
                                <td class="py-3 px-4 text-gray-300">${eq}</td>
                            </tr>
                        `;
                    } else {
                        const roic = r.ROIC_TTM ? (r.ROIC_TTM * 100).toFixed(1) + '%' : '-';
                        const cfo = r.CFO_Quality_TTM ? r.CFO_Quality_TTM.toFixed(2) : '-';
                        const val = r.Value_Ratio ? r.Value_Ratio.toFixed(1) : '-';
                        
                        tbody.innerHTML += `
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                                <td>${idx + 1}</td>
                                <td style="color: #38bdf8; font-weight: bold;">${t}</td>
                                <td style="color: #fbbf24; font-weight: bold;">${score.toFixed(1)}</td>
                                <td>${roic}</td>
                                <td>${cfo}</td>
                                <td style="color: #10b981;">${val}</td>
                            </tr>
                        `;
                    }
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #94a3b8;">Không có dữ liệu hoặc lỗi.</td></tr>`;
            }
        } catch (error) {
            console.error(error);
            const tbody = document.getElementById(`tbody-${elementId}`);
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--danger-color);">Lỗi tải dữ liệu.</td></tr>`;
        }
    }
});

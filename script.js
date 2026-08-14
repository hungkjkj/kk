document.addEventListener('DOMContentLoaded', () => {
    const sectorSelect = document.getElementById('sector-select');
    const runBtn = document.getElementById('run-btn');
    const statusMessage = document.getElementById('status-message');
    const tableContainer = document.getElementById('table-container');
    const tableBody = document.getElementById('table-body');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.querySelector('.spinner');

    // Fetch sectors on load
    fetchSectors();

    runBtn.addEventListener('click', () => {
        const selectedSector = sectorSelect.value;
        if (!selectedSector) return;
        runScreener(selectedSector);
    });

    async function fetchSectors() {
        try {
            const response = await fetch('/api/sectors');
            const data = await response.json();
            
            if (data.status === 'success') {
                populateSectors(data.sectors);
            } else {
                showError('Không thể tải danh sách ngành.');
            }
        } catch (error) {
            showError('Lỗi kết nối đến máy chủ.');
            console.error(error);
        }
    }

    function populateSectors(sectors) {
        sectorSelect.innerHTML = '<option value="">-- Chọn một ngành --</option>';
        sectors.forEach(sector => {
            const option = document.createElement('option');
            option.value = sector;
            option.textContent = sector;
            sectorSelect.appendChild(option);
        });
        sectorSelect.disabled = false;
        runBtn.disabled = false;
    }

    async function runScreener(sector) {
        // UI Loading state
        runBtn.disabled = true;
        sectorSelect.disabled = true;
        btnText.textContent = 'Đang phân tích...';
        spinner.style.display = 'block';
        tableContainer.style.display = 'none';
        statusMessage.textContent = `Hệ thống đang quét các mã thuộc ngành "${sector}". Vui lòng đợi... (Khoảng 1-2 phút)`;
        statusMessage.style.color = '#38bdf8';

        try {
            const response = await fetch(`/api/screener?sector=${encodeURIComponent(sector)}`);
            const data = await response.json();

            if (data.status === 'success') {
                renderTable(data.data);
                statusMessage.textContent = `Đã phân tích xong ${data.data.length} mã cổ phiếu hợp lệ!`;
                statusMessage.style.color = 'var(--success-color)';
            } else {
                showError(data.detail || 'Có lỗi xảy ra trong quá trình tính toán.');
            }
        } catch (error) {
            showError('Lỗi kết nối. Có thể máy chủ đang bận, vui lòng thử lại sau.');
            console.error(error);
        } finally {
            // Restore UI
            runBtn.disabled = false;
            sectorSelect.disabled = false;
            btnText.textContent = 'Quét Ngành Này';
            spinner.style.display = 'none';
        }
    }

    function renderTable(data) {
        tableBody.innerHTML = '';
        
        if (!data || data.length === 0) {
            tableContainer.style.display = 'none';
            statusMessage.textContent = 'Không có mã nào đủ điều kiện (Vốn hóa, Thanh khoản) trong ngành này.';
            statusMessage.style.color = '#fbbf24';
            return;
        }

        data.forEach(row => {
            const tr = document.createElement('tr');
            
            // Format numbers
            const formatPct = (val) => (val * 100).toFixed(2) + '%';
            const formatNum = (val) => val.toFixed(2);
            
            // Score Heatmap Color
            let scoreClass = 'score-mid';
            if (row['Total Score'] >= 80) scoreClass = 'score-high';
            else if (row['Total Score'] < 40) scoreClass = 'score-low';

            tr.innerHTML = `
                <td>${row['Ticker']}</td>
                <td>${formatPct(row['ROIC_5Y'])}</td>
                <td>${formatNum(row['Value_Ratio'])}</td>
                <td>${formatNum(row['CFO_Quality'])}</td>
                <td>${formatNum(row['DE_5Y'])}</td>
                <td class="${scoreClass}">${formatNum(row['Total Score'])}</td>
            `;
            tableBody.appendChild(tr);
        });

        tableContainer.style.display = 'block';
    }

    function showError(msg) {
        statusMessage.textContent = msg;
        statusMessage.style.color = 'var(--danger-color)';
        sectorSelect.disabled = false;
        runBtn.disabled = false;
    }
});

#!/usr/bin/env python3
"""
Generate interactive HTML dashboard with AI penetration data + Gong conversations.
"""
import json
from pathlib import Path

def generate_html():
    """Generate the dashboard HTML."""

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Product Penetration Dashboard - APAC</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f9fafb;
            color: #1f2937;
            padding: 20px;
            font-size: 13px;
        }

        .header {
            background: white;
            padding: 24px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }

        h1 {
            font-size: 24px;
            font-weight: 700;
            color: #03363d;
            margin-bottom: 8px;
        }

        .subtitle {
            color: #6b7280;
            font-size: 14px;
        }

        .filters-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .filter-group {
            margin-bottom: 16px;
        }

        .filter-label {
            font-weight: 600;
            font-size: 12px;
            color: #374151;
            margin-bottom: 6px;
            display: block;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .filter-select {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 13px;
            font-family: 'Inter', sans-serif;
            background: white;
            max-height: 200px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin-bottom: 20px;
        }

        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #03363d;
            margin-bottom: 4px;
        }

        .metric-label {
            font-size: 12px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .insights-section {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }

        .insight {
            padding: 12px;
            margin-bottom: 8px;
            background: #f0fdf4;
            border-left: 4px solid #d1f470;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .insight:hover {
            background: #dcfce7;
        }

        .insight-title {
            font-weight: 600;
            color: #03363d;
            margin-bottom: 4px;
        }

        .insight-detail {
            font-size: 12px;
            color: #6b7280;
        }

        .insight-accounts {
            display: none;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #e5e7eb;
        }

        .insight-accounts.expanded {
            display: block;
        }

        .account-link {
            color: #0066cc;
            text-decoration: none;
            display: inline-block;
            margin-right: 12px;
            margin-bottom: 4px;
        }

        .account-link:hover {
            text-decoration: underline;
        }

        .table-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .table-header {
            padding: 16px 20px;
            border-bottom: 1px solid #e5e7eb;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .table-title {
            font-weight: 600;
            font-size: 14px;
            color: #03363d;
        }

        .results-count {
            font-size: 12px;
            color: #6b7280;
        }

        .table-wrapper {
            overflow: auto;
            max-height: 800px;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }

        thead {
            position: sticky;
            top: 0;
            background: #f9fafb;
            z-index: 10;
        }

        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 11px;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 2px solid #e5e7eb;
            white-space: nowrap;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #f3f4f6;
            font-size: 13px;
        }

        tr:hover {
            background: #f9fafb;
        }

        .frozen-col {
            position: sticky;
            left: 0;
            background: white;
            z-index: 5;
        }

        .frozen-col-1 { left: 0; }
        .frozen-col-2 { left: 120px; }
        .frozen-col-3 { left: 240px; }
        .frozen-col-4 { left: 360px; }

        thead .frozen-col {
            background: #f9fafb;
            z-index: 15;
        }

        .checkmark {
            text-align: center;
            color: #10b981;
            font-weight: 600;
        }

        .gong-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            background: #dbeafe;
            border-radius: 12px;
            font-size: 11px;
            color: #1e40af;
            cursor: pointer;
        }

        .gong-indicator:hover {
            background: #bfdbfe;
        }

        .gong-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }

        .gong-modal.show {
            display: flex;
        }

        .gong-modal-content {
            background: white;
            padding: 24px;
            border-radius: 8px;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
        }

        .gong-modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e5e7eb;
        }

        .gong-modal-title {
            font-weight: 700;
            font-size: 18px;
            color: #03363d;
        }

        .close-modal {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #6b7280;
        }

        .close-modal:hover {
            color: #03363d;
        }

        .gong-call {
            padding: 16px;
            margin-bottom: 12px;
            background: #f9fafb;
            border-radius: 6px;
            border-left: 3px solid #d1f470;
        }

        .gong-call-title {
            font-weight: 600;
            color: #03363d;
            margin-bottom: 8px;
        }

        .gong-call-meta {
            font-size: 12px;
            color: #6b7280;
            margin-bottom: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Product Penetration Dashboard - APAC</h1>
        <p class="subtitle">Mitch Young's Organization | Copilot & AAA Growth Opportunities</p>
    </div>

    <div class="filters-section">
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;">
            <div class="filter-group">
                <label class="filter-label">Account Name</label>
                <select id="filter-account" class="filter-select" multiple size="3"></select>
            </div>
            <div class="filter-group">
                <label class="filter-label">RVP</label>
                <select id="filter-rvp" class="filter-select" multiple size="3"></select>
            </div>
            <div class="filter-group">
                <label class="filter-label">Market Segment</label>
                <select id="filter-segment" class="filter-select" multiple size="3"></select>
            </div>
            <div class="filter-group">
                <label class="filter-label">ARR Band</label>
                <select id="filter-arr-band" class="filter-select" multiple size="3"></select>
            </div>
        </div>
        <div style="margin-top: 12px;">
            <button onclick="resetFilters()" style="padding: 8px 16px; background: #d1f470; border: none; border-radius: 6px; cursor: pointer; font-weight: 600;">Reset Filters</button>
        </div>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value" id="metric-accounts">0</div>
            <div class="metric-label">Accounts</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="metric-opps">0</div>
            <div class="metric-label">Opportunities</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="metric-arr">$0</div>
            <div class="metric-label">Total ARR</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="metric-pipeline">$0</div>
            <div class="metric-label">Pipeline ARR</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" id="metric-gong">0</div>
            <div class="metric-label">Gong Calls</div>
        </div>
    </div>

    <div class="insights-section" id="insights-container">
        <div class="insight-title" style="margin-bottom: 12px;">💡 AI-Powered Insights</div>
    </div>

    <div class="table-container">
        <div class="table-header">
            <div class="table-title">Account & Opportunity Details</div>
            <div class="results-count" id="results-count">0 results</div>
        </div>
        <div class="table-wrapper">
            <table id="data-table">
                <thead>
                    <tr>
                        <th class="frozen-col frozen-col-1">RVP</th>
                        <th class="frozen-col frozen-col-2">FLM</th>
                        <th class="frozen-col frozen-col-3">AE</th>
                        <th class="frozen-col frozen-col-4">Account Name</th>
                        <th>Market Segment</th>
                        <th>Account ARR</th>
                        <th>TOP 3K</th>
                        <th>Has Copilot?</th>
                        <th>Has AAA?</th>
                        <th>Has QA?</th>
                        <th>Has Forethought?</th>
                        <th>Opportunity Name</th>
                        <th>Stage</th>
                        <th>Type</th>
                        <th>Opp ARR</th>
                        <th>Close Date</th>
                        <th>VP Forecast</th>
                        <th>Gong Calls</th>
                    </tr>
                </thead>
                <tbody id="table-body">
                </tbody>
            </table>
        </div>
    </div>

    <div class="gong-modal" id="gong-modal">
        <div class="gong-modal-content">
            <div class="gong-modal-header">
                <div class="gong-modal-title">Gong Conversation Analysis</div>
                <button class="close-modal" onclick="closeGongModal()">&times;</button>
            </div>
            <div id="gong-modal-body"></div>
        </div>
    </div>

    <script>
        let allData = [];
        let gongData = {};
        let filteredData = [];

        // Load data
        fetch('dashboard_data.json')
            .then(res => res.json())
            .then(data => {
                allData = data.accounts;
                gongData = data.gong || {};
                initializeFilters();
                updateDisplay();
            });

        function initializeFilters() {
            // Populate filter dropdowns with unique values
            const accounts = [...new Set(allData.map(d => d.account_name))].sort();
            const rvps = [...new Set(allData.map(d => d.rvp))].filter(v => v).sort();
            const segments = [...new Set(allData.map(d => d.market_segment))].filter(v => v).sort();
            const arrBands = ['< $10K', '$10K - $50K', '$50K - $100K', '$100K - $500K', '$500K+'];

            populateSelect('filter-account', accounts);
            populateSelect('filter-rvp', rvps);
            populateSelect('filter-segment', segments);
            populateSelect('filter-arr-band', arrBands);

            // Add event listeners
            ['filter-account', 'filter-rvp', 'filter-segment', 'filter-arr-band'].forEach(id => {
                document.getElementById(id).addEventListener('change', updateDisplay);
            });
        }

        function populateSelect(id, values) {
            const select = document.getElementById(id);
            values.forEach(val => {
                const option = document.createElement('option');
                option.value = val;
                option.textContent = val;
                option.selected = true;
                select.appendChild(option);
            });
        }

        function getSelectedValues(id) {
            const select = document.getElementById(id);
            return Array.from(select.selectedOptions).map(opt => opt.value);
        }

        function resetFilters() {
            ['filter-account', 'filter-rvp', 'filter-segment', 'filter-arr-band'].forEach(id => {
                const select = document.getElementById(id);
                Array.from(select.options).forEach(opt => opt.selected = true);
            });
            updateDisplay();
        }

        function updateDisplay() {
            // Apply filters
            const selectedAccounts = getSelectedValues('filter-account');
            const selectedRvps = getSelectedValues('filter-rvp');
            const selectedSegments = getSelectedValues('filter-segment');
            const selectedArrBands = getSelectedValues('filter-arr-band');

            filteredData = allData.filter(row => {
                return selectedAccounts.includes(row.account_name) &&
                       (!row.rvp || selectedRvps.includes(row.rvp)) &&
                       (!row.market_segment || selectedSegments.includes(row.market_segment)) &&
                       selectedArrBands.includes(row.arr_band);
            });

            updateMetrics();
            updateInsights();
            updateTable();
        }

        function updateMetrics() {
            const uniqueAccounts = new Set(filteredData.map(d => d.account_id)).size;
            const uniqueOpps = new Set(filteredData.filter(d => d.opportunity_id).map(d => d.opportunity_id)).size;
            const totalArr = filteredData.reduce((sum, d) => sum + (d.account_arr || 0), 0);
            const pipelineArr = filteredData.filter(d => d.opportunity_id).reduce((sum, d) => sum + (d.opp_arr || 0), 0);
            const gongCalls = filteredData.filter(d => d.opportunity_id && gongData[d.opportunity_id]).length;

            document.getElementById('metric-accounts').textContent = uniqueAccounts.toLocaleString();
            document.getElementById('metric-opps').textContent = uniqueOpps.toLocaleString();
            document.getElementById('metric-arr').textContent = formatCurrency(totalArr);
            document.getElementById('metric-pipeline').textContent = formatCurrency(pipelineArr);
            document.getElementById('metric-gong').textContent = gongCalls.toLocaleString();
        }

        function updateInsights() {
            const container = document.getElementById('insights-container');
            container.innerHTML = '<div class="insight-title" style="margin-bottom: 12px;">💡 AI-Powered Insights</div>';

            // Insight 1: Top accounts without Copilot
            const noCopilot = filteredData.filter(d => !d.has_copilot).slice(0, 10);
            if (noCopilot.length > 0) {
                const insight = createInsight(
                    `${noCopilot.length} accounts without Copilot`,
                    'High-value expansion opportunity',
                    noCopilot
                );
                container.appendChild(insight);
            }

            // Insight 2: Active opps with Gong calls
            const oppsWithGong = filteredData.filter(d => d.opportunity_id && gongData[d.opportunity_id]);
            if (oppsWithGong.length > 0) {
                const insight = createInsight(
                    `${oppsWithGong.length} opportunities with recorded calls`,
                    'Active sales conversations tracked in Gong',
                    oppsWithGong
                );
                container.appendChild(insight);
            }
        }

        function createInsight(title, detail, accounts) {
            const div = document.createElement('div');
            div.className = 'insight';
            div.innerHTML = `
                <div class="insight-title">${title}</div>
                <div class="insight-detail">${detail}</div>
                <div class="insight-accounts">
                    ${accounts.map(a => `<a href="https://zendesk.lightning.force.com/${a.account_id}" target="_blank" class="account-link">${a.account_name}</a>`).join('')}
                </div>
            `;
            div.onclick = (e) => {
                if (e.target.tagName !== 'A') {
                    div.querySelector('.insight-accounts').classList.toggle('expanded');
                }
            };
            return div;
        }

        function updateTable() {
            const tbody = document.getElementById('table-body');
            tbody.innerHTML = '';

            const uniqueAccounts = new Set(filteredData.map(d => d.account_id)).size;
            const uniqueOpps = new Set(filteredData.filter(d => d.opportunity_id).map(d => d.opportunity_id)).size;
            document.getElementById('results-count').textContent = `${uniqueAccounts} accounts & ${uniqueOpps} opportunities`;

            filteredData.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="frozen-col frozen-col-1">${row.rvp || ''}</td>
                    <td class="frozen-col frozen-col-2">${row.flm || ''}</td>
                    <td class="frozen-col frozen-col-3">${row.ae || ''}</td>
                    <td class="frozen-col frozen-col-4">
                        <a href="https://zendesk.lightning.force.com/${row.account_id}" target="_blank" style="color: #0066cc; text-decoration: none;">
                            ${row.account_name}
                        </a>
                    </td>
                    <td>${row.market_segment || ''}</td>
                    <td>${formatCurrency(row.account_arr)}</td>
                    <td class="checkmark">${row.is_top_3000 ? '✓' : ''}</td>
                    <td class="checkmark">${row.has_copilot ? '✓' : ''}</td>
                    <td class="checkmark">${row.has_aaa ? '✓' : ''}</td>
                    <td class="checkmark">${row.has_qa ? '✓' : ''}</td>
                    <td class="checkmark">${row.has_forethought ? '✓' : ''}</td>
                    <td>${row.opp_name || ''}</td>
                    <td>${row.stage_name || ''}</td>
                    <td>${row.opp_type || ''}</td>
                    <td>${formatCurrency(row.opp_arr)}</td>
                    <td>${row.close_date || ''}</td>
                    <td>${row.vp_forecast || ''}</td>
                    <td>${row.opportunity_id && gongData[row.opportunity_id] ?
                        `<span class="gong-indicator" onclick="showGongModal('${row.opportunity_id}')">
                            🎙️ ${gongData[row.opportunity_id].call_count}
                        </span>` : ''}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function showGongModal(oppId) {
            const modal = document.getElementById('gong-modal');
            const body = document.getElementById('gong-modal-body');

            const gong = gongData[oppId];
            if (!gong) return;

            body.innerHTML = `
                <div style="margin-bottom: 16px;">
                    <strong>Total Calls:</strong> ${gong.call_count}
                </div>
                ${gong.all_calls.map(call => `
                    <div class="gong-call">
                        <div class="gong-call-title">${call.title || 'Untitled Call'}</div>
                        <div class="gong-call-meta">📅 ${call.started_at || 'Date unknown'}</div>
                        <div class="gong-call-meta">⏱️ ${call.duration || 'Duration unknown'}</div>
                        <div class="gong-call-meta">👥 ${call.participant_count || 0} participants</div>
                    </div>
                `).join('')}
            `;

            modal.classList.add('show');
        }

        function closeGongModal() {
            document.getElementById('gong-modal').classList.remove('show');
        }

        function formatCurrency(val) {
            if (!val) return '$0';
            if (val >= 1e9) return '$' + (val / 1e9).toFixed(1) + 'B';
            if (val >= 1e6) return '$' + (val / 1e6).toFixed(1) + 'M';
            if (val >= 1e3) return '$' + (val / 1e3).toFixed(1) + 'K';
            return '$' + val.toFixed(0);
        }

        // Close modal on outside click
        document.getElementById('gong-modal').addEventListener('click', (e) => {
            if (e.target.id === 'gong-modal') {
                closeGongModal();
            }
        });
    </script>
</body>
</html>
""";

    output_path = Path(__file__).parent / 'ai_penetration_dashboard.html'
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✓ Dashboard HTML generated: {output_path}")

if __name__ == '__main__':
    generate_html()

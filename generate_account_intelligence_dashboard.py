#!/usr/bin/env python3
"""
Generate interactive Account Intelligence Dashboard HTML.

Features:
- Account selector with search/filter
- AI buying signal scores with reasoning
- Role-specific action cards (AE, SDR, CSM, Partner, Marketing)
- Product adoption heatmap
- Opportunity pipeline
- Consolidated notes
- Gong call intelligence
"""
import json
from pathlib import Path
from datetime import datetime


def format_currency(value):
    """Format currency with K/M/B notation."""
    if value is None:
        return '$0'
    # Convert to float to handle string numbers from JSON
    try:
        value = float(value)
    except (TypeError, ValueError):
        return '$0'

    if value >= 1_000_000_000:
        return f'${value/1_000_000_000:.1f}B'
    elif value >= 1_000_000:
        return f'${value/1_000_000:.1f}M'
    elif value >= 1_000:
        return f'${value/1_000:.0f}K'
    else:
        return f'${value:.0f}'


def generate_html():
    """Generate the interactive HTML dashboard."""

    # Load data
    data_path = Path(__file__).parent / 'account_intelligence.json'
    if not data_path.exists():
        print(f"✗ Data file not found: {data_path}")
        print("  Run ./fetch_account_intelligence.py first")
        return

    with open(data_path) as f:
        data = json.load(f)

    accounts = data['accounts']

    # Compute metrics
    total_arr = sum(float(a['account_arr'] or 0) for a in accounts)
    total_opps = sum(len(a['opportunities']) for a in accounts)

    # Compute pipeline ARR (convert string values to float)
    pipeline_arr = 0
    for a in accounts:
        for o in a['opportunities']:
            arr_value = o.get('arr') or 0
            try:
                pipeline_arr += float(arr_value)
            except (TypeError, ValueError):
                pass

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>APAC Account Intelligence & Expansion | Mitch Young</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f9fafb;
            color: #1f2937;
            padding: 8px;
            font-size: 14px;
            line-height: 1.5;
        }}

        .header {{
            background: white;
            padding: 10px 16px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 8px;
        }}

        h1 {{
            font-size: 24px;
            font-weight: 700;
            color: #03363d;
            margin-bottom: 4px;
        }}

        .subtitle {{
            color: #6b7280;
            font-size: 13px;
        }}

        .metrics-bar {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-bottom: 8px;
        }}

        .metric-card {{
            background: white;
            padding: 8px 12px;
            border-radius: 6px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }}

        .metric-label {{
            font-size: 11px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .metric-value {{
            font-size: 22px;
            font-weight: 700;
            color: #03363d;
        }}

        .metric-value a {{
            color: #03363d;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: border-color 0.15s;
        }}

        .metric-value a:hover {{
            border-bottom-color: #d1f470;
        }}

        .main-layout {{
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 16px;
        }}

        .right-section {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .account-list {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            height: calc(100vh - 100px);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}

        .account-list-header {{
            padding: 6px 10px;
            border-bottom: 1px solid #e5e7eb;
        }}

        .search-box {{
            width: 100%;
            padding: 6px 8px;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            font-size: 11px;
            font-family: 'Inter', sans-serif;
        }}

        .search-box:focus {{
            outline: none;
            border-color: #03363d;
        }}

        .filter-section {{
            padding: 6px 10px;
            border-bottom: 1px solid #e5e7eb;
            background: #f9fafb;
        }}

        .filter-label {{
            font-size: 10px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
            display: block;
        }}

        .filter-checkbox {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin-bottom: 4px;
            font-size: 11px;
        }}

        .filter-checkbox input {{
            width: 14px;
            height: 14px;
            cursor: pointer;
        }}

        .filter-dropdown {{
            margin-bottom: 3px;
        }}

        .filter-dropdown select {{
            width: 100%;
            padding: 5px 8px;
            font-size: 11px;
            border: 1px solid #d1d5db;
            border-radius: 4px;
            background: white;
            cursor: pointer;
        }}

        .product-filter-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4px;
            margin-top: 6px;
        }}

        .product-filter-item {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 10px;
        }}

        .product-filter-item input {{
            width: 12px;
            height: 12px;
            cursor: pointer;
        }}

        .account-list-items {{
            overflow-y: auto;
            flex: 1;
        }}

        .account-item {{
            padding: 6px 10px;
            border-bottom: 1px solid #f3f4f6;
            cursor: pointer;
            transition: background 0.15s;
        }}

        .account-item:hover {{
            background: #f9fafb;
        }}

        .account-item.active {{
            background: #d1f470;
            border-left: 4px solid #03363d;
        }}

        .account-item-name {{
            font-size: 13px;
            font-weight: 600;
            color: #03363d;
            margin-bottom: 2px;
        }}

        .account-item-meta {{
            font-size: 11px;
            color: #6b7280;
        }}

        .account-detail {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            flex: 1;
            overflow-y: auto;
            padding: 32px;
        }}

        .account-detail-header {{
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e5e7eb;
        }}

        .account-name {{
            font-size: 24px;
            font-weight: 700;
            color: #03363d;
            margin-bottom: 8px;
        }}

        .account-meta-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 8px;
        }}

        .meta-item {{
            display: flex;
            flex-direction: column;
        }}

        .meta-label {{
            font-size: 11px;
            font-weight: 600;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}

        .meta-value {{
            font-size: 14px;
            font-weight: 600;
            color: #03363d;
        }}

        .buying-signal-card {{
            background: linear-gradient(135deg, #03363d 0%, #2c5f6b 100%);
            color: white;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 16px;
        }}

        .signal-score {{
            font-size: 36px;
            font-weight: 700;
            margin-bottom: 4px;
        }}

        .signal-label {{
            font-size: 12px;
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .signal-reasoning {{
            font-size: 12px;
            line-height: 1.4;
            opacity: 0.95;
        }}

        .section {{
            margin-bottom: 20px;
        }}

        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: #03363d;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .role-actions {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }}

        .role-action-card {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px;
        }}

        .role-action-card h4 {{
            font-size: 12px;
            font-weight: 700;
            color: #03363d;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
        }}

        .role-action-card ul {{
            list-style: none;
            padding: 0;
        }}

        .role-action-card li {{
            font-size: 13px;
            color: #374151;
            margin-bottom: 8px;
            padding-left: 4px;
        }}

        .product-grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 8px;
        }}

        .product-badge {{
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .product-badge.active {{
            background: #d1f470;
            color: #03363d;
        }}

        .product-badge.inactive {{
            background: #f3f4f6;
            color: #9ca3af;
        }}

        .opp-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .opp-card {{
            background: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
        }}

        .opp-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
        }}

        .opp-name {{
            font-weight: 600;
            color: #03363d;
            flex: 1;
        }}

        .opp-name a {{
            color: #03363d;
            text-decoration: none;
            border-bottom: 2px solid transparent;
            transition: border-color 0.15s;
        }}

        .opp-name a:hover {{
            border-bottom-color: #d1f470;
        }}

        .opp-arr {{
            font-size: 18px;
            font-weight: 700;
            color: #03363d;
        }}

        .opp-meta {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            font-size: 12px;
        }}

        .opp-meta-item {{
            display: flex;
            flex-direction: column;
        }}

        .opp-meta-label {{
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 2px;
        }}

        .opp-meta-value {{
            color: #03363d;
        }}

        .notes-section {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}

        .note-card {{
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 16px;
            border-radius: 4px;
        }}

        .note-card h5 {{
            font-size: 11px;
            font-weight: 700;
            color: #92400e;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }}

        .note-card p {{
            font-size: 13px;
            color: #78350f;
            line-height: 1.6;
        }}

        .gong-section {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 8px;
            padding: 20px;
        }}

        .gong-section h4 {{
            font-size: 14px;
            font-weight: 700;
            color: #065f46;
            margin-bottom: 12px;
        }}

        .gong-section p {{
            font-size: 13px;
            color: #064e3b;
            line-height: 1.6;
            margin-bottom: 12px;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .badge.green {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge.yellow {{
            background: #fef3c7;
            color: #92400e;
        }}

        .badge.red {{
            background: #fee2e2;
            color: #991b1b;
        }}

        .empty-state {{
            text-align: center;
            padding: 80px 40px;
            color: #9ca3af;
        }}

        .empty-state-icon {{
            font-size: 64px;
            margin-bottom: 16px;
        }}

        .empty-state-text {{
            font-size: 18px;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Account Intelligence Dashboard</h1>
        <p class="subtitle">APAC | Product Whitespace</p>
        <p class="subtitle" style="margin-top: 8px; font-size: 13px;">Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>

    <div class="main-layout">
        <div class="account-list">
            <div class="filter-section">
                <label class="filter-label">Filters</label>

                <div style="display: flex; gap: 12px; align-items: center;">
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filterTop3000">
                        <label for="filterTop3000">Top 3000 Only</label>
                    </div>
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filterARR10k">
                        <label for="filterARR10k">ARR > $10k</label>
                    </div>
                    <div class="filter-dropdown" style="margin-bottom: 0;">
                        <select id="filterHealth" style="width: 140px;">
                            <option value="">All Health</option>
                            <option value="Green">Green</option>
                            <option value="Yellow">Yellow</option>
                            <option value="Orange">Orange</option>
                            <option value="Red">Red</option>
                            <option value="Churning">Churning</option>
                        </select>
                    </div>
                </div>

                <div style="display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap;">
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filterWithoutOpp">
                        <label for="filterWithoutOpp">Without Opp</label>
                    </div>
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filterWithOpp">
                        <label for="filterWithOpp">With Opp</label>
                    </div>
                    <div class="filter-checkbox">
                        <input type="checkbox" id="filterWithOppNoAI">
                        <label for="filterWithOppNoAI">With Opp but no AI SKU</label>
                    </div>
                </div>

                <label class="filter-label" style="margin-top: 12px;">Team</label>
                <div class="filter-dropdown">
                    <select id="filterRVP">
                        <option value="">All RVPs</option>
                    </select>
                </div>
                <div class="filter-dropdown">
                    <select id="filterFLM">
                        <option value="">All FLMs</option>
                    </select>
                </div>
                <div class="filter-dropdown">
                    <select id="filterAE">
                        <option value="">All AEs</option>
                    </select>
                </div>

                <label class="filter-label" style="margin-top: 12px;">Without Product (Whitespace)</label>
                <div class="product-filter-grid">
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoCopilot" data-product="copilot">
                        <label for="filterNoCopilot">No Copilot</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoAAA" data-product="aaa">
                        <label for="filterNoAAA">No AAA</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoForethought" data-product="forethought">
                        <label for="filterNoForethought">No Forethought</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoAIExpert" data-product="ai_expert">
                        <label for="filterNoAIExpert">No AI Expert</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoUltimate" data-product="ultimate">
                        <label for="filterNoUltimate">No Ultimate</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoUltimateAR" data-product="ultimate_ar">
                        <label for="filterNoUltimateAR">No Ultimate AR</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoAAE" data-product="aae">
                        <label for="filterNoAAE">No AAE</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoQA" data-product="qa">
                        <label for="filterNoQA">No QA</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoWEM" data-product="wem">
                        <label for="filterNoWEM">No WEM</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoCC" data-product="contact_center">
                        <label for="filterNoCC">No CC</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoADPP" data-product="adpp">
                        <label for="filterNoADPP">No ADPP</label>
                    </div>
                    <div class="product-filter-item">
                        <input type="checkbox" id="filterNoProfServ" data-product="profserv">
                        <label for="filterNoProfServ">No ProfServ</label>
                    </div>
                </div>
            </div>

            <div class="account-list-header">
                <input type="text" class="search-box" id="searchBox" placeholder="Search accounts...">
            </div>

            <div class="account-list-items" id="accountListItems">
                <!-- Populated by JavaScript -->
            </div>
        </div>

        <div class="right-section">
            <div class="metrics-bar" id="metricsBar">
                <div class="metric-card">
                    <div class="metric-label">Account Selected</div>
                    <div class="metric-value" id="metricAccountName">—</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Account ARR</div>
                    <div class="metric-value" id="metricAccountARR">—</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Open Opportunities</div>
                    <div class="metric-value" id="metricOpps">—</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Pipeline ARR</div>
                    <div class="metric-value" id="metricPipelineARR">—</div>
                </div>
            </div>

            <div class="account-detail" id="accountDetail">
                <div class="empty-state">
                    <div class="empty-state-icon">👈</div>
                    <div class="empty-state-text">Select an account to view summary</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const accounts = {json.dumps(accounts, indent=2, default=str)};

        // Sort accounts by ARR descending (highest first)
        accounts.sort((a, b) => (b.account_arr || 0) - (a.account_arr || 0));

        let currentAccountIndex = null;
        let filteredAccounts = [...accounts];
        const translationCache = {{}};

        // Detect if text contains CJK characters
        function hasCJK(text) {{
            if (!text || typeof text !== 'string') return false;
            return /[一-鿿぀-ゟ゠-ヿ가-힯]/.test(text);
        }}

        // Simple translation using free API
        async function translateText(text) {{
            if (!text || !hasCJK(text)) return null;
            if (translationCache[text]) return translationCache[text];

            // Limit text length for API
            const maxLength = 500;
            const textToTranslate = text.length > maxLength ? text.substring(0, maxLength) + '...' : text;

            try {{
                // Detect language
                const hasHiragana = /[぀-ゟ]/.test(text);
                const hasKatakana = /[゠-ヿ]/.test(text);
                const hasHangul = /[가-힯]/.test(text);

                let sourceLang = 'auto';
                if (hasHiragana || hasKatakana) sourceLang = 'ja';
                else if (hasHangul) sourceLang = 'ko';
                else sourceLang = 'zh';

                const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${{sourceLang}}&tl=en&dt=t&q=${{encodeURIComponent(textToTranslate)}}`;
                const response = await fetch(url);
                const data = await response.json();

                if (data && data[0] && data[0][0] && data[0][0][0]) {{
                    const translated = data[0].map(item => item[0]).join('');
                    translationCache[text] = translated;
                    return translated;
                }}
            }} catch (e) {{
                console.warn('Translation failed:', e);
            }}

            return null;
        }}

        // Add translation on hover
        async function addTranslationToElement(element) {{
            if (element.dataset.translated) return; // Already processed

            const text = element.textContent;
            if (!hasCJK(text)) return;

            element.style.borderBottom = '1px dotted #6b7280';
            element.style.cursor = 'help';
            element.dataset.translated = 'pending';

            const translation = await translateText(text);
            if (translation) {{
                element.title = translation;
                element.dataset.translated = 'done';
            }}
        }}

        // Populate team dropdowns with cascading logic
        function populateTeamFilters() {{
            const selectedRVP = document.getElementById('filterRVP').value;
            const selectedFLM = document.getElementById('filterFLM').value;

            // Filter accounts based on current RVP/FLM selection
            let relevantAccounts = accounts;
            if (selectedRVP) {{
                relevantAccounts = relevantAccounts.filter(a => a.rvp === selectedRVP);
            }}
            if (selectedFLM) {{
                relevantAccounts = relevantAccounts.filter(a => a.flm === selectedFLM);
            }}

            // Get unique values
            const rvps = new Set();
            const flms = new Set();
            const aes = new Set();

            accounts.forEach(a => {{
                if (a.rvp) rvps.add(a.rvp);
            }});

            relevantAccounts.forEach(a => {{
                if (selectedRVP && a.rvp === selectedRVP && a.flm) {{
                    flms.add(a.flm);
                }} else if (!selectedRVP && a.flm) {{
                    flms.add(a.flm);
                }}

                if (a.ae) {{
                    aes.add(a.ae);
                }}
            }});

            // Populate RVP dropdown (always shows all)
            const rvpSelect = document.getElementById('filterRVP');
            const currentRVP = rvpSelect.value;
            rvpSelect.innerHTML = '<option value="">All RVPs</option>';
            Array.from(rvps).sort().forEach(rvp => {{
                const option = document.createElement('option');
                option.value = rvp;
                option.textContent = rvp;
                if (rvp === currentRVP) option.selected = true;
                rvpSelect.appendChild(option);
            }});

            // Populate FLM dropdown (filtered by RVP)
            const flmSelect = document.getElementById('filterFLM');
            const currentFLM = flmSelect.value;
            flmSelect.innerHTML = '<option value="">All FLMs</option>';
            Array.from(flms).sort().forEach(flm => {{
                const option = document.createElement('option');
                option.value = flm;
                option.textContent = flm;
                if (flm === currentFLM) option.selected = true;
                flmSelect.appendChild(option);
            }});

            // Populate AE dropdown (filtered by RVP + FLM)
            const aeSelect = document.getElementById('filterAE');
            const currentAE = aeSelect.value;
            aeSelect.innerHTML = '<option value="">All AEs</option>';
            Array.from(aes).sort().forEach(ae => {{
                const option = document.createElement('option');
                option.value = ae;
                option.textContent = ae;
                if (ae === currentAE) option.selected = true;
                aeSelect.appendChild(option);
            }});
        }}

        // Initialize
        populateTeamFilters();
        renderAccountList();

        // Filtering function
        function applyFilters() {{
            const searchQuery = document.getElementById('searchBox').value.toLowerCase();
            const filterTop3000 = document.getElementById('filterTop3000').checked;
            const filterARR10k = document.getElementById('filterARR10k').checked;
            const filterHealth = document.getElementById('filterHealth').value;
            const filterWithoutOpp = document.getElementById('filterWithoutOpp').checked;
            const filterWithOpp = document.getElementById('filterWithOpp').checked;
            const filterWithOppNoAI = document.getElementById('filterWithOppNoAI').checked;
            const filterRVP = document.getElementById('filterRVP').value;
            const filterFLM = document.getElementById('filterFLM').value;
            const filterAE = document.getElementById('filterAE').value;

            // Get all checked product filters
            const productFilters = Array.from(document.querySelectorAll('[data-product]'))
                .filter(cb => cb.checked)
                .map(cb => cb.getAttribute('data-product'));

            filteredAccounts = accounts.filter(a => {{
                // Search filter
                const matchesSearch = !searchQuery ||
                    a.account_name.toLowerCase().includes(searchQuery) ||
                    a.ae.toLowerCase().includes(searchQuery) ||
                    (a.segment || '').toLowerCase().includes(searchQuery);

                // Top 3000 filter
                const matchesTop3000 = !filterTop3000 || a.is_top_3000 === true;

                // ARR > $10k filter
                const matchesARR10k = !filterARR10k || (a.account_arr && a.account_arr > 10000);

                // Health filter
                const matchesHealth = !filterHealth || a.health_status === filterHealth;

                // Opportunity filters
                const hasOpp = a.opportunities && a.opportunities.some(opp => opp.opp_id);
                const matchesWithoutOpp = !filterWithoutOpp || !hasOpp;
                const matchesWithOpp = !filterWithOpp || hasOpp;

                // With Opp but no AI SKU filter
                let matchesWithOppNoAI = true;
                if (filterWithOppNoAI) {{
                    if (!hasOpp) {{
                        matchesWithOppNoAI = false;
                    }} else {{
                        // Check if any opp has AI products
                        const aiSkus = ['AI_Expert', 'Copilot', 'Ultimate', 'Ultimate_AR', 'Zendesk_AR', 'QA', 'WEM', 'Forethought'];
                        const hasAISku = a.opportunities.some(opp => {{
                            if (!opp.products) return false;
                            const oppProducts = opp.products.toLowerCase();
                            return aiSkus.some(sku => oppProducts.includes(sku.toLowerCase()));
                        }});
                        matchesWithOppNoAI = !hasAISku;
                    }}
                }}

                // Team filters
                const matchesRVP = !filterRVP || a.rvp === filterRVP;
                const matchesFLM = !filterFLM || a.flm === filterFLM;
                const matchesAE = !filterAE || a.ae === filterAE;

                // Product filters (account must NOT have the selected products)
                const matchesProducts = productFilters.length === 0 ||
                    productFilters.every(product => a.products[product] === false || a.products[product] === null);

                return matchesSearch && matchesTop3000 && matchesARR10k && matchesHealth && matchesWithoutOpp && matchesWithOpp && matchesWithOppNoAI && matchesRVP && matchesFLM && matchesAE && matchesProducts;
            }});

            renderAccountList();
        }}

        // Search functionality
        document.getElementById('searchBox').addEventListener('input', applyFilters);

        // Top 3000 filter
        document.getElementById('filterTop3000').addEventListener('change', applyFilters);

        // ARR > $10k filter
        document.getElementById('filterARR10k').addEventListener('change', applyFilters);

        // Health filter
        document.getElementById('filterHealth').addEventListener('change', applyFilters);

        // Opportunity filters
        document.getElementById('filterWithoutOpp').addEventListener('change', applyFilters);
        document.getElementById('filterWithOpp').addEventListener('change', applyFilters);
        document.getElementById('filterWithOppNoAI').addEventListener('change', applyFilters);

        // Team filters with cascading
        document.getElementById('filterRVP').addEventListener('change', () => {{
            // When RVP changes, reset FLM and AE, then repopulate
            document.getElementById('filterFLM').value = '';
            document.getElementById('filterAE').value = '';
            populateTeamFilters();
            applyFilters();
        }});

        document.getElementById('filterFLM').addEventListener('change', () => {{
            // When FLM changes, reset AE, then repopulate
            document.getElementById('filterAE').value = '';
            populateTeamFilters();
            applyFilters();
        }});

        document.getElementById('filterAE').addEventListener('change', applyFilters);

        // Product filters
        document.querySelectorAll('[data-product]').forEach(checkbox => {{
            checkbox.addEventListener('change', applyFilters);
        }});

        function renderAccountList() {{
            const container = document.getElementById('accountListItems');
            container.innerHTML = '';

            filteredAccounts.forEach((account, index) => {{
                const div = document.createElement('div');
                div.className = 'account-item';
                if (currentAccountIndex === index) {{
                    div.classList.add('active');
                }}

                div.innerHTML = `
                    <div class="account-item-name">${{account.account_name}}</div>
                    <div class="account-item-meta">
                        ${{formatCurrency(account.account_arr)}} ARR • ${{account.ae}}
                    </div>
                `;

                div.addEventListener('click', () => {{
                    currentAccountIndex = index;
                    renderAccountList();
                    renderAccountDetail(account);
                }});

                container.appendChild(div);
            }});
        }}

        function renderAccountDetail(account) {{
            const container = document.getElementById('accountDetail');

            // Update metrics bar with account-specific data
            const sfLink = `https://zendesk.lightning.force.com/lightning/r/Account/${{account.account_id}}/view`;
            document.getElementById('metricAccountName').innerHTML = `<a href="${{sfLink}}" target="_blank">${{account.account_name}}</a>`;
            document.getElementById('metricAccountARR').textContent = formatCurrency(account.account_arr);

            // Count only opportunities with valid IDs
            const validOpps = account.opportunities.filter(opp => opp.opp_id);
            document.getElementById('metricOpps').textContent = validOpps.length;

            // Calculate pipeline ARR for this account
            let pipelineARR = 0;
            account.opportunities.forEach(opp => {{
                pipelineARR += parseFloat(opp.arr || 0);
            }});
            document.getElementById('metricPipelineARR').textContent = formatCurrency(pipelineARR);

            // Build opportunities HTML (filter out NULL opportunity IDs)
            let oppsHtml = '';
            const validOpportunities = account.opportunities.filter(opp => opp.opp_id);

            if (validOpportunities.length > 0) {{
                oppsHtml = validOpportunities.map(opp => {{
                    const oppSfLink = `https://zendesk.lightning.force.com/lightning/r/Opportunity/${{opp.opp_id}}/view`;
                    return `
                    <div class="opp-card">
                        <div class="opp-header">
                            <div class="opp-name"><a href="${{oppSfLink}}" target="_blank">${{opp.opp_name}}</a></div>
                            <div class="opp-arr">${{formatCurrency(opp.arr)}}</div>
                        </div>
                        <div class="opp-meta">
                            <div class="opp-meta-item">
                                <span class="opp-meta-label">Stage</span>
                                <span class="opp-meta-value">${{opp.stage || 'N/A'}}</span>
                            </div>
                            <div class="opp-meta-item">
                                <span class="opp-meta-label">Type</span>
                                <span class="opp-meta-value">${{opp.type || 'N/A'}}</span>
                            </div>
                            <div class="opp-meta-item">
                                <span class="opp-meta-label">Close Date</span>
                                <span class="opp-meta-value">${{opp.close_date || 'N/A'}}</span>
                            </div>
                            <div class="opp-meta-item">
                                <span class="opp-meta-label">Days Open</span>
                                <span class="opp-meta-value">${{opp.days_open !== null && opp.days_open !== undefined ? opp.days_open + ' days' : 'N/A'}}</span>
                            </div>
                        </div>
                        <div style="margin-top: 12px; font-size: 12px; color: #6b7280;">
                            <strong>Products:</strong> ${{opp.products || 'N/A'}}
                        </div>
                    </div>
                `;
                }}).join('');
            }} else {{
                oppsHtml = '<p style="color: #9ca3af; font-style: italic;">No opp</p>';
            }}

            // Build notes HTML
            let notesHtml = '';
            const notes = [];
            if (account.notes.ae) notes.push({{ label: 'AE Notes', content: account.notes.ae }});
            if (account.notes.sdr) notes.push({{ label: 'SDR Notes', content: account.notes.sdr }});
            if (account.notes.se) notes.push({{ label: 'SE Notes', content: account.notes.se }});
            if (account.notes.orr) notes.push({{ label: 'ORR Notes', content: account.notes.orr }});
            if (account.notes.health_status) notes.push({{ label: 'Health Status Notes', content: account.notes.health_status }});
            if (account.notes.renewal) notes.push({{ label: 'Renewal Notes', content: account.notes.renewal }});

            if (notes.length > 0) {{
                notesHtml = notes.map(note => `
                    <div class="note-card">
                        <h5>${{note.label}}</h5>
                        <p>${{note.content}}</p>
                    </div>
                `).join('');
            }} else {{
                notesHtml = '<p style="color: #9ca3af; font-style: italic;">No notes available</p>';
            }}

            // Build Gong spotlight HTML
            let gongHtml = '';
            if (account.gong_spotlight.brief) {{
                // Parse key points array
                let keyPointsHtml = '';
                if (account.gong_spotlight.key_points) {{
                    try {{
                        const keyPointsArray = typeof account.gong_spotlight.key_points === 'string' ?
                            JSON.parse(account.gong_spotlight.key_points) : account.gong_spotlight.key_points;
                        keyPointsHtml = '<ul style="margin: 8px 0; padding-left: 20px;">' +
                            keyPointsArray.map(p => `<li>${{p}}</li>`).join('') + '</ul>';
                    }} catch (e) {{
                        keyPointsHtml = account.gong_spotlight.key_points;
                    }}
                }}

                // Parse next steps array
                let nextStepsHtml = '';
                if (account.gong_spotlight.next_steps) {{
                    try {{
                        const nextStepsArray = typeof account.gong_spotlight.next_steps === 'string' ?
                            JSON.parse(account.gong_spotlight.next_steps) : account.gong_spotlight.next_steps;
                        nextStepsHtml = '<ul style="margin: 8px 0; padding-left: 20px;">' +
                            nextStepsArray.map(s => `<li>${{s}}</li>`).join('') + '</ul>';
                    }} catch (e) {{
                        nextStepsHtml = account.gong_spotlight.next_steps;
                    }}
                }}

                gongHtml = `
                    <div class="gong-section">
                        <h4>🎙️ Latest Gong Call Spotlight</h4>
                        <p><strong>Brief:</strong> ${{account.gong_spotlight.brief}}</p>
                        ${{keyPointsHtml ? `<div><strong>Key Points:</strong> ${{keyPointsHtml}}</div>` : ''}}
                        ${{nextStepsHtml ? `<div><strong>Next Steps:</strong> ${{nextStepsHtml}}</div>` : ''}}
                    </div>
                `;
            }} else {{
                gongHtml = '<p style="color: #9ca3af; font-style: italic;">No Gong call data available</p>';
            }}

            // Build role actions HTML
            const roleActions = account.role_actions;
            const roleActionsHtml = `
                <div class="role-actions">
                    <div class="role-action-card">
                        <h4>AE Actions</h4>
                        <ul>${{roleActions.ae.length > 0 ? roleActions.ae.map(a => `<li>${{a}}</li>`).join('') : '<li style="color: #9ca3af;">No actions</li>'}}</ul>
                    </div>
                    <div class="role-action-card">
                        <h4>SDR Actions</h4>
                        <ul>${{roleActions.sdr.length > 0 ? roleActions.sdr.map(a => `<li>${{a}}</li>`).join('') : '<li style="color: #9ca3af;">No actions</li>'}}</ul>
                    </div>
                    <div class="role-action-card">
                        <h4>CSM Actions</h4>
                        <ul>${{roleActions.csm.length > 0 ? roleActions.csm.map(a => `<li>${{a}}</li>`).join('') : '<li style="color: #9ca3af;">No actions</li>'}}</ul>
                    </div>
                    <div class="role-action-card">
                        <h4>Partner Actions</h4>
                        <ul>${{roleActions.partner.length > 0 ? roleActions.partner.map(a => `<li>${{a}}</li>`).join('') : '<li style="color: #9ca3af;">No actions</li>'}}</ul>
                    </div>
                </div>
            `;

            // Build product badges (all 17+ products)
            const products = account.products;
            const productBadges = `
                <div class="product-grid">
                    <div class="product-badge ${{products.copilot ? 'active' : 'inactive'}}">Copilot</div>
                    <div class="product-badge ${{products.aaa ? 'active' : 'inactive'}}">AAA</div>
                    <div class="product-badge ${{products.forethought ? 'active' : 'inactive'}}">Forethought</div>
                    <div class="product-badge ${{products.ai_expert ? 'active' : 'inactive'}}">AI Expert</div>
                    <div class="product-badge ${{products.ultimate ? 'active' : 'inactive'}}">Ultimate</div>
                    <div class="product-badge ${{products.ultimate_ar ? 'active' : 'inactive'}}">Ultimate AR</div>
                    <div class="product-badge ${{products.aae ? 'active' : 'inactive'}}">AAE</div>
                    <div class="product-badge ${{products.qa ? 'active' : 'inactive'}}">QA</div>
                    <div class="product-badge ${{products.wem ? 'active' : 'inactive'}}">WEM</div>
                    <div class="product-badge ${{products.wfm ? 'active' : 'inactive'}}">WFM</div>
                    <div class="product-badge ${{products.contact_center ? 'active' : 'inactive'}}">CC</div>
                    <div class="product-badge ${{products.es ? 'active' : 'inactive'}}">ES</div>
                    <div class="product-badge ${{products.adpp ? 'active' : 'inactive'}}">ADPP</div>
                    <div class="product-badge ${{products.ela ? 'active' : 'inactive'}}">ELA</div>
                    <div class="product-badge ${{products.profserv ? 'active' : 'inactive'}}">ProfServ</div>
                    <div class="product-badge ${{products.suite ? 'active' : 'inactive'}}">Suite</div>
                    <div class="product-badge ${{products.talk ? 'active' : 'inactive'}}">Talk</div>
                </div>
            `;

            // Health badge color
            let healthBadge = '';
            if (account.health_status) {{
                const color = account.health_status === 'Green' ? 'green' : account.health_status === 'Yellow' ? 'yellow' : 'red';
                healthBadge = `<span class="badge ${{color}}">${{account.health_status}}</span>`;
            }}

            container.innerHTML = `
                <div class="account-detail-header">
                    <div class="account-name">${{account.account_name}}</div>
                    <div class="account-meta-grid">
                        <div class="meta-item">
                            <span class="meta-label">ARR</span>
                            <span class="meta-value">${{formatCurrency(account.account_arr)}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Segment</span>
                            <span class="meta-value">${{account.segment || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Industry</span>
                            <span class="meta-value">${{account.industry || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Health</span>
                            <span class="meta-value">${{healthBadge}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">AE</span>
                            <span class="meta-value">${{account.ae}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">SDR</span>
                            <span class="meta-value">${{account.sdr || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">CSM</span>
                            <span class="meta-value">${{account.csm || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Renewal Rep</span>
                            <span class="meta-value">${{account.renewal_rep || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Paid Seats</span>
                            <span class="meta-value">${{account.paid_seats ? account.paid_seats.toLocaleString() : 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">3rd Party Bot</span>
                            <span class="meta-value">${{account.products.third_party_ai || 'None'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Resale Partner</span>
                            <span class="meta-value">${{account.resale_partner || 'None'}}</span>
                        </div>
                        <div class="meta-item" style="visibility: hidden;"></div>
                        <div class="meta-item">
                            <span class="meta-label">Last Touch Date</span>
                            <span class="meta-value">${{account.last_touch.date ? new Date(account.last_touch.date).toLocaleDateString() : 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Last Touch Type</span>
                            <span class="meta-value">${{account.last_touch.type || 'N/A'}}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Last Touch Role</span>
                            <span class="meta-value">${{account.last_touch.role || 'N/A'}}</span>
                        </div>
                    </div>
                </div>

                <div class="buying-signal-card">
                    <div class="signal-score">${{account.gong_analysis.buying_signal_score}}/100</div>
                    <div class="signal-label">Buying Signal Score</div>
                    <div class="signal-reasoning">${{account.gong_analysis.buying_signal_reasoning}}</div>
                </div>

                <div class="section">
                    <div class="section-title">🎙️ Gong Intelligence</div>
                    ${{gongHtml}}
                </div>

                <div class="section">
                    <div class="section-title">🎯 Role-Specific Actions</div>
                    ${{roleActionsHtml}}
                </div>

                <div class="section">
                    <div class="section-title">📦 Product Adoption</div>
                    ${{productBadges}}
                </div>

                <div class="section">
                    <div class="section-title">💰 Open Opportunities (${{validOpportunities.length}})</div>
                    <div class="opp-list">
                        ${{oppsHtml}}
                    </div>
                </div>

                <div class="section">
                    <div class="section-title">📝 Team Notes</div>
                    <div class="notes-section">
                        ${{notesHtml}}
                    </div>
                </div>
            `;

            // Add translations to CJK text after rendering
            setTimeout(() => {{
                // Account name
                const accountNameEl = container.querySelector('.account-name');
                if (accountNameEl) addTranslationToElement(accountNameEl);

                // Gong brief, key points, next steps
                const gongTexts = container.querySelectorAll('.gong-section p, .gong-section li');
                gongTexts.forEach(el => addTranslationToElement(el));

                // Notes
                const noteTexts = container.querySelectorAll('.note-card p');
                noteTexts.forEach(el => addTranslationToElement(el));
            }}, 100);
        }}

        function formatCurrency(value) {{
            if (!value) return '0';
            if (value >= 1e9) return (value / 1e9).toFixed(1) + 'B';
            if (value >= 1e6) return (value / 1e6).toFixed(1) + 'M';
            if (value >= 1e3) return (value / 1e3).toFixed(0) + 'K';
            return value.toFixed(0);
        }}
    </script>
</body>
</html>
"""

    # Write to file
    output_path = Path(__file__).parent / 'account_intelligence_dashboard.html'
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✓ Dashboard generated: {output_path}")
    print(f"  - {len(accounts)} accounts")
    print(f"  Open with: open {output_path}")


def main():
    generate_html()


if __name__ == '__main__':
    main()

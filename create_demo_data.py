#!/usr/bin/env python3
"""
Create demo data for the AI Penetration Dashboard.
Uses static sample data to demonstrate dashboard functionality.
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Generate realistic demo data."""

    print("Generating demo data...")

    # Sample account names
    company_names = [
        "Acme Tech Solutions", "GlobalSoft Industries", "DataFlow Systems",
        "CloudVenture Corp", "Innovation Labs", "TechNova Group",
        "Digital Transform Co", "SmartScale Technologies", "FutureStack Inc",
        "AgileWorks Solutions", "NextGen Software", "Quantum Systems",
        "Velocity Tech", "Pinnacle Digital", "Horizon Cloud",
        "Summit Software", "Catalyst Solutions", "Momentum Tech",
        "Apex Digital", "Zenith Systems", "Prime Software",
        "Elite Cloud Solutions", "Alpha Tech Group", "Beta Innovations",
        "Gamma Digital", "Delta Systems", "Epsilon Software"
    ]

    segments = ['Enterprise', 'Mid-Market', 'SMB']
    flms = ['Sarah Chen', 'David Kim', 'Emma Wilson', 'James Lee', 'Maria Garcia']
    aes = ['Alex Thompson', 'Jordan Martinez', 'Taylor Brown', 'Casey Johnson', 'Morgan Davis',
           'Riley Anderson', 'Quinn Wilson', 'Cameron Moore', 'Avery Taylor', 'Parker White']

    stages = ['02 - Confirm Need', '03 - Solution Design', '04 - Vendor Selection',
              '05 - Negotiation', '06 - Commit']
    opp_types = ['New Business', 'Renewal', 'Expansion', 'Upsell']
    forecasts = ['Commit', 'Best Case', 'Pipeline']

    accounts = []
    account_id_counter = 1
    opp_id_counter = 1

    for company in company_names:
        # Account details
        account_arr = random.randint(15000, 750000)

        # Determine ARR band
        if account_arr < 10000:
            arr_band = '< $10K'
        elif account_arr < 50000:
            arr_band = '$10K - $50K'
        elif account_arr < 100000:
            arr_band = '$50K - $100K'
        elif account_arr < 500000:
            arr_band = '$100K - $500K'
        else:
            arr_band = '$500K+'

        # AI Product flags (weighted towards growth opportunity)
        has_copilot = random.random() < 0.3  # 30% have Copilot
        has_aaa = random.random() < 0.25     # 25% have AAA

        account_id = f"001PC{str(account_id_counter).zfill(12)}"
        account_id_counter += 1

        base_account = {
            'rvp': 'Mitch Young',
            'flm': random.choice(flms),
            'ae': random.choice(aes),
            'account_name': company,
            'account_id': account_id,
            'market_segment': random.choice(segments),
            'account_arr': account_arr,
            'arr_band': arr_band,
            'is_top_3000': account_arr > 100000,
            'has_copilot': has_copilot,
            'has_aaa': has_aaa,
            'has_qa': random.choice([True, False]),
            'has_forethought': random.choice([True, False]),
            'has_ultimate': account_arr > 50000,
        }

        # 70% of accounts have 1-2 opportunities
        if random.random() < 0.7:
            num_opps = random.randint(1, 2)
            for _ in range(num_opps):
                opp_id = f"006PC{str(opp_id_counter).zfill(12)}"
                opp_id_counter += 1

                opp_arr = random.randint(5000, min(account_arr, 200000))
                close_date = datetime.now() + timedelta(days=random.randint(10, 120))

                is_ai_opp = random.random() < 0.4  # 40% are AI opps

                opp_record = base_account.copy()
                opp_record.update({
                    'opportunity_id': opp_id,
                    'opp_name': f"{company} - {'AI Agent Expansion' if is_ai_opp else 'Platform Renewal'}",
                    'stage_name': random.choice(stages),
                    'opp_type': random.choice(opp_types),
                    'opp_arr': opp_arr,
                    'close_date': close_date.strftime('%Y-%m-%d'),
                    'vp_forecast': random.choice(forecasts),
                    'is_ai_opp': is_ai_opp,
                    'ae_notes': None,
                    'sdr_notes': None,
                    'orr_notes': None
                })
                accounts.append(opp_record)
        else:
            # Account without opportunities
            no_opp_record = base_account.copy()
            no_opp_record.update({
                'opportunity_id': None,
                'opp_name': None,
                'stage_name': None,
                'opp_type': None,
                'opp_arr': None,
                'close_date': None,
                'vp_forecast': None,
                'is_ai_opp': False,
                'ae_notes': None,
                'sdr_notes': None,
                'orr_notes': None
            })
            accounts.append(no_opp_record)

    print(f"✓ Generated {len(accounts)} account/opportunity records")

    # Simulate Gong data for some opportunities (30% of opps)
    gong_data = {}
    opps_with_data = [a for a in accounts if a['opportunity_id']]

    for opp in random.sample(opps_with_data, min(len(opps_with_data) // 3, 20)):
        opp_id = opp['opportunity_id']
        call_count = random.randint(1, 5)

        calls = []
        for i in range(call_count):
            days_ago = random.randint(1, 60)
            call_date = datetime.now() - timedelta(days=days_ago)

            call_titles = [
                "Discovery Call - AI Agent Use Cases",
                "Technical Deep Dive - Copilot Integration",
                "Executive Briefing - AI Strategy",
                "Demo Follow-up - AAA Features",
                "Pricing & Packaging Discussion"
            ]

            calls.append({
                'title': random.choice(call_titles),
                'started_at': call_date.strftime('%Y-%m-%d %H:%M:%S'),
                'duration': f"{random.randint(15, 60)} min",
                'participant_count': random.randint(2, 6),
                'call_url': f"https://app.gong.io/call?id=mock-{opp_id}-{i}"
            })

        # Sort by date descending
        calls.sort(key=lambda x: x['started_at'], reverse=True)

        gong_data[opp_id] = {
            'call_count': call_count,
            'most_recent': calls[0],
            'all_calls': calls
        }

    print(f"✓ Simulated Gong data for {len(gong_data)} opportunities")

    return accounts, gong_data

def main():
    try:
        accounts, gong_data = generate_demo_data()

        # Create output data
        data = {
            'accounts': accounts,
            'gong': gong_data,
            'fetched_at': datetime.now().isoformat(),
            'data_type': 'demo',
            'note': 'This is demo data for testing. Replace with real Snowflake data in production.'
        }

        # Save to JSON
        output_path = Path(__file__).parent / 'dashboard_data.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Demo data saved to {output_path}")
        print(f"  - {len(accounts)} total rows")
        print(f"  - {len(set(a['account_id'] for a in accounts))} unique accounts")
        print(f"  - {len([a for a in accounts if a['opportunity_id']])} opportunities")
        print(f"  - {len(gong_data)} opportunities with Gong calls")

        # Generate HTML
        import subprocess
        subprocess.run(['python', 'generate_dashboard.py'], cwd=Path(__file__).parent)

        print(f"\n✅ Dashboard ready! Open: ai_penetration_dashboard.html")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())

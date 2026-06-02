#!/usr/bin/env python3
"""
Fetch AI product penetration data from Snowflake with Gong conversation analysis.
"""
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from connections.snowflake.cli import query as snowflake_query
from connections.gong import GongCache

def fetch_penetration_data():
    """Fetch AI product penetration data from Snowflake."""

    sql = """
    select
        -- Account hierarchy
        rvp.name as rvp,
        flm.name as flm,
        ae.name as ae,
        a.name as account_name,
        a.account_id,

        -- Account details
        ra.market_segment_c as market_segment,
        a.total_arr_c as account_arr,
        case
            when a.total_arr_c < 10000 then '< $10K'
            when a.total_arr_c < 50000 then '$10K - $50K'
            when a.total_arr_c < 100000 then '$50K - $100K'
            when a.total_arr_c < 500000 then '$100K - $500K'
            else '$500K+'
        end as arr_band,
        a.is_top_3000_account_c as is_top_3000,

        -- AI Product flags
        a.has_copilot_c as has_copilot,
        a.has_aaa_c as has_aaa,
        a.has_qa_c as has_qa,
        a.has_forethought_c as has_forethought,
        a.has_ultimate_c as has_ultimate,

        -- Opportunity details
        o.opportunity_id,
        o.name as opp_name,
        o.stage_name,
        o.type as opp_type,
        o.total_arr_c as opp_arr,
        o.close_date,
        o.vp_deal_forecast_c as vp_forecast,

        -- AI Product opportunities
        case when o.name ilike '%copilot%' or o.name ilike '%ai agent%' then true else false end as is_ai_opp,

        -- Notes
        ae.notes_c as ae_notes,
        a.sdr_notes_c as sdr_notes,
        a.orr_notes_c as orr_notes

    from cleansed.salesforce.account_scd2 a
    left join cleansed.salesforce.user_scd2 ae on a.owner_id = ae.user_id and ae.valid_to_timestamp = '9999-12-31'
    left join cleansed.salesforce.user_role_scd2 ur on ae.user_role_id = ur.user_role_id and ur.valid_to_timestamp = '9999-12-31'
    left join functional.gtm_sales_ops.role_attributes ra on ur.developer_name = ra.role_c
    left join cleansed.salesforce.user_scd2 flm on ra.flm_user_id_c = flm.user_id and flm.valid_to_timestamp = '9999-12-31'
    left join cleansed.salesforce.user_scd2 rvp on ra.rvp_user_id_c = rvp.user_id and rvp.valid_to_timestamp = '9999-12-31'
    left join cleansed.salesforce.opportunity_scd2 o on a.account_id = o.account_id
        and o.valid_to_timestamp = '9999-12-31'
        and o.is_deleted = false
        and o.is_closed = false
        and o.stage_name not in ('00 - Lead', '01 - Qualify')

    where a.valid_to_timestamp = '9999-12-31'
        and a.is_deleted = false
        and rvp.name = 'Mitch Young'

    order by a.total_arr_c desc nulls last, a.name
    """

    print("Fetching penetration data from Snowflake...")
    df = snowflake_query(sql)
    print(f"✓ Fetched {len(df)} rows")

    return df

def fetch_gong_data(opportunity_ids):
    """Fetch Gong call data for opportunities."""
    if not opportunity_ids:
        return {}

    print(f"\nFetching Gong data for {len(opportunity_ids)} opportunities...")
    gong = GongCache()

    gong_data = {}
    for opp_id in opportunity_ids:
        calls = gong.get_calls_for_opportunity(opp_id)
        if calls:
            # Get summary of most recent call
            recent = calls[0]
            gong_data[opp_id] = {
                'call_count': len(calls),
                'most_recent': {
                    'date': recent.get('started_at'),
                    'title': recent.get('title'),
                    'duration': recent.get('duration'),
                    'participants': recent.get('participant_count', 0)
                },
                'all_calls': calls
            }

    print(f"✓ Found Gong data for {len(gong_data)} opportunities")
    return gong_data

def main():
    try:
        # Fetch penetration data
        df = fetch_penetration_data()

        # Get unique opportunity IDs for Gong lookup
        opp_ids = df[df['opportunity_id'].notna()]['opportunity_id'].unique().tolist()

        # Fetch Gong data
        gong_data = fetch_gong_data(opp_ids)

        # Convert to JSON-serializable format
        data = {
            'accounts': df.to_dict(orient='records'),
            'gong': gong_data,
            'fetched_at': str(pd.Timestamp.now('UTC'))
        }

        # Save to JSON
        output_path = Path(__file__).parent / 'dashboard_data.json'
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\n✓ Data saved to {output_path}")
        print(f"  - {len(df)} total rows")
        print(f"  - {df['account_id'].nunique()} unique accounts")
        print(f"  - {len(opp_ids)} opportunities")
        print(f"  - {len(gong_data)} opportunities with Gong calls")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    import pandas as pd
    main()

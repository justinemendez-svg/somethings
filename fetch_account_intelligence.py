#!/usr/bin/env python3
"""
Fetch comprehensive account intelligence: Snowflake data + AI-powered Gong analysis.

Combines your APAC pipeline query with deep call intelligence:
- Buying signal scoring (0-100)
- Competitor mentions
- MEDDPICC gap analysis
- Objection patterns
- Role-specific action items
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from connections.snowflake.cli import query as snowflake_query
from connections.gong import GongCache


def fetch_apac_pipeline():
    """Execute your exact Snowflake query with all account/opp details."""

    sql = """
WITH APAC_PIPELINE_ALL AS (
    SELECT
        CLOSE_YEAR_QUARTER,
        STAGE_2_PLUS_DATE_C,
        CREATED_DATE,
        CLOSEDATE,
        CRM_ACCOUNT_ID,
        CRM_OPPORTUNITY_ID,
        OPP_NAME,
        TYPE,
        VP_DEAL_FORECAST__C,
        PRODUCT_ARR_USD,
        STAGE_NAME,
        PRODUCT
    FROM FUNCTIONAL.GTM_SALES_OPS.GTMSI_CONSOLIDATED_PIPELINE_BOOKINGS
    WHERE SVP_NAME = 'Mitch Young'
      AND LEFT(STAGE_NAME, 2) IN ('00', '01', '02', '03', '04', '05', '06')
      AND OPPORTUNITY_IS_COMMISSIONABLE = TRUE
      AND CLOSEDATE >= '2026-01-01'
      AND DATE_LABEL = 'today'
),

TOTAL_BOOKING_OPPS AS (
    SELECT
        STAGE_2_PLUS_DATE_C,
        CREATED_DATE,
        CLOSEDATE,
        CLOSE_YEAR_QUARTER,
        CRM_ACCOUNT_ID,
        CRM_OPPORTUNITY_ID,
        OPP_NAME,
        VP_DEAL_FORECAST__C,
        TYPE,
        STAGE_NAME,
        PRODUCT_ARR_USD AS TOTAL_BOOKING_ARR
    FROM APAC_PIPELINE_ALL
    WHERE PRODUCT = 'Total Booking'
      AND PRODUCT_ARR_USD > 0
),

PRODUCT_LIST AS (
    SELECT
        CRM_OPPORTUNITY_ID,
        LISTAGG(PRODUCT, ', ') WITHIN GROUP (ORDER BY PRODUCT) AS PRODUCTS
    FROM APAC_PIPELINE_ALL
    WHERE PRODUCT NOT IN ('Total Booking')
      AND PRODUCT_ARR_USD > 0
    GROUP BY CRM_OPPORTUNITY_ID
),

PIPELINE_SUMMARY AS (
    SELECT
        t.STAGE_2_PLUS_DATE_C,
        t.CREATED_DATE,
        t.CLOSEDATE,
        t.CLOSE_YEAR_QUARTER,
        t.CRM_ACCOUNT_ID,
        t.CRM_OPPORTUNITY_ID,
        t.OPP_NAME,
        t.VP_DEAL_FORECAST__C,
        t.TYPE,
        t.STAGE_NAME,
        t.TOTAL_BOOKING_ARR,
        p.PRODUCTS
    FROM TOTAL_BOOKING_OPPS t
    LEFT JOIN PRODUCT_LIST p ON t.CRM_OPPORTUNITY_ID = p.CRM_OPPORTUNITY_ID
),

LATEST_ACCOUNT_SNAPSHOT AS (
    SELECT
        PRIMARY_RESALE_PARTNER_NAME,
        CRM_ACCOUNT_ID
    FROM FUNCTIONAL.PRODUCT_ANALYTICS.SALESFORCE_ACCOUNT_DAILY_SNAPSHOT
    WHERE SOURCE_SNAPSHOT_DATE = (
        SELECT MAX(SOURCE_SNAPSHOT_DATE)
        FROM FUNCTIONAL.PRODUCT_ANALYTICS.SALESFORCE_ACCOUNT_DAILY_SNAPSHOT
    )
),

GONG_CALLS AS (
    SELECT
        gg.OBJECT_ID,
        v.CALL_SPOTLIGHT_BRIEF,
        v.CALL_SPOTLIGHT_NEXT_STEPS,
        v.CALL_SPOTLIGHT,
        v.CALL_SPOTLIGHT_KEY_POINTS
    FROM CLEANSED.GONG.GONG_CALLS_BCV v
    LEFT JOIN CLEANSED.GONG.GONG_CONVERSATION_CONTEXTS_BCV gg
        ON v.CONVERSATION_KEY = gg.CONVERSATION_KEY
    WHERE v.CALL_SPOTLIGHT_BRIEF IS NOT NULL
      AND TRIM(v.CALL_SPOTLIGHT_BRIEF) <> ''
      AND gg.OBJECT_TYPE = 'account'
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY gg.OBJECT_ID
        ORDER BY v.PLANNED_START_DATETIME DESC
    ) = 1
),

GONG_ACCOUNT AS (
    SELECT
        OBJECT_ID AS CRM_ACCOUNT_ID,
        CALL_SPOTLIGHT_BRIEF AS ACCOUNT_CALL_SPOTLIGHT_BRIEF,
        CALL_SPOTLIGHT_NEXT_STEPS AS ACCOUNT_CALL_SPOTLIGHT_NEXT_STEPS,
        CALL_SPOTLIGHT AS ACCOUNT_CALL_SPOTLIGHT,
        CALL_SPOTLIGHT_KEY_POINTS AS ACCOUNT_CALL_SPOTLIGHT_KEY_POINTS
    FROM GONG_CALLS
)

SELECT
    a.MINUS1_NAME AS RVP_NAME,
    a.FLM_NAME,
    a.AE_NAME,
    a.CRM_ACCOUNT_ID,
    a.CRM_ACCOUNT_NAME,
    a.CRM_MARKET_SEGMENT,
    a.KEY_VERTICALS,
    a.CRM_EMPLOYEE_RANGE,
    a.CRM_HEALTH_STATUS,
    a.ARR_USD_CUSTOMER_CURRENT_DATE AS ACCOUNT_ARR,
    a.TOP_3000_FLAG,
    s.PRIMARY_RESALE_PARTNER_NAME,

    c_sdr.USER_NAME AS SDR_ASSIGNED,
    c_success.USER_NAME AS SUCCESS_OWNER,
    c_renewal.USER_NAME AS RENEWAL_REP,

    b.AE_NOTES_C,
    b.SDR_NOTES_C,
    b.SE_NOTES_C,
    b.ORR_NOTES_C,
    b.AE_HEALTH_STATUS_NOTES_C,
    b.RENEWAL_STATUS_NOTES_UPDATED_C,
    b.LAST_SALES_TOUCH_USER_ROLE_ON_ACC_BDR_C,
    b.LAST_SALES_TOUCH_DATE_TIME_C,
    b.LAST_SALES_TOUCH_TYPE_C,

    ga.ACCOUNT_CALL_SPOTLIGHT_BRIEF,
    ga.ACCOUNT_CALL_SPOTLIGHT_NEXT_STEPS,
    ga.ACCOUNT_CALL_SPOTLIGHT,
    ga.ACCOUNT_CALL_SPOTLIGHT_KEY_POINTS,

    a.THIRD_PARTY_AI_BOT,
    a.PAID_SEATS_CURRENT_DATE,

    a.CUSTOMER_HAS_OPEN_GROWTH_VECTORS_DEALS_CURRENT_DATE,
    a.CRM_IS_COPILOT_ACTIVATED,
    a.CUSTOMER_HAS_OPEN_COPILOT_DEALS_CURRENT_DATE,
    a.CRM_IS_AI_AGENTS_ADVANCED_ACTIVATED,
    a.CUSTOMER_HAS_OPEN_AI_AGENTS_ADVANCED_DEALS_CURRENT_DATE,
    a.WITH_FORETHOUGHT_CURRENT_DATE,
    a.WITH_AI_EXPERT_CURRENT_DATE,
    a.WITH_ULTIMATE_CURRENT_DATE,
    a.WITH_ULTIMATE_AR_CURRENT_DATE,
    a.WITH_AAE_PRODUCT_ANALYTICS_CURRENT_DATE,
    a.WITH_QA_CURRENT_DATE,
    a.WITH_WEM_CURRENT_DATE,
    a.WITH_WFM_CURRENT_DATE,
    a.WITH_CONTACT_CENTER_CURRENT_DATE,
    a.WITH_ES_CURRENT_DATE,
    a.WITH_ADPP_CURRENT_DATE,
    a.WITH_ELA_CURRENT_DATE,
    a.WITH_PROFSERV_CURRENT_DATE,
    a.WITH_SUITE_CURRENT_DATE,
    a.WITH_TALK_CURRENT_DATE,
    a.CUSTOMER_HAS_OPEN_DEALS_CURRENT_DATE,
    a.CUSTOMER_HAS_OPEN_AI_ALL_WEM_ALL_DEALS_CURRENT_DATE,

    p.CRM_OPPORTUNITY_ID,
    p.OPP_NAME,
    p.TOTAL_BOOKING_ARR,
    p.STAGE_NAME,
    p.TYPE,
    p.VP_DEAL_FORECAST__C,
    p.CLOSEDATE,
    CASE
        WHEN EXTRACT(MONTH FROM p.CLOSEDATE) IN (2, 5, 8, 11) THEN 'M1'
        WHEN EXTRACT(MONTH FROM p.CLOSEDATE) IN (3, 6, 9, 12) THEN 'M2'
        WHEN EXTRACT(MONTH FROM p.CLOSEDATE) IN (1, 4, 7, 10) THEN 'M3'
        ELSE NULL
    END AS CLOSE_MONTH,
    p.CLOSE_YEAR_QUARTER,
    p.STAGE_2_PLUS_DATE_C,
    p.CREATED_DATE,
    p.PRODUCTS

FROM FUNCTIONAL.GTM_SALES_OPS.PENETRATION_DASH a
LEFT JOIN DEV_CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV b
    ON a.CRM_ACCOUNT_ID = b.ID
   AND a.CRM_OWNER_ID = b.OWNER_ID
LEFT JOIN LATEST_ACCOUNT_SNAPSHOT s
    ON a.CRM_ACCOUNT_ID = s.CRM_ACCOUNT_ID
LEFT JOIN foundational.customer.dim_crm_users_daily_snapshot_bcv c_sdr
    ON b.SDR_ASSIGNED_C = c_sdr.CRM_USER_ID
LEFT JOIN foundational.customer.dim_crm_users_daily_snapshot_bcv c_success
    ON b.SUCCESS_OWNER_C = c_success.CRM_USER_ID
LEFT JOIN foundational.customer.dim_crm_users_daily_snapshot_bcv c_renewal
    ON b.RENEWAL_REP_C = c_renewal.CRM_USER_ID
LEFT JOIN PIPELINE_SUMMARY p
    ON a.CRM_ACCOUNT_ID = p.CRM_ACCOUNT_ID
LEFT JOIN GONG_ACCOUNT ga
    ON a.CRM_ACCOUNT_ID = ga.CRM_ACCOUNT_ID

WHERE a.SVP_NAME = 'Mitch Young'
  AND a.ARR_USD_CUSTOMER_CURRENT_DATE > 0
ORDER BY
    a.MINUS1_NAME,
    a.FLM_NAME,
    a.AE_NAME,
    a.ARR_USD_CUSTOMER_CURRENT_DATE DESC
    """

    print("Fetching APAC pipeline data from Snowflake...")
    df = snowflake_query(sql)
    print(f"✓ Fetched {len(df)} rows")
    print(f"  - {df['CRM_ACCOUNT_ID'].nunique()} unique accounts")

    return df


def analyze_account_gong_calls(gong_spotlight_data):
    """
    Analyze Gong call spotlight data to generate buying signal score and reasoning.

    Uses the Gong spotlight fields from Snowflake:
    - CALL_SPOTLIGHT_BRIEF
    - CALL_SPOTLIGHT_KEY_POINTS
    - CALL_SPOTLIGHT_NEXT_STEPS
    - CALL_SPOTLIGHT

    Returns dict with score (0-100) and reasoning.
    """

    # Check if we have any Gong data (handle None/NaN values)
    def is_valid_text(value):
        return value and isinstance(value, str) and value.strip()

    has_brief = is_valid_text(gong_spotlight_data.get('brief'))
    has_key_points = is_valid_text(gong_spotlight_data.get('key_points'))
    has_next_steps = is_valid_text(gong_spotlight_data.get('next_steps'))
    has_spotlight = is_valid_text(gong_spotlight_data.get('spotlight'))

    if not any([has_brief, has_key_points, has_next_steps, has_spotlight]):
        return {
            'buying_signal_score': 0,
            'buying_signal_reasoning': 'No Gong call data available for this account',
            'competitors': [],
            'meddpicc_gaps': [],
            'objections': [],
            'positive_signals': [],
            'risk_flags': [],
            'call_count': 0
        }

    # Combine all spotlight data for analysis (filter out None/NaN)
    def safe_str(value):
        return str(value) if value and isinstance(value, str) else ''

    combined_text = ' '.join(filter(None, [
        safe_str(gong_spotlight_data.get('brief')),
        safe_str(gong_spotlight_data.get('key_points')),
        safe_str(gong_spotlight_data.get('next_steps')),
        safe_str(gong_spotlight_data.get('spotlight'))
    ])).lower()

    # Analyze for buying signals
    signals = analyze_transcript_for_signals(combined_text)

    # Build reasoning from detected signals
    reasoning_parts = []

    if signals['positive_signals']:
        reasoning_parts.append(f"✅ Positive signals: {', '.join(signals['positive_signals'][:3])}")

    if signals['risk_flags']:
        reasoning_parts.append(f"⚠️ Risk factors: {', '.join(signals['risk_flags'][:2])}")

    if signals['competitors']:
        reasoning_parts.append(f"🔍 Competitors mentioned: {', '.join(set(signals['competitors'][:3]))}")

    # MEDDPICC analysis
    meddpicc = signals['meddpicc']
    meddpicc_present = sum([
        meddpicc['metrics'],
        meddpicc['economic_buyer'],
        meddpicc['decision_criteria'],
        meddpicc['decision_process'],
        meddpicc['paper_process'],
        meddpicc['champion'],
        meddpicc['competition']
    ])

    if meddpicc_present > 0:
        reasoning_parts.append(f"📋 MEDDPICC coverage: {meddpicc_present}/7 elements present")

    if signals['objections']:
        reasoning_parts.append(f"🚧 Objections detected: {', '.join(set(signals['objections']))}")

    # If no specific signals, provide generic reasoning
    if not reasoning_parts:
        if signals['buying_signal_score'] >= 50:
            reasoning_parts.append("Neutral engagement detected in recent call")
        else:
            reasoning_parts.append("Limited engagement signals in recent call")

    reasoning = ' | '.join(reasoning_parts)

    return {
        'buying_signal_score': signals['buying_signal_score'],
        'buying_signal_reasoning': reasoning,
        'competitors': list(set(signals['competitors'])),
        'meddpicc_gaps': [],  # Could enhance this later
        'objections': list(set(signals['objections'])),
        'positive_signals': signals['positive_signals'],
        'risk_flags': signals['risk_flags'],
        'call_count': 1  # We have one call's spotlight data
    }


def analyze_transcript_for_signals(transcript_text):
    """
    Analyze transcript text for buying signals, competitors, MEDDPICC, objections.

    This is a rule-based placeholder - production version would use LLM.
    """

    signals = {
        'buying_signal_score': 50,  # 0-100
        'positive_signals': [],
        'risk_flags': [],
        'competitors': [],
        'meddpicc': {
            'metrics': False,
            'economic_buyer': False,
            'decision_criteria': False,
            'decision_process': False,
            'paper_process': False,
            'champion': False,
            'competition': False
        },
        'objections': []
    }

    text_lower = transcript_text.lower()

    # Buying signals (positive)
    if any(phrase in text_lower for phrase in [
        'budget approved', 'legal review', 'security review',
        'procurement', 'contract', 'when can we start'
    ]):
        signals['buying_signal_score'] += 20
        signals['positive_signals'].append('Budget/legal engagement detected')

    if any(phrase in text_lower for phrase in [
        'executive', 'ceo', 'cfo', 'vp of', 'director of'
    ]):
        signals['buying_signal_score'] += 15
        signals['positive_signals'].append('Executive involvement')
        signals['meddpicc']['economic_buyer'] = True

    if any(phrase in text_lower for phrase in [
        'timeline', 'go live', 'implementation', 'rollout'
    ]):
        signals['buying_signal_score'] += 10
        signals['positive_signals'].append('Implementation planning')

    # Risk flags (negative)
    if any(phrase in text_lower for phrase in [
        'not sure', 'need to think', 'budget concerns', 'pricing is high',
        'competitors', 'looking at alternatives'
    ]):
        signals['buying_signal_score'] -= 15
        signals['risk_flags'].append('Hesitation or budget concerns')

    if 'postpone' in text_lower or 'delay' in text_lower or 'push out' in text_lower:
        signals['buying_signal_score'] -= 20
        signals['risk_flags'].append('Timeline delays mentioned')

    # Competitor detection (simple pattern matching)
    # Note: 'zendesk' removed since we ARE Zendesk
    competitor_patterns = [
        'intercom', 'freshdesk', 'salesforce', 'service now',
        'gorgias', 'helpscout', 'drift', 'ada', 'ultimate.ai'
    ]
    for comp in competitor_patterns:
        if comp in text_lower:
            signals['competitors'].append(comp.title())

    # MEDDPICC detection
    if 'metrics' in text_lower or 'roi' in text_lower or 'cost savings' in text_lower:
        signals['meddpicc']['metrics'] = True
    if 'decision criteria' in text_lower or 'evaluation' in text_lower:
        signals['meddpicc']['decision_criteria'] = True
    if 'approval process' in text_lower or 'sign off' in text_lower:
        signals['meddpicc']['decision_process'] = True
    if 'champion' in text_lower or 'advocate' in text_lower:
        signals['meddpicc']['champion'] = True

    # Objections
    objection_patterns = [
        ('pricing', r'(price|cost|expensive|budget)'),
        ('timing', r'(timing|timeline|too soon|not ready)'),
        ('technical', r'(integration|technical|complex|difficult)'),
        ('competitor', r'(already use|currently have|existing solution)')
    ]
    for obj_type, pattern in objection_patterns:
        if re.search(pattern, text_lower):
            signals['objections'].append(obj_type.title())

    # Clamp score to 0-100
    signals['buying_signal_score'] = max(0, min(100, signals['buying_signal_score']))

    return signals


def generate_role_actions(account_data, gong_analysis):
    """
    Generate role-specific action items based on account data and Gong analysis.

    Returns dict with keys: ae, sdr, csm, partner, marketing
    """

    actions = {
        'ae': [],
        'sdr': [],
        'csm': [],
        'partner': [],
        'marketing': []
    }

    # AE actions
    if gong_analysis['buying_signal_score'] > 70:
        actions['ae'].append('🔥 High buying intent - accelerate to close')
    if gong_analysis['competitors']:
        actions['ae'].append(f"⚠️ Competitor mentions: {', '.join(gong_analysis['competitors'][:3])}")
    if gong_analysis['risk_flags']:
        actions['ae'].append(f"🚨 Risk: {gong_analysis['risk_flags'][0]}")

    # SDR actions
    if not account_data.get('SDR_ASSIGNED'):
        actions['sdr'].append('📍 No SDR assigned - consider account coverage')
    if account_data.get('LAST_SALES_TOUCH_DATE_TIME_C'):
        # Check if last touch was >30 days ago
        actions['sdr'].append('📞 Schedule follow-up cadence')

    # CSM actions
    if not account_data.get('CRM_IS_COPILOT_ACTIVATED') and account_data.get('ACCOUNT_ARR', 0) > 100000:
        actions['csm'].append('💡 High-value account without Copilot - expansion opportunity')
    if account_data.get('CRM_HEALTH_STATUS') in ['Red', 'Yellow']:
        actions['csm'].append(f"⚠️ Account health: {account_data.get('CRM_HEALTH_STATUS')} - address immediately")

    # Partner actions
    if account_data.get('PRIMARY_RESALE_PARTNER_NAME'):
        actions['partner'].append(f"🤝 Partner: {account_data['PRIMARY_RESALE_PARTNER_NAME']}")
    elif account_data.get('ACCOUNT_ARR', 0) > 250000:
        actions['partner'].append('🎯 Large account without partner - potential for partner-led expansion')

    # Marketing actions
    if gong_analysis['buying_signal_score'] < 40:
        actions['marketing'].append('📧 Low engagement - trigger nurture campaign')
    if account_data.get('THIRD_PARTY_AI_BOT'):
        actions['marketing'].append(f"🤖 Using 3rd party AI: {account_data['THIRD_PARTY_AI_BOT']} - competitive positioning needed")

    return actions


def main():
    try:
        # 1. Fetch Snowflake data
        df = fetch_apac_pipeline()

        # 2. Group by account (one row per account with aggregated opps)
        print("\nGrouping data by account...")
        account_groups = df.groupby('CRM_ACCOUNT_ID')

        # 3. Build account-level intelligence
        print("\nAnalyzing accounts...")
        accounts = []

        for account_id, group_df in account_groups:
            account_row = group_df.iloc[0].to_dict()

            # Get all opportunities for this account
            opps = []
            for _, opp_row in group_df.iterrows():
                if opp_row['CRM_OPPORTUNITY_ID']:
                    # Calculate days open
                    stage2_date = opp_row['STAGE_2_PLUS_DATE_C']
                    created_date = opp_row['CREATED_DATE']
                    days_open = None

                    if stage2_date and not pd.isna(stage2_date):
                        days_open = (datetime.now().date() - pd.to_datetime(stage2_date).date()).days
                    elif created_date and not pd.isna(created_date):
                        days_open = (datetime.now().date() - pd.to_datetime(created_date).date()).days

                    opps.append({
                        'opp_id': opp_row['CRM_OPPORTUNITY_ID'],
                        'opp_name': opp_row['OPP_NAME'],
                        'arr': opp_row['TOTAL_BOOKING_ARR'],
                        'stage': opp_row['STAGE_NAME'],
                        'type': opp_row['TYPE'],
                        'close_date': str(opp_row['CLOSEDATE']) if opp_row['CLOSEDATE'] else None,
                        'close_month': opp_row['CLOSE_MONTH'],
                        'products': opp_row['PRODUCTS'],
                        'vp_forecast': opp_row['VP_DEAL_FORECAST__C'],
                        'days_open': days_open
                    })

            # Analyze Gong spotlight data from Snowflake
            gong_spotlight = {
                'brief': account_row['ACCOUNT_CALL_SPOTLIGHT_BRIEF'],
                'key_points': account_row['ACCOUNT_CALL_SPOTLIGHT_KEY_POINTS'],
                'next_steps': account_row['ACCOUNT_CALL_SPOTLIGHT_NEXT_STEPS'],
                'spotlight': account_row['ACCOUNT_CALL_SPOTLIGHT']
            }
            gong_analysis = analyze_account_gong_calls(gong_spotlight)

            # Generate role-specific actions
            role_actions = generate_role_actions(account_row, gong_analysis)

            # Build account intelligence object
            account_intel = {
                # Account basics
                'account_id': account_id,
                'account_name': account_row['CRM_ACCOUNT_NAME'],
                'account_arr': account_row['ACCOUNT_ARR'],
                'health_status': account_row['CRM_HEALTH_STATUS'],
                'segment': account_row['CRM_MARKET_SEGMENT'],
                'industry': account_row['KEY_VERTICALS'],
                'employee_range': account_row['CRM_EMPLOYEE_RANGE'],
                'paid_seats': account_row['PAID_SEATS_CURRENT_DATE'],
                'is_top_3000': account_row['TOP_3000_FLAG'],

                # Team assignments
                'rvp': account_row['RVP_NAME'],
                'flm': account_row['FLM_NAME'],
                'ae': account_row['AE_NAME'],
                'sdr': account_row['SDR_ASSIGNED'],
                'csm': account_row['SUCCESS_OWNER'],
                'renewal_rep': account_row['RENEWAL_REP'],

                # Product adoption (all 17+ products from your query)
                'products': {
                    'copilot': account_row['CRM_IS_COPILOT_ACTIVATED'],
                    'aaa': account_row['CRM_IS_AI_AGENTS_ADVANCED_ACTIVATED'],
                    'forethought': account_row['WITH_FORETHOUGHT_CURRENT_DATE'],
                    'ai_expert': account_row['WITH_AI_EXPERT_CURRENT_DATE'],
                    'ultimate': account_row['WITH_ULTIMATE_CURRENT_DATE'],
                    'ultimate_ar': account_row['WITH_ULTIMATE_AR_CURRENT_DATE'],
                    'aae': account_row['WITH_AAE_PRODUCT_ANALYTICS_CURRENT_DATE'],
                    'qa': account_row['WITH_QA_CURRENT_DATE'],
                    'wem': account_row['WITH_WEM_CURRENT_DATE'],
                    'wfm': account_row['WITH_WFM_CURRENT_DATE'],
                    'contact_center': account_row['WITH_CONTACT_CENTER_CURRENT_DATE'],
                    'es': account_row['WITH_ES_CURRENT_DATE'],
                    'adpp': account_row['WITH_ADPP_CURRENT_DATE'],
                    'ela': account_row['WITH_ELA_CURRENT_DATE'],
                    'profserv': account_row['WITH_PROFSERV_CURRENT_DATE'],
                    'suite': account_row['WITH_SUITE_CURRENT_DATE'],
                    'talk': account_row['WITH_TALK_CURRENT_DATE'],
                    'third_party_ai': account_row['THIRD_PARTY_AI_BOT']
                },

                # Notes
                'notes': {
                    'ae': account_row['AE_NOTES_C'],
                    'sdr': account_row['SDR_NOTES_C'],
                    'se': account_row['SE_NOTES_C'],
                    'orr': account_row['ORR_NOTES_C'],
                    'health_status': account_row['AE_HEALTH_STATUS_NOTES_C'],
                    'renewal': account_row['RENEWAL_STATUS_NOTES_UPDATED_C']
                },

                # Last touch
                'last_touch': {
                    'date': str(account_row['LAST_SALES_TOUCH_DATE_TIME_C']) if account_row['LAST_SALES_TOUCH_DATE_TIME_C'] else None,
                    'type': account_row['LAST_SALES_TOUCH_TYPE_C'],
                    'role': account_row['LAST_SALES_TOUCH_USER_ROLE_ON_ACC_BDR_C']
                },

                # Gong intelligence
                'gong_spotlight': {
                    'brief': account_row['ACCOUNT_CALL_SPOTLIGHT_BRIEF'],
                    'next_steps': account_row['ACCOUNT_CALL_SPOTLIGHT_NEXT_STEPS'],
                    'spotlight': account_row['ACCOUNT_CALL_SPOTLIGHT'],
                    'key_points': account_row['ACCOUNT_CALL_SPOTLIGHT_KEY_POINTS']
                },

                # AI analysis
                'gong_analysis': gong_analysis,

                # Opportunities
                'opportunities': opps,

                # Role-specific actions
                'role_actions': role_actions,

                # Partner
                'partner': account_row['PRIMARY_RESALE_PARTNER_NAME']
            }

            accounts.append(account_intel)

        print(f"✓ Processed {len(accounts)} accounts")

        # 5. Save to JSON
        output = {
            'accounts': accounts,
            'generated_at': datetime.now().isoformat(),
            'data_freshness': '30 days of Gong calls',
            'account_count': len(accounts),
            'total_arr': sum(a['account_arr'] or 0 for a in accounts)
        }

        output_path = Path(__file__).parent / 'account_intelligence.json'
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"\n✓ Account intelligence saved to {output_path}")
        print(f"  - {len(accounts)} accounts")
        print(f"  - {sum(len(a['opportunities']) for a in accounts)} opportunities")
        print(f"  - Total ARR: ${sum(a['account_arr'] or 0 for a in accounts):,.0f}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import pandas as pd
    main()

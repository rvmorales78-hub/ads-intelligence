import streamlit as st
import os, math, stripe
from datetime import date, timedelta, datetime, timezone
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cryptography.fernet import Fernet

from config import logger
from facebook_client import FacebookClient
from analyzer import (
    calculate_kpis,
    add_recommendations,
    generate_insights,
    get_objective_label,
    generate_detailed_insights,
    generate_star_campaign_analysis,
    calculate_weekly_trends,
    estimate_roi_potential,
    calculate_account_health_score,
    get_priority_actions,
)
from config import format_currency
from auth import logout
from database import (
    save_user_credentials, get_user_by_id, get_fb_accounts, add_fb_account, delete_fb_account,
    get_all_system_fb_accounts, save_daily_actions_summary, get_today_actions_summary, 
    get_last_week_actions, save_user_progress, get_user_progress_history, mark_action_as_completed,
    get_completed_actions, get_total_completed_actions
)

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable must be set for production.")

def get_fernet() -> Fernet:
    return Fernet(ENCRYPTION_KEY.encode())

def create_stripe_checkout_session(price_id: str, user_id: int) -> str:
    """Crea una sesión de checkout de Stripe y devuelve la URL."""
    try:
        # Verificación centralizada de todas las variables de entorno de Stripe
        api_key = os.getenv('STRIPE_API_KEY')
        domain_url = os.getenv('DOMAIN_URL')

        missing_vars = []
        if not api_key: missing_vars.append('STRIPE_API_KEY')
        if not domain_url: missing_vars.append('DOMAIN_URL')
        if not os.getenv('STRIPE_PRO_PRICE_ID'): missing_vars.append('STRIPE_PRO_PRICE_ID')
        if not os.getenv('STRIPE_ENTERPRISE_PRICE_ID'): missing_vars.append('STRIPE_ENTERPRISE_PRICE_ID')

        if missing_vars:
            error_msg = f"El sistema de pagos no está configurado. Faltan las siguientes variables de entorno: {', '.join(missing_vars)}. Por favor, contacta al administrador."
            logger.error(error_msg)
            st.error(error_msg)
            return ""

        stripe.api_key = api_key
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url=f'{domain_url}/?page=dashboard&payment=success',
            cancel_url=f'{domain_url}/?page=dashboard&payment=cancelled',
            client_reference_id=user_id,
            subscription_data={
                'metadata': {
                    'user_id': user_id
                }
            }
        )
        return checkout_session.url
    except Exception as e:
        logger.error(f"Error al crear sesión de Stripe: {e}")
        st.error(f"Error al contactar con el sistema de pagos: {e}")
        return ""

def encrypt_text(text: str) -> str:
    if not text:
        return ""
    try:
        f = get_fernet()
        return f.encrypt(text.encode()).decode()
    except Exception:
        return ""


def decrypt_text(encrypted: str) -> str:
    if not encrypted:
        return ""
    try:
        f = get_fernet()
        return f.decrypt(encrypted.encode()).decode()
    except Exception:
        return ""


# ========== CSS PREMIUM (compartido con app.py) ==========
DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { 
    background: #F0F2F5 !important; 
    color: #1c1e21; 
    font-family: 'Roboto', sans-serif;
    overflow-y: auto !important;  /* ← AGREGAR ESTA LÍNEA */
    height: auto !important;       /* ← AGREGAR ESTA LÍNEA */
}
h1,h2,h3,h4 { font-family: 'Segoe UI', 'Roboto', sans-serif; font-weight: 700; }

/* ---- HEADER BAR ---- */
.dash-header {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid #dddfe2;
    margin-bottom: 2rem;
    gap: 1rem;
}
.dash-logo {
    font-family: 'Segoe UI', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #1877F2;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.dash-logo .logo-mark {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    object-fit: contain;
    vertical-align: middle;
}
.dash-company {
    font-family: 'Segoe UI', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: #1c1e21;
}
.dash-sub {
    font-size: 0.85rem;
    color: #606770;
    margin-top: 0.2rem;
}

/* ---- PLAN BADGE ---- */
.plan-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.85rem;
    border-radius: 40px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.plan-basic      { background: #E4E6EB; border: 1px solid #ccd0d5; color: #1c1e21; }
.plan-pro        { background: #e7f3ff; border: 1px solid #1877F2; color: #1877F2; }
.plan-enterprise { background: #1877F2; border: 1px solid #166FE5; color: white; }

/* ---- METRIC CARDS ---- */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}
.metric-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.metric-card.green::after  { background: #31A24C; }
.metric-card.gold::after   { background: #F7B928; }
.metric-card.purple::after { background: #8A6AE0; }
.metric-card.blue::after   { background: #1877F2; }
.metric-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #606770;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
}
.metric-value.green  { color: #31A24C; }
.metric-value.gold   { color: #92400E; }
.metric-value.purple { color: #8A6AE0; }
.metric-value.blue   { color: #1877F2; }
.metric-value.red    { color: #dd3c10; }
.metric-value.white  { color: #1c1e21; }

/* ---- SECTION HEADERS ---- */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #1877F2;
    margin-bottom: 0.4rem;
}
.section-title {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #1c1e21;
    margin-bottom: 1.25rem;
}
.divider { border: none; border-top: 1px solid #dddfe2; margin: 2rem 0; }

/* ---- FILTER STRIP ---- */
.filter-strip {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}

/* ---- EXPANDER / CARD ---- */
.panel {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1c1e21;
    margin-bottom: 0.75rem;
}

/* ---- HEALTH INDICATORS ---- */
.health-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1rem 0;
}
.health-card {
    border-radius: 8px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.health-card.optimal  { background: #ECFDF5; border: 1px solid #A7F3D0; }
.health-card.warning  { background: #FFFBEB; border: 1px solid #FDE68A; }
.health-card.critical { background: #fae0e0; border: 1px solid #f5c0c0; }
.health-dot { font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; margin-bottom: 0.4rem; }
.health-dot.optimal  { color: #065F46; }
.health-dot.warning  { color: #92400E; }
.health-dot.critical { color: #dd3c10; }
.health-pct {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    line-height: 1;
}
.health-pct.optimal  { color: #065F46; }
.health-pct.warning  { color: #92400E; }
.health-pct.critical { color: #dd3c10; }
.health-amount { font-size: 0.78rem; color: #606770; margin-top: 0.25rem; }
.health-note {
    font-size: 0.65rem;
    color: #8a8d91;
    margin-top: 0.25rem;
}

/* ---- STAR CAMPAIGN ---- */
.star-card {
    border-radius: 8px;
    padding: 1.75rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}
.star-card.elite    { background: #ECFDF5; border: 1px solid #A7F3D0; }
.star-card.solid    { background: #e7f3ff; border: 1px solid #bde4ff; }
.star-card.improve  { background: #FFFBEB; border: 1px solid #FDE68A; }
.star-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.star-badge.elite   { color: #065F46; }
.star-badge.solid   { color: #1877F2; }
.star-badge.improve { color: #92400E; }
.star-name {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #1c1e21;
    margin-bottom: 0.3rem;
}
.star-obj { font-size: 0.82rem; color: #606770; }

/* ---- ROI BOX ---- */
.roi-box {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1rem;
}
.roi-box-title { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 0.85rem; font-weight: 700; color: #065F46; margin-bottom: 0.6rem; }
.roi-row { font-size: 0.85rem; color: #1c1e21; padding: 0.2rem 0; }
.roi-note { font-size: 0.72rem; color: #606770; margin-top: 0.5rem; }

/* ---- RECOMMENDATION BOX ---- */
.rec-box {
    background: #e7f3ff;
    border: 1px solid #bde4ff;
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 0.75rem;
}
.rec-title { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 0.9rem; font-weight: 700; color: #1877F2; margin-bottom: 0.4rem; }
.rec-text  { font-size: 0.85rem; color: #1c1e21; }

/* ---- ALERT BOX ---- */
.alert-box {
    background: #fae0e0;
    border: 1px solid #f5c0c0;
    border-left: 3px solid #dd3c10;
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.alert-title { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 0.82rem; font-weight: 700; color: #dd3c10; margin-bottom: 0.25rem; }
.alert-body  { font-size: 0.82rem; color: #1c1e21; }

/* ---- CAMPAIGN ROW ---- */
.camp-card {
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid;
}
.camp-card.high   { background: #fae0e0; border-color: #dd3c10; }
.camp-card.medium { background: #FFFBEB; border-color: #F7B928; }
.camp-card.low    { background: #ECFDF5; border-color: #31A24C; }
.camp-name { font-family: 'Segoe UI', 'Roboto', sans-serif; font-size: 0.95rem; font-weight: 700; color: #1c1e21; margin-bottom: 0.75rem; }
.camp-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; }
.camp-table td { padding: 0.3rem 0.5rem 0.3rem 0; color: #606770; vertical-align: top; }
.camp-table td strong { color: #1c1e21; display: block; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem; }

/* ---- PLAN SIDEBAR ---- */
.plan-panel {
    border-radius: 8px;
    padding: 1.25rem;
    margin-top: 1rem;
}
.plan-panel.basic      { background: #E4E6EB; border: 1px solid #ccd0d5; }
.plan-panel.pro        { background: #e7f3ff; border: 1px solid #bde4ff; }
.plan-panel.enterprise { background: #e7f3ff; border: 1px solid #bde4ff; }
.plan-name {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1c1e21;
    margin-bottom: 0.75rem;
}
.plan-item { font-size: 0.8rem; color: #606770; padding: 0.22rem 0; }
.plan-item.ok  { color: #065F46; }
.plan-item.off { color: #8a8d91; }

/* ---- SCORE BANNER ---- */
.score-banner {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.5rem;
    display: grid;
    grid-template-columns: 110px 1px 1fr 180px;
    align-items: center;
    gap: 2rem;
}
.score-num {
    font-size: 3.5rem;
    font-weight: 900;
    line-height: 1;
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    text-align: center;
}
.score-grade {
    font-size: 1rem;
    font-weight: 700;
    text-align: center;
    margin-top: 0.1rem;
}
.score-label {
    font-size: 0.62rem;
    color: #8a8d91;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    text-align: center;
    margin-top: 0.3rem;
}
.score-sep { background: #dddfe2; height: 100%; }
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.68rem;
    color: #606770;
    margin-bottom: 0.2rem;
}
.score-bar-track {
    background: #E4E6EB;
    border-radius: 4px;
    height: 4px;
    margin-bottom: 0.6rem;
}
.score-bar-fill { border-radius: 4px; height: 4px; }

/* ---- KPI GRID 8 ---- */
.kpi-grid-8 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.kpi-gold::after   { background: #F7B928; }
.kpi-card.kpi-blue::after   { background: #1877F2; }
.kpi-card.kpi-purple::after { background: #8A6AE0; }
.kpi-card.kpi-green::after  { background: #31A24C; }
.kpi-card.kpi-red::after    { background: #dd3c10; }
.kpi-card.kpi-amber::after  { background: #F7B928; }
.kpi-tag {
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #606770;
    margin-bottom: 0.4rem;
}
.kpi-val {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    line-height: 1;
}
.kpi-val.kpi-gold   { color: #92400E; }
.kpi-val.kpi-blue   { color: #1877F2; }
.kpi-val.kpi-purple { color: #A890F0; }
.kpi-val.kpi-green  { color: #31A24C; }
.kpi-val.kpi-red    { color: #dd3c10; }
.kpi-val.kpi-amber  { color: #92400E; }
.kpi-val.kpi-white  { color: #1c1e21; }
.kpi-sub { font-size: 0.67rem; color: #8a8d91; margin-top: 0.35rem; }

/* ---- CHART SECTION ---- */
.chart-section {
    background: #FFFFFF;
    border: 1px solid #dddfe2;
    border-radius: 8px;
    padding: 1.25rem 1.5rem;
}
.chart-title {
    font-family: 'Segoe UI', 'Roboto', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1c1e21;
    margin-bottom: 0.25rem;
}
.chart-subtitle { font-size: 0.72rem; color: #606770; margin-bottom: 0.75rem; }

/* ---- PRIORITY QUEUE ---- */
.pq-item {
    border-radius: 0 12px 12px 0;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    display: grid;
    grid-template-columns: 42px 1fr auto;
    gap: 0.85rem;
    align-items: start;
}
.pq-num {
    font-size: 0.58rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.15rem;
    text-align: center;
}
.pq-icon { font-size: 1.15rem; line-height: 1; text-align: center; }
.pq-title { font-size: 0.875rem; font-weight: 700; color: #1c1e21; margin-bottom: 0.2rem; }
.pq-detail { font-size: 0.76rem; color: #606770; margin-bottom: 0.3rem; }
.pq-action { font-size: 0.76rem; color: #1c1e21; }
.pq-badge {
    font-size: 0.6rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 20px;
    padding: 0.2rem 0.6rem;
    white-space: nowrap;
    align-self: start;
}

/* ---- FREQUENCY MAP ---- */
.freq-row {
    border-radius: 6px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.5rem;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 1rem;
    align-items: center;
}
.freq-name { font-size: 0.84rem; font-weight: 600; color: #1c1e21; }
.freq-badge {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-radius: 20px;
    padding: 0.1rem 0.5rem;
    border: 1px solid;
    margin-left: 0.6rem;
}
.freq-bar-track { background: #E4E6EB; border-radius: 4px; height: 4px; margin-top: 0.5rem; }
.freq-val { font-size: 1.3rem; font-weight: 800; line-height: 1; }
.freq-sub { font-size: 0.67rem; color: #606770; margin-top: 0.15rem; }

/* ---- CAMP CARD V2 ---- */
.camp-v2 {
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.6rem;
}
.camp-v2-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 0.75rem;
}
.camp-v2-metric { }
.camp-v2-lbl { font-size: 0.63rem; text-transform: uppercase; letter-spacing: 0.1em; color: #606770; margin-bottom: 0.2rem; }
.camp-v2-val { font-size: 1.05rem; font-weight: 700; color: #1c1e21; }
.camp-v2-sub { font-size: 0.67rem; color: #8a8d91; margin-top: 0.1rem; }

/* ---- BENCHMARK TABLE ---- */
.bench-table { width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-top: 0.5rem; }
.bench-table th {
    font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.1em;
    color: #606770; font-weight: 600;
    padding: 0.4rem 0.75rem; text-align: left;
    border-bottom: 1px solid #dddfe2;
}
.bench-table td { padding: 0.5rem 0.75rem; color: #1c1e21; border-bottom: 1px solid #F0F2F5; }
.bench-table tr:last-child td { border-bottom: none; }
.bench-ok   { color: #31A24C !important; font-weight: 600; }
.bench-warn { color: #92400E !important; font-weight: 600; }
.bench-bad  { color: #dd3c10 !important; font-weight: 600; }

/* ---- STREAMLIT OVERRIDES ---- */
.stButton > button {
    background: #1877F2 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Roboto', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: background-color 0.2s !important;
}
.stButton > button:hover { background: #166FE5 !important; }
.stExpander { background: #FFFFFF !important; border: 1px solid #dddfe2 !important; border-radius: 8px !important; }
div[data-testid="stExpander"] > div:first-child { border-radius: 8px !important; }
.stDateInput input, .stTextInput input, .stSelectbox select {
    background: #FFFFFF !important;
    border: 1px solid #ccd0d5 !important;
    color: #1c1e21 !important;
    border-radius: 6px !important;
}
.stRadio label { color: #1c1e21 !important; }
.stMetric label { color: #606770 !important; font-size: 0.75rem !important; }
.stMetric [data-testid="metric-container"] > div:nth-child(2) { color: #1c1e21 !important; }
div[data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #dddfe2 !important; }

section.main > div {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 1.5rem;
    overflow-y: visible !important;  /* ← AGREGAR */
    height: auto !important;          /* ← AGREGAR */
}

/* Fix scroll */
.block-container {
    overflow-y: visible !important;
    height: auto !important;
    padding-bottom: 3rem !important;
}

.main > div {
    overflow-y: visible !important;
}
</style>
"""


def check_plan_limits(df: pd.DataFrame, plan: str, date_range_days: int):
    plan = plan.lower() if plan else 'basic'
    limits = {
        'basic':      {'max_ads': 1,      'max_days': 30,  'can_export': False, 'can_see_alerts': False},
        'pro':        {'max_ads': 20,     'max_days': 90,  'can_export': True,  'can_see_alerts': True},
        'enterprise': {'max_ads': 999999, 'max_days': 365, 'can_export': True,  'can_see_alerts': True}
    }
    limit = limits.get(plan, limits['basic'])

    if len(df) > limit['max_ads']:
        st.warning(f"⚠️ Tu plan {plan.upper()} muestra solo los {limit['max_ads']} mejores anuncios")
        df = df.nlargest(limit['max_ads'], 'spend')

    if date_range_days > limit['max_days']:
        st.warning(f"⚠️ Tu plan {plan.upper()} permite máximo {limit['max_days']} días de historial")

    return df, limit




def get_objective_name(objective_code: str) -> str:
    objective_map = {
        'APP_INSTALLS': 'Instalaciones de App', 'BRAND_AWARENESS': 'Reconocimiento de Marca',
        'CONVERSIONS': 'Conversiones', 'EVENT_RESPONSES': 'Respuestas a Evento',
        'LEAD_GENERATION': 'Generación de Leads', 'LINK_CLICKS': 'Clics en Enlaces',
        'MESSAGES': 'Mensajes', 'OFFER_CLAIMS': 'Canjes de Oferta',
        'OUTCOME_ENGAGEMENT': 'Engagement', 'OUTCOME_TRAFFIC': 'Tráfico',
        'PAGE_LIKES': 'Me Gusta de Página', 'POST_ENGAGEMENT': 'Engagement en Post',
        'PRODUCT_CATALOG_SALES': 'Ventas de Catálogo', 'REACH': 'Alcance',
        'STORE_VISITS': 'Visitas a Tienda', 'VIDEO_VIEWS': 'Vistas de Video',
        'UNKNOWN': 'No especificado'
    }
    return objective_map.get(str(objective_code).upper(), str(objective_code))


def render_performance_table(df: pd.DataFrame, plan: str, plan_limits: dict):
    display_cols = [c for c in ['adset_name', 'campaign_name', 'objective', 'spend', 'roas', 'ctr', 'cpc'] if c in df.columns]
    if plan_limits['can_see_alerts'] and 'recommendation' in df.columns:
        display_cols.append('recommendation')

    display_df = df[[c for c in display_cols if c in df.columns]].copy()

    if 'roas' in display_df.columns and df['roas'].fillna(0).sum() == 0:
        display_df = display_df.drop(columns=['roas'])
        st.info('💡 No hay datos de conversiones. ROAS no disponible.')

    if 'objective' in display_df.columns:
        display_df['objective'] = display_df['objective'].apply(get_objective_label)

    def color_roas(val):
        if isinstance(val, (int, float)):
            if val >= 3:   return 'background-color: rgba(100,220,150,0.2); color: #64DC96'
            elif val >= 1.5: return 'background-color: rgba(251,191,36,0.2); color: #FBbf24'
            elif val > 0:  return 'background-color: rgba(252,129,129,0.2); color: #FC8181'
        return ''

    def color_ctr(val):
        if isinstance(val, (int, float)):
            if val >= 2:   return 'color: #64DC96; font-weight: 500'
            elif val >= 1: return 'color: #FBbf24'
            elif val > 0:  return 'color: #FC8181'
        return ''

    format_dict = {'spend': '${:.2f}', 'roas': '{:.2f}x', 'ctr': '{:.2f}%', 'cpc': '${:.2f}'}
    for col, fmt in format_dict.items():
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: fmt.format(x) if pd.notna(x) else 'N/A')

    rename_map = {
        'adset_name': 'Anuncio', 'campaign_name': 'Campaña', 'objective': 'Objetivo', 'spend': 'Gasto',
        'roas': 'ROAS', 'ctr': 'CTR', 'cpc': 'CPC', 'recommendation': 'Recomendación'
    }
    display_df = display_df.rename(columns=rename_map)

    styled = display_df.style
    if 'ROAS' in display_df.columns:
        roas_numeric = df['roas'] if 'roas' in df.columns else []
        styled = styled.apply(lambda x: [color_roas(val) for val in roas_numeric], subset=['ROAS'])
    if 'CTR' in display_df.columns:
        ctr_numeric = df['ctr'] if 'ctr' in df.columns else []
        styled = styled.apply(lambda x: [color_ctr(val) for val in ctr_numeric], subset=['CTR'])

    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        good_roas = len(df[df['roas'] >= 2]) if 'roas' in df.columns else 0
        st.metric("ROAS > 2x", good_roas)
    with col2:
        bad_roas = len(df[(df['roas'] < 1) & (df['roas'] > 0)]) if 'roas' in df.columns else 0
        st.metric("ROAS < 1x", bad_roas)
    with col3:
        no_conversions = len(df[df['roas'] == 0]) if 'roas' in df.columns else 0
        st.metric("Sin conversiones", no_conversions)

    if not plan_limits['can_see_alerts']:
        st.markdown("""
        <div style="background:rgba(138,106,224,0.07); border:1px solid rgba(138,106,224,0.18);
             border-radius:12px; padding:1rem; font-size:0.82rem; color:rgba(232,230,240,0.55); margin-top:1rem;">
            ✦ Mejora a <strong style="color:#A890F0;">PRO</strong> o <strong style="color:#C9A84C;">ENTERPRISE</strong>
            para ver recomendaciones personalizadas por anuncio.
        </div>
        """, unsafe_allow_html=True)


def render_health_indicator(df: pd.DataFrame):
    """Indicador de salud basado en ROAS (si existe) o en CTR/CPC (si no hay conversiones)"""

    if 'spend' not in df.columns:
        return

    total_spend = df['spend'].sum()
    if total_spend == 0:
        return

    has_roas_data = 'roas' in df.columns and df['roas'].fillna(0).sum() > 0

    st.markdown('<div class="section-label">Inversión</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Salud de la inversión</div>', unsafe_allow_html=True)

    if has_roas_data:
        healthy = df[df['roas'] >= 2]['spend'].sum()
        warning = df[(df['roas'] >= 1) & (df['roas'] < 2)]['spend'].sum()
        critical = df[df['roas'] < 1]['spend'].sum()

        healthy_pct = (healthy / total_spend) * 100
        warning_pct = (warning / total_spend) * 100
        critical_pct = (critical / total_spend) * 100

        st.markdown(f"""
        <div class="health-grid">
            <div class="health-card optimal">
                <div class="health-dot optimal">🟢 ROAS óptimo (≥2x)</div>
                <div class="health-pct optimal">{healthy_pct:.0f}%</div>
                <div class="health-amount">${healthy:,.0f}</div>
            </div>
            <div class="health-card warning">
                <div class="health-dot warning">🟡 ROAS medio (1-2x)</div>
                <div class="health-pct warning">{warning_pct:.0f}%</div>
                <div class="health-amount">${warning:,.0f}</div>
            </div>
            <div class="health-card critical">
                <div class="health-dot critical">🔴 ROAS bajo (&lt;1x)</div>
                <div class="health-pct critical">{critical_pct:.0f}%</div>
                <div class="health-amount">${critical:,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        if 'ctr' not in df.columns:
            return

        def get_ctr_benchmark(row):
            objective = str(row.get('objective', '')).upper()
            benchmarks = {
                'TRÁFICO': 1.5,
                'ENGAGEMENT': 1.2,
                'LEADS': 1.8,
                'CONVERSIONES': 1.3,
                'RECONOCIMIENTO': 0.8,
                'VIDEO': 1.2,
                'DEFAULT': 1.0
            }
            return benchmarks.get(objective, benchmarks['DEFAULT'])

        def classify_ctr(row):
            ctr = row.get('ctr', 0)
            benchmark = get_ctr_benchmark(row)
            if ctr >= benchmark * 2:
                return 'excelente'
            elif ctr >= benchmark:
                return 'bueno'
            else:
                return 'bajo'

        df['ctr_quality'] = df.apply(classify_ctr, axis=1)

        excelente = df[df['ctr_quality'] == 'excelente']['spend'].sum()
        bueno = df[df['ctr_quality'] == 'bueno']['spend'].sum()
        bajo = df[df['ctr_quality'] == 'bajo']['spend'].sum()

        excelente_pct = (excelente / total_spend) * 100
        bueno_pct = (bueno / total_spend) * 100
        bajo_pct = (bajo / total_spend) * 100

        st.markdown(f"""
        <div class="health-grid">
            <div class="health-card optimal">
                <div class="health-dot optimal">🟢 CTR excelente</div>
                <div class="health-pct optimal">{excelente_pct:.0f}%</div>
                <div class="health-amount">${excelente:,.0f}</div>
                <div class="health-note">+2x del benchmark</div>
            </div>
            <div class="health-card warning">
                <div class="health-dot warning">🟡 CTR aceptable</div>
                <div class="health-pct warning">{bueno_pct:.0f}%</div>
                <div class="health-amount">${bueno:,.0f}</div>
                <div class="health-note">En rango normal</div>
            </div>
            <div class="health-card critical">
                <div class="health-dot critical">🔴 CTR bajo</div>
                <div class="health-pct critical">{bajo_pct:.0f}%</div>
                <div class="health-amount">${bajo:,.0f}</div>
                <div class="health-note">Requiere atención</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.caption("💡 No hay datos de conversiones. La salud se mide por CTR vs benchmarks del sector.")


def render_plan_info(plan: str):
    plan = plan.lower() if plan else 'basic'

    if plan == 'basic':
        icon, label = "◈", "Plan Gratuito"
        items = [
            ("ok",  "✓ 1 campaña máximo"),
            ("ok",  "✓ 30 días de historial"),
            ("off", "✗ Sin exportación"),
            ("off", "✗ Sin alertas avanzadas"),
        ]
        upgrade = '<div style="margin-top:0.75rem;font-size:0.75rem;color:rgba(138,106,224,0.7);">⬆ Mejorar a PRO</div>'
    elif plan == 'pro':
        icon, label = "⭐", "Plan Pro"
        items = [
            ("ok", "✓ 20 anuncios máximo"),
            ("ok", "✓ 90 días de historial"),
            ("ok", "✓ Exportación a CSV"),
            ("ok", "✓ Alertas avanzadas"),
        ]
        upgrade = ''
    else:
        icon, label = "♛", "Plan Enterprise"
        items = [
            ("ok", "✓ Anuncios ilimitados"),
            ("ok", "✓ 365 días de historial"),
            ("ok", "✓ Exportación a CSV"),
            ("ok", "✓ Alertas avanzadas"),
            ("ok", "✓ Soporte prioritario"),
            ("ok", "✓ White label"),
        ]
        upgrade = ''

    items_html = ''.join(f'<div class="plan-item {cls}">{text}</div>' for cls, text in items)

    st.markdown(f"""
    <div class="plan-panel {plan}">
        <div class="plan-name">{icon} {label}</div>
        {items_html}
        {upgrade}
    </div>
    """, unsafe_allow_html=True)


def _fmt_big(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:,}"


def render_account_score(score_data: dict, df: pd.DataFrame, date_from: str, date_to: str, count: int, level: str):
    score = score_data['score']
    grade = score_data['grade']
    color = score_data['color']
    bd    = score_data['breakdown']

    has_roas = 'roas' in df.columns and df['roas'].fillna(0).sum() > 0
    if has_roas:
        avg_roas = df['roas'].mean()
        insight = (f"ROAS {avg_roas:.1f}x — excelente retorno" if avg_roas >= 3
                   else f"ROAS {avg_roas:.1f}x — hay margen de mejora" if avg_roas >= 1.5
                   else f"ROAS {avg_roas:.1f}x — necesita atención urgente")
    else:
        avg_ctr = df['ctr'].mean() if 'ctr' in df.columns else 0
        insight = (f"CTR {avg_ctr:.2f}% — muy por encima del benchmark" if avg_ctr >= 2
                   else f"CTR {avg_ctr:.2f}% — rendimiento aceptable" if avg_ctr >= 1
                   else f"CTR {avg_ctr:.2f}% — creatividad necesita revisión")

    level_label = 'adsets' if level == 'adset' else 'campañas'

    # Layout con st.columns para garantizar renderizado correcto
    c_score, c_bars, c_info = st.columns([1.2, 3, 2])

    with c_score:
        st.markdown(
            f'<div style="text-align:center;padding:1.25rem 0 0.5rem;">'
            f'<div style="font-size:2.8rem;font-weight:900;color:{color};line-height:1;">{score}</div>'
            f'<div style="font-size:1rem;font-weight:700;color:{color};margin-top:0.15rem;">{grade}</div>'
            f'<div style="font-size:0.6rem;color:rgba(232,230,240,0.3);text-transform:uppercase;'
            f'letter-spacing:0.12em;margin-top:0.3rem;">Account Score</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with c_bars:
        st.markdown(
            '<div style="font-size:0.65rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;'
            'color:rgba(232,230,240,0.3);margin-bottom:0.6rem;margin-top:1rem;">Desglose del score</div>',
            unsafe_allow_html=True
        )
        for lbl, val, mx in [
            ('Rendimiento',           bd['performance'],   bd['performance_max']),
            ('Eficiencia CPC',        bd['cpc_efficiency'], bd['cpc_max']),
            ('Salud de audiencia',    bd['audience'],       bd['audience_max']),
            ('Distrib. presupuesto',  bd['distribution'],   bd['distribution_max']),
        ]:
            pct = round(val / mx * 100) if mx else 0
            st.markdown(
                f'<div style="margin-bottom:0.45rem;">'
                f'<div style="display:flex;justify-content:space-between;font-size:0.68rem;'
                f'color:rgba(232,230,240,0.4);margin-bottom:0.2rem;">'
                f'<span>{lbl}</span>'
                f'<span style="color:rgba(232,230,240,0.7);">{val}/{mx}</span>'
                f'</div>'
                f'<div style="background:rgba(255,255,255,0.06);border-radius:4px;height:4px;">'
                f'<div style="width:{pct}%;background:{color};border-radius:4px;height:4px;"></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    with c_info:
        st.markdown(
            f'<div style="padding:1rem 0;text-align:right;">'
            f'<div style="font-size:0.7rem;color:rgba(232,230,240,0.3);margin-bottom:0.3rem;">'
            f'{date_from} al {date_to}</div>'
            f'<div style="font-size:0.82rem;color:rgba(232,230,240,0.55);margin-bottom:0.5rem;">'
            f'{count} {level_label} analizados</div>'
            f'<div style="font-size:0.84rem;color:rgba(232,230,240,0.8);line-height:1.4;">'
            f'{insight}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def render_kpi_grid(df: pd.DataFrame, total_ads: int, level: str):
    spend       = df['spend'].sum() if 'spend' in df.columns else 0
    reach       = int(df['reach'].sum()) if 'reach' in df.columns else 0
    clicks      = int(df['clicks'].sum()) if 'clicks' in df.columns else 0
    impressions = int(df['impressions'].sum()) if 'impressions' in df.columns else 0

    has_roas = 'roas' in df.columns and df['roas'].fillna(0).sum() > 0
    avg_roas = df['roas'].mean() if has_roas else 0
    avg_ctr  = df['ctr'].mean()  if 'ctr'  in df.columns else 0
    cpc_vals = df['cpc'].dropna() if 'cpc' in df.columns else pd.Series(dtype=float)
    avg_cpc  = float(cpc_vals[cpc_vals > 0].mean()) if not cpc_vals[cpc_vals > 0].empty else 0
    avg_cpm  = df['cpm'].mean() if 'cpm' in df.columns else (spend / impressions * 1000 if impressions > 0 else 0)
    avg_freq = df['frequency'].mean() if 'frequency' in df.columns else 0
    convs    = df['conversion_metric'].sum() if 'conversion_metric' in df.columns else 0

    label_nivel = 'Adsets' if level == 'adset' else 'Campañas'

    roas_c  = 'kpi-green' if avg_roas >= 2 else 'kpi-amber' if avg_roas >= 1 else 'kpi-red' if has_roas else 'kpi-white'
    ctr_c   = 'kpi-green' if avg_ctr >= 2 else 'kpi-amber' if avg_ctr >= 1 else 'kpi-red'
    cpc_c   = 'kpi-green' if 0 < avg_cpc <= 0.50 else 'kpi-amber' if avg_cpc <= 1.0 else 'kpi-red' if avg_cpc > 1.0 else 'kpi-white'
    freq_c  = 'kpi-green' if avg_freq <= 2 else 'kpi-amber' if avg_freq <= 4 else 'kpi-red'
    conv_c  = 'kpi-green' if convs > 0 else 'kpi-white'

    acc_color_cls = ('kpi-gold' if spend >= 1000 else 'kpi-gold')

    st.markdown(f"""
    <div class="kpi-grid-8">
        <div class="kpi-card kpi-gold">
            <div class="kpi-tag">Inversión total</div>
            <div class="kpi-val kpi-gold">{format_currency(spend)}</div>
            <div class="kpi-sub">Período seleccionado</div>
        </div>
        <div class="kpi-card kpi-blue">
            <div class="kpi-tag">Alcance</div>
            <div class="kpi-val kpi-blue">{_fmt_big(reach)}</div>
            <div class="kpi-sub">Personas únicas impactadas</div>
        </div>
        <div class="kpi-card kpi-purple">
            <div class="kpi-tag">Clics totales</div>
            <div class="kpi-val kpi-purple">{_fmt_big(clicks)}</div>
            <div class="kpi-sub">{_fmt_big(impressions)} impresiones</div>
        </div>
        <div class="kpi-card kpi-blue">
            <div class="kpi-tag">{label_nivel}</div>
            <div class="kpi-val kpi-white">{total_ads}</div>
            <div class="kpi-sub">Con datos en el período</div>
        </div>
    </div>
    <div class="kpi-grid-8" style="margin-bottom:1.5rem;">
        <div class="kpi-card {'kpi-green' if avg_roas >= 2 else 'kpi-amber' if avg_roas >= 1 and has_roas else 'kpi-red' if has_roas else 'kpi-blue'}">
            <div class="kpi-tag">ROAS</div>
            <div class="kpi-val {roas_c}">{f'{avg_roas:.2f}x' if has_roas else 'N/A'}</div>
            <div class="kpi-sub">{'Retorno sobre inversión' if has_roas else 'Sin datos de conversión'}</div>
        </div>
        <div class="kpi-card {'kpi-green' if avg_ctr >= 2 else 'kpi-amber' if avg_ctr >= 1 else 'kpi-red'}">
            <div class="kpi-tag">CTR Promedio</div>
            <div class="kpi-val {ctr_c}">{avg_ctr:.2f}%</div>
            <div class="kpi-sub">Benchmark industria: 1.0–2.0%</div>
        </div>
        <div class="kpi-card {'kpi-green' if 0 < avg_cpc <= 0.50 else 'kpi-amber' if avg_cpc <= 1.0 else 'kpi-blue'}">
            <div class="kpi-tag">CPC Promedio</div>
            <div class="kpi-val {cpc_c}">{f'${avg_cpc:.2f}' if avg_cpc > 0 else 'N/A'}</div>
            <div class="kpi-sub">CPM: ${avg_cpm:.2f}</div>
        </div>
        <div class="kpi-card {'kpi-green' if avg_freq <= 2 else 'kpi-amber' if avg_freq <= 4 else 'kpi-red'}">
            <div class="kpi-tag">Frecuencia</div>
            <div class="kpi-val {freq_c}">{avg_freq:.1f}x</div>
            <div class="kpi-sub">{'Saludable ✓' if avg_freq <= 2 else 'Monitorear' if avg_freq <= 4 else 'Saturación detectada'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_spend_charts(df: pd.DataFrame, level: str):
    name_col = 'adset_name' if ('adset_name' in df.columns and level == 'adset') else 'campaign_name'
    if name_col not in df.columns or df.empty:
        return

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="chart-section">
            <div class="chart-title">Distribución del gasto</div>
            <div class="chart-subtitle">Top campañas por inversión</div>
        </div>
        """, unsafe_allow_html=True)

        chart_df = df[[name_col, 'spend']].copy().sort_values('spend', ascending=True).tail(10)
        chart_df[name_col] = chart_df[name_col].str[:32]

        max_spend = chart_df['spend'].max()
        colors = [
            f'rgba(201,168,76,{0.4 + 0.55 * (v / max_spend):.2f})' if max_spend > 0 else 'rgba(201,168,76,0.6)'
            for v in chart_df['spend']
        ]

        fig = go.Figure(go.Bar(
            x=chart_df['spend'],
            y=chart_df[name_col],
            orientation='h',
            marker=dict(color=colors, line=dict(width=0)),
            text=[f'${v:,.0f}' for v in chart_df['spend']],
            textposition='outside',
            textfont=dict(color='rgba(232,230,240,0.55)', size=10, family='Satoshi')
        ))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=55, t=8, b=8), height=260,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0)',
                       tickfont=dict(color='rgba(232,230,240,0.55)', size=10, family='Satoshi'),
                       ticksuffix='  '),
            font=dict(family='Satoshi, sans-serif'),
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with col2:
        st.markdown("""
        <div class="chart-section">
            <div class="chart-title">CTR vs Gasto</div>
            <div class="chart-subtitle">Color = frecuencia · Tamaño = inversión</div>
        </div>
        """, unsafe_allow_html=True)

        cols_needed = [name_col, 'spend', 'ctr', 'frequency']
        sc_df = df[[c for c in cols_needed if c in df.columns]].copy()
        sc_df[name_col] = sc_df[name_col].str[:22]
        if 'frequency' not in sc_df.columns:
            sc_df['frequency'] = 0

        def freq_color(f):
            return '#64DC96' if f <= 2 else '#FBbf24' if f <= 4 else '#FC8181'

        fig2 = go.Figure()
        for _, row in sc_df.iterrows():
            fig2.add_trace(go.Scatter(
                x=[row['spend']], y=[row['ctr']],
                mode='markers+text',
                marker=dict(
                    size=max(9, min(float(row['spend']) / 8, 36)),
                    color=freq_color(float(row.get('frequency', 0))),
                    opacity=0.82,
                    line=dict(color='rgba(255,255,255,0.08)', width=1)
                ),
                text=[row[name_col]],
                textposition='top center',
                textfont=dict(color='rgba(232,230,240,0.45)', size=9, family='Satoshi'),
                showlegend=False,
                hovertemplate=(
                    f"<b>{row[name_col]}</b><br>"
                    f"Gasto: ${row['spend']:,.0f}<br>"
                    f"CTR: {row['ctr']:.2f}%<br>"
                    f"Frecuencia: {row.get('frequency', 0):.1f}<extra></extra>"
                )
            ))

        fig2.add_hline(y=1.0, line_dash='dot', line_color='rgba(255,255,255,0.12)',
                       annotation_text='Benchmark 1%',
                       annotation_font=dict(color='rgba(232,230,240,0.2)', size=9),
                       annotation_position='bottom right')
        fig2.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=8, b=30), height=260,
            xaxis=dict(title=dict(text='Gasto ($)', font=dict(color='rgba(232,230,240,0.3)', size=9)),
                       gridcolor='rgba(255,255,255,0.04)',
                       tickfont=dict(color='rgba(232,230,240,0.4)', size=9, family='Satoshi'),
                       zeroline=False),
            yaxis=dict(title=dict(text='CTR (%)', font=dict(color='rgba(232,230,240,0.3)', size=9)),
                       gridcolor='rgba(255,255,255,0.04)',
                       tickfont=dict(color='rgba(232,230,240,0.4)', size=9, family='Satoshi'),
                       zeroline=False),
            font=dict(family='Satoshi, sans-serif'),
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})

    st.markdown("""
    <div style="display:flex;gap:1.5rem;font-size:0.69rem;color:rgba(232,230,240,0.38);
         margin-top:-0.75rem;margin-bottom:0.5rem;padding-left:52%;">
        <span><span style="color:#64DC96;">●</span> Frecuencia ≤2 (saludable)</span>
        <span><span style="color:#FBbf24;">●</span> 2–4 (monitorear)</span>
        <span><span style="color:#FC8181;">●</span> >4 (saturación)</span>
    </div>
    """, unsafe_allow_html=True)


def render_priority_queue(actions: list):
    if not actions:
        return
    st.markdown('<div class="section-label">Inteligencia</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Cola de Prioridades</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem;color:rgba(232,230,240,0.4);margin-bottom:1rem;">Acciones ordenadas por impacto. Completa de arriba hacia abajo.</div>', unsafe_allow_html=True)

    for i, a in enumerate(actions, 1):
        st.markdown(f"""
        <div class="pq-item" style="background:{a['bg']};border:1px solid {a['border']};border-left:3px solid {a['color']};">
            <div>
                <div class="pq-icon">{a['icon']}</div>
                <div class="pq-num" style="color:{a['color']};">#{i}</div>
            </div>
            <div>
                <div class="pq-title">{a['title']}</div>
                <div class="pq-detail">{a['detail']}</div>
                <div class="pq-action">→ {a['action']}</div>
            </div>
            <div>
                <span class="pq-badge" style="color:{a['color']};background:{a['bg']};border-color:{a['border']};">{a['urgency']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_frequency_panel(df: pd.DataFrame, level: str):
    if 'frequency' not in df.columns:
        return
    name_col = 'adset_name' if ('adset_name' in df.columns and level == 'adset') else 'campaign_name'
    if name_col not in df.columns:
        return

    freq_df = df[[name_col, 'frequency', 'spend',
                  'impressions', 'reach']].copy().sort_values('frequency', ascending=False)

    st.markdown('<div class="section-label">Audiencia</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Mapa de Saturación</div>', unsafe_allow_html=True)

    rows_html = []
    for _, row in freq_df.iterrows():
        freq    = float(row['frequency'])
        name    = str(row[name_col])[:50]
        spend   = float(row['spend'])
        impr    = int(row.get('impressions', 0))
        reach   = int(row.get('reach', 0))
        bar_pct = min(round(freq / 8 * 100), 100)

        if freq > 5:
            clr, status, bg, bc = '#FC8181', 'SATURADA', 'rgba(252,129,129,0.07)', '#FC818133'
        elif freq > 3:
            clr, status, bg, bc = '#FBbf24', 'ALERTA', 'rgba(251,191,36,0.07)', '#FBbf2433'
        else:
            clr, status, bg, bc = '#64DC96', 'SALUDABLE', 'rgba(100,220,150,0.05)', '#64DC9633'

        rows_html.append(f"""
        <div class="freq-row" style="background:{bg};">
            <div>
                <div style="display:flex;align-items:center;">
                    <span class="freq-name">{name}</span>
                    <span class="freq-badge" style="color:{clr};border-color:{bc};">{status}</span>
                </div>
                <div style="font-size:0.71rem;color:rgba(232,230,240,0.35);margin-top:0.3rem;">
                    {_fmt_big(impr)} impresiones · {_fmt_big(reach)} alcance · ${spend:,.0f} gastado
                </div>
                <div class="freq-bar-track">
                    <div style="width:{bar_pct}%;background:{clr};border-radius:4px;height:4px;"></div>
                </div>
            </div>
            <div style="text-align:right;min-width:60px;">
                <div class="freq-val" style="color:{clr};">{freq:.1f}x</div>
                <div class="freq-sub">frecuencia</div>
            </div>
        </div>
        """)

    st.markdown(''.join(rows_html), unsafe_allow_html=True)
    st.caption("Frecuencia ideal: ≤2 para reconocimiento de marca · ≤3 para conversión · Por encima de 5 la creatividad está agotada.")


def render_benchmark_table(df: pd.DataFrame, level: str):
    """Tabla comparativa de métricas vs benchmarks del sector."""
    name_col = 'adset_name' if ('adset_name' in df.columns and level == 'adset') else 'campaign_name'
    if name_col not in df.columns or df.empty:
        return

    BENCH = {
        'TRÁFICO': (1.5, 0.55), 'ENGAGEMENT': (1.2, 0.50), 'LEADS': (1.8, 0.75),
        'CONVERSIONES': (1.3, 0.65), 'RECONOCIMIENTO': (0.8, 0.35),
        'VIDEO': (1.2, 0.45), 'DEFAULT': (1.0, 0.55),
    }

    rows = []
    meta = []   # guardar b_ctr, b_cpc, cpc raw para estilos
    for _, row in df.sort_values('spend', ascending=False).iterrows():
        name  = str(row.get(name_col, ''))[:32]
        obj   = str(row.get('objective', 'DEFAULT')).upper()
        b_ctr, b_cpc = BENCH.get(obj, BENCH['DEFAULT'])
        ctr   = float(row.get('ctr', 0))
        cpc   = float(row.get('cpc', 0) or 0)
        spend = float(row.get('spend', 0))
        freq  = float(row.get('frequency', 0))
        diff  = ctr - b_ctr

        rows.append({
            'Campaña / Adset': name,
            'Gasto':           f'${spend:,.0f}',
            'CTR':             f'{ctr:.2f}%  ({diff:+.1f}% vs bench)',
            'CPC':             f'${cpc:.2f}' if cpc > 0 else 'N/A',
            'Frecuencia':      f'{freq:.1f}x',
            'Benchmark':       f'CTR {b_ctr:.1f}% · CPC ${b_cpc:.2f}',
        })
        meta.append({'ctr': ctr, 'b_ctr': b_ctr, 'cpc': cpc, 'b_cpc': b_cpc, 'freq': freq})

    tbl = pd.DataFrame(rows)

    def _style(df_s):
        styles = pd.DataFrame('', index=df_s.index, columns=df_s.columns)
        for i, m in enumerate(meta):
            # CTR
            if m['ctr'] >= m['b_ctr'] * 1.5:
                styles.at[i, 'CTR'] = 'color:#64DC96;font-weight:600'
            elif m['ctr'] >= m['b_ctr']:
                styles.at[i, 'CTR'] = 'color:#FBbf24;font-weight:600'
            else:
                styles.at[i, 'CTR'] = 'color:#FC8181;font-weight:600'
            # CPC
            if m['cpc'] > 0:
                if m['cpc'] <= m['b_cpc']:
                    styles.at[i, 'CPC'] = 'color:#64DC96;font-weight:600'
                elif m['cpc'] <= m['b_cpc'] * 1.5:
                    styles.at[i, 'CPC'] = 'color:#FBbf24'
                else:
                    styles.at[i, 'CPC'] = 'color:#FC8181'
            # Frecuencia
            if m['freq'] <= 2:
                styles.at[i, 'Frecuencia'] = 'color:#64DC96'
            elif m['freq'] <= 4:
                styles.at[i, 'Frecuencia'] = 'color:#FBbf24'
            else:
                styles.at[i, 'Frecuencia'] = 'color:#FC8181;font-weight:600'
        return styles

    st.dataframe(
        tbl.style.apply(_style, axis=None),
        use_container_width=True,
        hide_index=True,
    )


def render_campaign_cards_v2(detailed: dict, level: str, plan_limits: dict):
    if not detailed['campaigns']:
        return

    label = 'Adset' if level == 'adset' else 'Campaña'
    st.markdown(f'<div class="section-label">Detalle</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Análisis por {label}</div>', unsafe_allow_html=True)

    for camp in detailed['campaigns']:
        priority_map = {'alta': ('high', '🔴'), 'media': ('medium', '🟡')}
        card_cls, icon = priority_map.get(camp['priority'], ('low', '🟢'))

        title_name = camp.get('adset_name') or camp.get('campaign_name', 'Sin nombre')
        ctr     = float(camp.get('ctr', 0))
        cpc     = float(camp.get('cpc', 0))
        spend   = float(camp.get('spend', 0))
        freq    = float(camp.get('frequency', 0))
        clicks  = int(camp.get('clicks', 0))
        impr    = int(camp.get('impressions', 0))
        reach   = int(camp.get('reach', 0))
        roas    = float(camp.get('roas', 0))

        ctr_c  = '#64DC96' if camp['ctr_rating'] == 'excelente' else '#FBbf24' if camp['ctr_rating'] == 'bueno' else '#FC8181'
        freq_c = '#64DC96' if freq <= 2 else '#FBbf24' if freq <= 4 else '#FC8181'

        expander_label = f"{icon} {title_name[:55]}  ·  ${spend:,.2f}  ·  CTR {ctr:.2f}%  ·  Freq {freq:.1f}x"
        with st.expander(expander_label):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Gasto", f"${spend:,.2f}")
            with c2:
                st.metric("CTR", f"{ctr:.2f}%",
                          delta=f"bench {camp['benchmark_ctr']:.1f}%",
                          delta_color="normal" if ctr >= camp['benchmark_ctr'] else "inverse")
            with c3:
                st.metric("CPC", f"${cpc:.2f}" if cpc > 0 else "N/A",
                          delta=f"bench ${camp['benchmark_cpc']:.2f}",
                          delta_color="normal" if 0 < cpc <= camp['benchmark_cpc'] else "inverse")
            with c4:
                st.metric("Frecuencia", f"{freq:.1f}x")

            st.markdown(f"""
            <div class="camp-v2 camp-card {card_cls}" style="margin-top:0.75rem;">
                <div class="camp-v2-grid">
                    <div class="camp-v2-metric">
                        <div class="camp-v2-lbl">Impresiones</div>
                        <div class="camp-v2-val">{_fmt_big(impr)}</div>
                        <div class="camp-v2-sub">{_fmt_big(reach)} alcance único</div>
                    </div>
                    <div class="camp-v2-metric">
                        <div class="camp-v2-lbl">Clics</div>
                        <div class="camp-v2-val">{_fmt_big(clicks)}</div>
                        <div class="camp-v2-sub">de {_fmt_big(impr)} impresiones</div>
                    </div>
                    <div class="camp-v2-metric">
                        <div class="camp-v2-lbl">ROAS</div>
                        <div class="camp-v2-val" style="color:{'#64DC96' if roas >= 2 else '#FBbf24' if roas >= 1 else '#FC8181' if roas > 0 else '#F5F3FF'};">{f'{roas:.2f}x' if roas > 0 else 'N/A'}</div>
                        <div class="camp-v2-sub">retorno sobre inversión</div>
                    </div>
                    <div class="camp-v2-metric">
                        <div class="camp-v2-lbl">Objetivo</div>
                        <div class="camp-v2-val" style="font-size:0.9rem;">{get_objective_label(camp.get('objective',''))}</div>
                    </div>
                </div>
                <div style="border-top:1px solid rgba(255,255,255,0.06);padding-top:0.75rem;
                     display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                    <div>
                        <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
                             color:rgba(232,230,240,0.3);margin-bottom:0.25rem;">CTR</div>
                        <div style="font-size:0.82rem;color:{ctr_c};">{camp['ctr_emoji']} {camp['ctr_message']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
                             color:rgba(232,230,240,0.3);margin-bottom:0.25rem;">CPC</div>
                        <div style="font-size:0.82rem;color:rgba(232,230,240,0.7);">{camp['cpc_emoji']} {camp['cpc_message']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
                             color:rgba(232,230,240,0.3);margin-bottom:0.25rem;">Frecuencia</div>
                        <div style="font-size:0.82rem;color:{freq_c};">{camp['frequency_message']}</div>
                    </div>
                    <div>
                        <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
                             color:rgba(232,230,240,0.3);margin-bottom:0.25rem;">CPM estimado</div>
                        <div style="font-size:0.82rem;color:rgba(232,230,240,0.7);">
                            {f'${spend / impr * 1000:.2f} por mil imp.' if impr > 0 else 'N/A'}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if plan_limits['can_see_alerts']:
                st.markdown(f"""
                <div class="rec-box">
                    <div class="rec-title">{camp['action']}</div>
                    <div class="rec-text">{camp['action_detail']}</div>
                    <div style="font-size:0.78rem;color:rgba(100,220,150,0.75);margin-top:0.5rem;">📈 {camp['expected_result']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:rgba(138,106,224,0.07);border:1px solid rgba(138,106,224,0.18);
                     border-radius:10px;padding:0.75rem 1rem;font-size:0.78rem;
                     color:rgba(232,230,240,0.45);margin-top:0.5rem;">
                    ✦ Actualiza a <strong style="color:#A890F0;">PRO</strong> para ver recomendaciones y acciones específicas.
                </div>
                """, unsafe_allow_html=True)


def render_action_center(actions: list):
    """Renderiza el centro de acciones agrupadas por Kill, Scale, Fix."""
    if not actions:
        st.markdown("""
        <div style="background:rgba(138,106,224,0.06); border:1px solid rgba(138,106,224,0.18);
             border-radius:16px; padding:2rem; text-align:center;">
            <div style="font-family:'Satoshi',sans-serif; font-size:1.1rem; font-weight:700;
                 color:#A890F0; margin-bottom:0.5rem;">✅ Todo bajo control</div>
            <div style="font-size:0.85rem; color:rgba(232,230,240,0.4);">
                No hay acciones urgentes pendientes. Tus campañas están funcionando correctamente.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Agrupar acciones
    kill_actions = []
    fix_actions = []
    scale_actions = []

    for a in actions:
        urgency = a.get('urgency', '').upper()
        if urgency in ['CRÍTICO', 'URGENTE']:
            kill_actions.append(a)
        elif urgency == 'OPORTUNIDAD':
            scale_actions.append(a)
        else:  # ATENCIÓN u otros
            fix_actions.append(a)

    st.markdown('<div class="section-label">Acción</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 Acciones Prioritarias</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem;color:rgba(232,230,240,0.4);margin-bottom:1.5rem;">Ordenadas por impacto. Enfócate en Kill primero, luego Fix, finalmente Scale.</div>', unsafe_allow_html=True)

    # Contadores
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:rgba(252,129,129,0.07); border:1px solid rgba(252,129,129,0.2);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#FC8181;">{len(kill_actions)}</div>
            <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; color:#FC8181;">Kill</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background:rgba(251,191,36,0.07); border:1px solid rgba(251,191,36,0.2);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#FBbf24;">{len(fix_actions)}</div>
            <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; color:#FBbf24;">Fix</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background:rgba(100,220,150,0.07); border:1px solid rgba(100,220,150,0.2);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#64DC96;">{len(scale_actions)}</div>
            <div style="font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; color:#64DC96;">Scale</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin:1.5rem 0;"></div>', unsafe_allow_html=True)

    # Sección KILL
    if kill_actions:
        st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FC8181; margin-bottom:0.75rem;">❌ Kill (Detener inmediatamente)</div>', unsafe_allow_html=True)
        for a in kill_actions:
            st.markdown(f"""
            <div style="background:rgba(252,129,129,0.05); border-left:3px solid #FC8181;
                 border-radius:0 10px 10px 0; padding:1rem; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:start; gap:0.75rem;">
                    <div style="font-size:1.2rem;">{a['icon']}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700; color:#F5F3FF; font-size:0.9rem;">{a['title']}</div>
                        <div style="font-size:0.8rem; color:rgba(232,230,240,0.55); margin:0.25rem 0;">{a['detail']}</div>
                        <div style="display:flex; gap:0.75rem; margin-top:0.5rem; font-size:0.7rem;">
                            <span style="color:#FC8181;">Confidence: {a.get('confidence', 'Medium')}</span>
                            <span style="color:#FBbf24;">Impact: {a.get('impact', 'Medium')}</span>
                            <span style="color:#64DC96;">{a.get('time_context', '')}</span>
                        </div>
                        <div style="font-size:0.8rem; color:#FC8181; font-weight:600;">→ {a['action']}</div>
                    </div>
                    <div style="font-size:0.65rem; font-weight:800; text-transform:uppercase;
                         color:#FC8181; background:rgba(252,129,129,0.15); padding:0.2rem 0.6rem;
                         border-radius:20px;">{a['urgency']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Sección FIX
    if fix_actions:
        st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#FBbf24; margin-bottom:0.75rem;">⚠️ Fix (Optimizar/Corregir)</div>', unsafe_allow_html=True)
        for a in fix_actions:
            st.markdown(f"""
            <div style="background:rgba(251,191,36,0.05); border-left:3px solid #FBbf24;
                 border-radius:0 10px 10px 0; padding:1rem; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:start; gap:0.75rem;">
                    <div style="font-size:1.2rem;">{a['icon']}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700; color:#F5F3FF; font-size:0.9rem;">{a['title']}</div>
                        <div style="font-size:0.8rem; color:rgba(232,230,240,0.55); margin:0.25rem 0;">{a['detail']}</div>
                        <div style="display:flex; gap:0.75rem; margin-top:0.5rem; font-size:0.7rem;">
                            <span style="color:#FC8181;">Confidence: {a.get('confidence', 'Medium')}</span>
                            <span style="color:#FBbf24;">Impact: {a.get('impact', 'Medium')}</span>
                            <span style="color:#64DC96;">{a.get('time_context', '')}</span>
                        </div>
                        <div style="font-size:0.8rem; color:#FBbf24; font-weight:600;">→ {a['action']}</div>
                    </div>
                    <div style="font-size:0.65rem; font-weight:800; text-transform:uppercase;
                         color:#FBbf24; background:rgba(251,191,36,0.15); padding:0.2rem 0.6rem;
                         border-radius:20px;">{a['urgency']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Sección SCALE
    if scale_actions:
        st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64DC96; margin-bottom:0.75rem;">✅ Scale (Aumentar/Escalar)</div>', unsafe_allow_html=True)
        for a in scale_actions:
            st.markdown(f"""
            <div style="background:rgba(100,220,150,0.05); border-left:3px solid #64DC96;
                 border-radius:0 10px 10px 0; padding:1rem; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:start; gap:0.75rem;">
                    <div style="font-size:1.2rem;">{a['icon']}</div>
                    <div style="flex:1;">
                        <div style="font-weight:700; color:#F5F3FF; font-size:0.9rem;">{a['title']}</div>
                        <div style="font-size:0.8rem; color:rgba(232,230,240,0.55); margin:0.25rem 0;">{a['detail']}</div>
                        <div style="display:flex; gap:0.75rem; margin-top:0.5rem; font-size:0.7rem;">
                            <span style="color:#FC8181;">Confidence: {a.get('confidence', 'Medium')}</span>
                            <span style="color:#FBbf24;">Impact: {a.get('impact', 'Medium')}</span>
                            <span style="color:#64DC96;">{a.get('time_context', '')}</span>
                        </div>
                        <div style="font-size:0.8rem; color:#64DC96; font-weight:600;">→ {a['action']}</div>
                    </div>
                    <div style="font-size:0.65rem; font-weight:800; text-transform:uppercase;
                         color:#64DC96; background:rgba(100,220,150,0.15); padding:0.2rem 0.6rem;
                         border-radius:20px;">{a['urgency']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_account_status_simple(score_data: dict):
    """Renderiza el status de cuenta simplificado."""
    score = score_data['score']
    grade = score_data['grade']
    color = score_data['color']

    # Determinar status basado en score
    if score >= 75:
        status = "Óptimo"
        status_emoji = "✅"
        status_color = "#64DC96"
    elif score >= 55:
        status = "Needs Optimization"
        status_emoji = "⚠️"
        status_color = "#FBbf24"
    else:
        status = "Requires Attention"
        status_emoji = "🔴"
        status_color = "#FC8181"

    st.markdown('<div class="section-label">Estado</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Account Status</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:2.5rem; font-weight:900; color:{color}; line-height:1;">{score}</div>
            <div style="font-size:0.7rem; color:rgba(232,230,240,0.3); text-transform:uppercase;
                 letter-spacing:0.1em; margin-top:0.2rem;">Score</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="font-size:1.8rem; font-weight:900; color:{color}; line-height:1;">{grade}</div>
            <div style="font-size:0.7rem; color:rgba(232,230,240,0.3); text-transform:uppercase;
                 letter-spacing:0.1em; margin-top:0.2rem;">Grade</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="text-align:center; padding-top:0.5rem;">
            <div style="font-size:1.1rem; font-weight:700; color:{status_color};">{status_emoji} {status}</div>
            <div style="font-size:0.75rem; color:rgba(232,230,240,0.4); margin-top:0.25rem;">
                {f"{score}/100 - "}{'Excelente rendimiento' if score >= 75 else 'Hay margen de mejora' if score >= 55 else 'Requiere atención urgente'}
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_top_insights(df: pd.DataFrame):
    """Renderiza insights clave (no métricas detalladas)."""
    if df.empty:
        return

    insights = []

    # CPC analysis
    if 'cpc' in df.columns:
        avg_cpc = df['cpc'].mean()
        if avg_cpc > 1.0:
            insights.append(("💰", "CPC is 35% above average", f"Average CPC: ${avg_cpc:.2f}"))
        elif avg_cpc < 0.3:
            insights.append(("✅", "CPC is excellent", f"Average CPC: ${avg_cpc:.2f}"))

    # CTR analysis
    if 'ctr' in df.columns:
        avg_ctr = df['ctr'].mean()
        if avg_ctr < 1.0:
            insights.append(("⚠️", "CTR below benchmark", f"Average CTR: {avg_ctr:.1f}%"))
        elif avg_ctr > 2.5:
            insights.append(("🚀", "CTR above benchmark", f"Average CTR: {avg_ctr:.1f}%"))

    # Frequency analysis
    if 'frequency' in df.columns:
        saturated = df[df['frequency'] > 4]
        if len(saturated) > 0:
            insights.append(("🔄", f"{len(saturated)} campaigns saturated", "Frequency > 4x"))

    # ROAS analysis
    if 'roas' in df.columns:
        avg_roas = df['roas'].mean()
        if avg_roas > 0:
            if avg_roas < 1:
                insights.append(("🔴", "ROAS below 1x", f"Average ROAS: {avg_roas:.1f}x"))
            elif avg_roas >= 3:
                insights.append(("✅", "Excellent ROAS", f"Average ROAS: {avg_roas:.1f}x"))

    # Spend concentration
    if 'spend' in df.columns and len(df) > 1:
        top_3_pct = df.nlargest(3, 'spend')['spend'].sum() / df['spend'].sum() * 100
        if top_3_pct > 80:
            insights.append(("🎯", "Budget highly concentrated", f"Top 3 campaigns: {top_3_pct:.0f}% of spend"))

    if not insights:
        return

    st.markdown('<div class="section-label">Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Top Insights</div>', unsafe_allow_html=True)

    for emoji, title, detail in insights[:5]:  # Mostrar máximo 5
        st.markdown(f"""
        <div style="background:rgba(138,106,224,0.05); border-radius:10px; padding:0.9rem 1rem;
             margin-bottom:0.5rem; display:flex; align-items:center; gap:0.75rem;">
            <div style="font-size:1.2rem;">{emoji}</div>
            <div style="flex:1;">
                <div style="font-weight:700; color:#F5F3FF; font-size:0.85rem;">{title}</div>
                <div style="font-size:0.75rem; color:rgba(232,230,240,0.5);">{detail}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_today_summary(user_id: int, actions: list, score_data: dict, last_update: str = None):
    """Renderiza el resumen diario para crear hábito de uso."""
    if not actions:
        st.markdown("""
        <div style="background:rgba(100,220,150,0.06); border:1px solid rgba(100,220,150,0.15);
             border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-family:'Satoshi',sans-serif; font-size:0.9rem; font-weight:700;
                         color:#64DC96; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.25rem;">
                        🔁 Today's Summary
                    </div>
                    <div style="font-size:1.1rem; font-weight:700; color:#F5F3FF;">✅ Everything looks good</div>
                    <div style="font-size:0.8rem; color:rgba(232,230,240,0.4); margin-top:0.25rem;">
                        No urgent actions needed today
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.7rem; color:rgba(232,230,240,0.3);">Last update</div>
                    <div style="font-size:0.8rem; color:#64DC96;">Just now</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Contar acciones por categoría
    kill_actions = []
    fix_actions = []
    scale_actions = []

    for a in actions:
        urgency = a.get('urgency', '').upper()
        if urgency in ['CRÍTICO', 'URGENTE']:
            kill_actions.append(a)
        elif urgency == 'OPORTUNIDAD':
            scale_actions.append(a)
        else:  # ATENCIÓN u otros
            fix_actions.append(a)

    kill_count = len(kill_actions)
    fix_count = len(fix_actions)
    scale_count = len(scale_actions)

    # Determinar estado general
    if kill_count > 0:
        status = "⚠️ Needs Attention"
        status_color = "#FBbf24"
    elif fix_count > 0:
        status = "📊 Optimize"
        status_color = "#60A5FA"
    else:
        status = "✅ All Good"
        status_color = "#64DC96"

    # Formatear última actualización
    update_text = last_update if last_update else "Just now"

    st.markdown(f"""
    <div style="background:rgba(138,106,224,0.06); border:1px solid rgba(138,106,224,0.15);
         border-radius:16px; padding:1.5rem; margin-bottom:1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <div>
                <div style="font-family:'Satoshi',sans-serif; font-size:0.9rem; font-weight:700;
                     color:#A890F0; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:0.25rem;">
                    🔁 Today's Summary
                </div>
                <div style="font-size:1.1rem; font-weight:700; color:{status_color};">{status}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:0.7rem; color:rgba(232,230,240,0.3);">Last update</div>
                <div style="font-size:0.8rem; color:#A890F0;">{update_text}</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1rem;">
            <div style="text-align:center;">
                <div style="font-size:1.5rem; font-weight:800; color:#FC8181;">{kill_count}</div>
                <div style="font-size:0.75rem; color:rgba(232,230,240,0.5);">to stop</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem; font-weight:800; color:#FBbf24;">{fix_count}</div>
                <div style="font-size:0.75rem; color:rgba(232,230,240,0.5);">to fix</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:1.5rem; font-weight:800; color:#64DC96;">{scale_count}</div>
                <div style="font-size:0.75rem; color:rgba(232,230,240,0.5);">to scale</div>
            </div>
        </div>

        <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:0.8rem; color:rgba(232,230,240,0.5);">
                Score today: <span style="color:#F5F3FF; font-weight:600;">{score_data['score']}/100</span>
                • Total actions: <span style="color:#F5F3FF; font-weight:600;">{kill_count + fix_count + scale_count}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_progress_history(user_id: int):
    """Renderiza el historial de progreso y acciones completadas."""
    # Obtener datos de progreso
    progress_history = get_user_progress_history(user_id, days=7)
    completed_actions = get_completed_actions(user_id, days=7)
    total_completed = get_total_completed_actions(user_id)

    if not progress_history and not completed_actions:
        # Mostrar mensaje motivacional para empezar
        st.markdown("""
        <div style="background:rgba(138,106,224,0.05); border:1px solid rgba(138,106,224,0.1);
             border-radius:12px; padding:1.5rem; text-align:center;">
            <div style="font-size:1rem; font-weight:700; color:#A890F0; margin-bottom:0.5rem;">🚀 Start Your Journey</div>
            <div style="font-size:0.8rem; color:rgba(232,230,240,0.4);">
                Complete your first action to start tracking progress
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown('<div class="section-label">Progreso</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Your Progress</div>', unsafe_allow_html=True)

    # Tarjetas de resumen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:rgba(100,220,150,0.07); border:1px solid rgba(100,220,150,0.15);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#64DC96;">{total_completed}</div>
            <div style="font-size:0.7rem; color:rgba(232,230,240,0.5); text-transform:uppercase; letter-spacing:0.1em;">
                Actions Completed
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        score_improvement = 0
        if len(progress_history) >= 2:
            latest = progress_history[0]['score'] if progress_history else 0
            oldest = progress_history[-1]['score'] if len(progress_history) > 1 else latest
            score_improvement = latest - oldest

        improvement_text = f"+{score_improvement}" if score_improvement > 0 else f"{score_improvement}"
        improvement_color = "#64DC96" if score_improvement > 0 else "#FC8181" if score_improvement < 0 else "#FBbf24"

        st.markdown(f"""
        <div style="background:rgba(138,106,224,0.07); border:1px solid rgba(138,106,224,0.15);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:{improvement_color};">{improvement_text}</div>
            <div style="font-size:0.7rem; color:rgba(232,230,240,0.5); text-transform:uppercase; letter-spacing:0.1em;">
                Score Change (7d)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        recent_completed = len(completed_actions)
        st.markdown(f"""
        <div style="background:rgba(96,165,250,0.07); border:1px solid rgba(96,165,250,0.15);
             border-radius:12px; padding:1rem; text-align:center;">
            <div style="font-size:1.5rem; font-weight:800; color:#60A5FA;">{recent_completed}</div>
            <div style="font-size:0.7rem; color:rgba(232,230,240,0.5); text-transform:uppercase; letter-spacing:0.1em;">
                This Week
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Mostrar últimas acciones completadas
    if completed_actions:
        st.markdown('<div style="margin-top:1.5rem; font-size:0.8rem; color:rgba(232,230,240,0.4);">Recently completed:</div>', unsafe_allow_html=True)
        for action in completed_actions[:3]:  # Mostrar solo las 3 más recientes
            action_type = action['action_type']
            type_color = '#FC8181' if action_type == 'kill' else '#FBbf24' if action_type == 'fix' else '#64DC96'
            type_emoji = '❌' if action_type == 'kill' else '⚠️' if action_type == 'fix' else '✅'

            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.03); border-left:2px solid {type_color};
                 border-radius:0 8px 8px 0; padding:0.75rem 1rem; margin-bottom:0.5rem;">
                <div style="display:flex; align-items:center; gap:0.5rem;">
                    <span style="color:{type_color};">{type_emoji}</span>
                    <span style="font-size:0.8rem; color:#F5F3FF;">{action['campaign_name'][:30]}</span>
                    <span style="font-size:0.7rem; color:rgba(232,230,240,0.4); margin-left:auto;">
                        {datetime.fromisoformat(action['completed_at']).strftime('%b %d') if 'completed_at' in action else ''}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def client_dashboard():
    # st.set_page_config(
    #     page_title=f"Ads Intelligence – {st.session_state.get('company_name', 'Mi Cuenta')}",
    #     page_icon="◈",
    #     layout="wide"
    # )

    # Inyectar CSS premium
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

    # Forzar actualización del plan desde la BD
    if st.session_state.get('user_id'):
        user = get_user_by_id(st.session_state['user_id'])
        if user and user.get('plan'):
            st.session_state['plan'] = user['plan']

    # Obtener user_id de la sesión para usarlo en toda la función
    user_id = st.session_state.get('user_id')

    plan = st.session_state.get('plan', 'basic')
    date_range = None

    # ========== HEADER ==========
    company = st.session_state.get('company_name', 'Mi Empresa')
    email   = st.session_state.get('user_email', '')
    plan_cls = plan.lower()

    col_info, col_btn = st.columns([5, 1])
    with col_info:
        st.markdown(f"""
        <div style="padding: 1.5rem 0 0.5rem;">
            <div class="dash-logo"><img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="logo-mark" alt="Logo"> Ads Intelligence</div>
            <div class="dash-company" style="margin-top:0.5rem;">{company}</div>
            <div style="display:flex; align-items:center; gap:0.75rem; margin-top:0.4rem;">
                <div class="dash-sub">{email}</div>
                <span class="plan-badge plan-{plan_cls}">{'◈' if plan_cls=='basic' else '⭐' if plan_cls=='pro' else '♛'} {plan.upper()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        st.markdown('<div style="padding-top:2rem;">', unsafe_allow_html=True)
        if st.button("Cerrar sesión →", use_container_width=True):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # Banner y botones de Upgrade para usuarios del plan gratuito
    if plan == 'basic':
        st.markdown("""
        <div style="background: #e7f3ff; border: 1px solid #bde4ff;
             border-radius:12px; padding:1rem 1.5rem; margin-bottom:1rem; display:flex; 
             justify-content:space-between; align-items:center;">
            <div>
                <div style="color:#1877F2; font-weight:700; font-size:0.95rem; margin-bottom:0.25rem;">
                    🚀 Desbloquea todo el potencial de Ads Intelligence
                </div>
                <div style="color:#1c1e21; font-size:0.85rem;">
                    Actualiza a PRO para analizar hasta 20 campañas y recibir alertas de la IA.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⭐ Actualizar a PRO ($79/mes)", use_container_width=True, key="upgrade_pro"):
                price_id = os.getenv('STRIPE_PRO_PRICE_ID')
                if price_id and user_id:
                    checkout_url = create_stripe_checkout_session(price_id, user_id)
                    if checkout_url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)
        with col2:
            if st.button("♛ Actualizar a ENTERPRISE ($199/mes)", use_container_width=True, key="upgrade_enterprise"):
                price_id = os.getenv('STRIPE_ENTERPRISE_PRICE_ID')
                if price_id and user_id:
                    checkout_url = create_stripe_checkout_session(price_id, user_id)
                    if checkout_url:
                        st.markdown(f'<meta http-equiv="refresh" content="0; url={checkout_url}">', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Plan info en sidebar
    with st.sidebar:
        # El CSS ya está inyectado arriba
        st.markdown('<div class="dash-logo" style="padding:1rem 0 0.5rem;"><img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="logo-mark" alt="Logo"> Ads Intelligence</div>', unsafe_allow_html=True)
        render_plan_info(plan)

    # ========== FILTROS ==========
    st.markdown('<div class="section-label">Análisis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Filtros de análisis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        today = date.today()
        max_days = 30 if plan == 'basic' else 90 if plan == 'pro' else 365
        date_range = st.date_input(
            "Rango de fechas",
            [today - timedelta(days=min(29, max_days - 1)), today],
            key="date_range_filter"
        )
    with col2:
        level = st.selectbox(
            "Nivel de análisis",
            options=['adset', 'campaign'],
            format_func=lambda x: 'Anuncios (adsets)' if x == 'adset' else 'Campañas',
            key="level_selector"
        )
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("↻ Actualizar datos", use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ========== CONEXIÓN FACEBOOK (MULTI-CUENTA) ==========
    fb_accounts = get_fb_accounts(user_id) if user_id else []

    # Sincronizar cuenta activa al iniciar sesión
    if fb_accounts and not st.session_state.get('fb_configured', False):
        first = fb_accounts[0]
        st.session_state['active_fb_account_id'] = first['id']
        st.session_state['fb_app_id_enc']         = first['app_id_enc']
        st.session_state['fb_token_enc']           = first['access_token_enc']
        st.session_state['fb_account_enc']         = first['account_id_enc']
        st.session_state['fb_configured']          = True

    with st.expander("🔑 Cuentas de Facebook Ads", expanded=not fb_accounts):
        # ---- Selector de cuenta activa ----
        if fb_accounts:
            account_labels = [
                f"{a.get('account_name') or 'Cuenta'} #{a['id']}" for a in fb_accounts
            ]
            active_idx = 0
            active_id = st.session_state.get('active_fb_account_id')
            for i, a in enumerate(fb_accounts):
                if a['id'] == active_id:
                    active_idx = i
                    break

            selected_idx = st.selectbox(
                "Cuenta activa",
                range(len(account_labels)),
                format_func=lambda i: account_labels[i],
                index=active_idx,
                key="fb_account_selector"
            )
            selected_account = fb_accounts[selected_idx]

            if selected_account['id'] != st.session_state.get('active_fb_account_id'):
                st.session_state['active_fb_account_id'] = selected_account['id']
                st.session_state['fb_app_id_enc']         = selected_account['app_id_enc']
                st.session_state['fb_token_enc']           = selected_account['access_token_enc']
                st.session_state['fb_account_enc']         = selected_account['account_id_enc']
                st.session_state['fb_configured']          = True
                st.rerun()

            col_status, col_del = st.columns([4, 1])
            with col_status:
                st.markdown("""
                <div style="background:#ECFDF5; border:1px solid #A7F3D0;
                     border-radius:10px; padding:0.55rem 1rem; font-size:0.8rem;
                     color:#065F46;">
                    ● Cuenta conectada
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️ Eliminar", key="del_active_account", use_container_width=True):
                    delete_fb_account(selected_account['id'])
                    st.session_state.pop('active_fb_account_id', None)
                    st.session_state.pop('fb_app_id_enc', None)
                    st.session_state.pop('fb_token_enc', None)
                    st.session_state.pop('fb_account_enc', None)
                    st.session_state['fb_configured'] = False
                    st.rerun()

            st.markdown("---")

        # ---- Formulario para añadir nueva cuenta ----
        st.markdown("**Añadir cuenta de Facebook Ads**")
        st.caption("Necesitas una App en developers.facebook.com con permisos `ads_read`")

        col1, col2 = st.columns(2)
        with col1:
            new_name    = st.text_input("Nombre de cuenta (etiqueta)", placeholder="Ej: Cliente A", key="new_fb_name")
            new_app_id  = st.text_input("App ID",    type="password",              key="new_fb_app_id")
            new_account = st.text_input("Account ID", placeholder="act_123456789", key="new_fb_account")
        with col2:
            new_token   = st.text_input("Access Token", type="password", key="new_fb_token")

        if st.button("➕ Agregar cuenta", use_container_width=True, key="add_fb_account_btn"):
            if all([new_app_id, new_token, new_account]):
                # Verificación de duplicados a nivel de sistema
                system_accounts = get_all_system_fb_accounts()
                is_duplicate = False
                for acc in system_accounts:
                    decrypted_id = decrypt_text(acc['account_id_enc'])
                    if decrypted_id == new_account:
                        is_duplicate = True
                        break
                
                if is_duplicate:
                    st.error("❌ Este Account ID ya está registrado en otra cuenta del sistema. No se puede reutilizar en el periodo de prueba.")
                else:
                    enc_app_id  = encrypt_text(new_app_id)
                    enc_token   = encrypt_text(new_token)
                    enc_account = encrypt_text(new_account)
                    add_fb_account(user_id, enc_app_id, enc_token, enc_account, account_name=new_name)
                    # Activar la cuenta recién añadida
                    new_accounts = get_fb_accounts(user_id)
                    if new_accounts:
                        newest = new_accounts[-1]
                        st.session_state['active_fb_account_id'] = newest['id']
                        st.session_state['fb_app_id_enc']         = newest['app_id_enc']
                        st.session_state['fb_token_enc']           = newest['access_token_enc']
                        st.session_state['fb_account_enc']         = newest['account_id_enc']
                        st.session_state['fb_configured']          = True
                    st.success("✅ Cuenta agregada y activada")
                    st.rerun()
            else:
                st.error("Completa App ID, Access Token y Account ID")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not st.session_state.get('fb_configured', False):
        st.markdown("""
        <div style="background: #e7f3ff; border: 1px solid #bde4ff;
             border-radius:8px; padding:2rem; text-align:center;">
            <div style="font-family:'Segoe UI', 'Roboto', sans-serif; font-size:1.1rem; font-weight:700;
                 color:#1877F2; margin-bottom:0.5rem;">Conecta tu cuenta de Facebook Ads</div>
            <div style="font-size:0.85rem; color:#1c1e21;">
                Configura tus credenciales arriba para comenzar el análisis.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # ========== FECHAS ==========
    today = date.today()
    max_days_allowed = 30 if plan == 'basic' else 90 if plan == 'pro' else 365

    if date_range is not None and len(date_range) >= 2:
        date_from = date_range[0].isoformat()
        date_to   = date_range[1].isoformat()
        days_selected = (date_range[1] - date_range[0]).days + 1
        if days_selected > max_days_allowed:
            st.warning(f"⚠️ Tu plan {plan.upper()} permite máximo {max_days_allowed} días")
            date_from = (today - timedelta(days=max_days_allowed - 1)).isoformat()
            date_to   = today.isoformat()
    else:
        date_from = (today - timedelta(days=min(29, max_days_allowed - 1))).isoformat()
        date_to   = today.isoformat()

    # ========== CREDENCIALES ==========
    fb_app_id  = decrypt_text(st.session_state.get('fb_app_id_enc', ''))
    fb_token   = decrypt_text(st.session_state.get('fb_token_enc', ''))
    fb_account = decrypt_text(st.session_state.get('fb_account_enc', ''))

    # ========== DATOS ==========
    try:
        with st.spinner("Cargando datos…"):
            client = FacebookClient(app_id=fb_app_id, access_token=fb_token, ad_account_id=fb_account)
            raw    = client.get_ads_insights(date_from, date_to, level=level)
            df     = pd.DataFrame(raw)

            if df.empty:
                st.warning("No hay anuncios activos en el período seleccionado.")
                return

            # Agrupar según el nivel seleccionado
            if 'campaign_id' in df.columns:
                sum_cols  = [c for c in ['impressions', 'clicks', 'spend', 'reach'] if c in df.columns]
                if level == 'adset' and 'adset_id' in df.columns:
                    group_cols = ['campaign_id', 'adset_id']
                    text_cols = [c for c in ['campaign_name', 'adset_name', 'objective'] if c in df.columns]
                else:
                    group_cols = ['campaign_id']
                    text_cols = [c for c in ['campaign_name', 'objective'] if c in df.columns]

                # frequency NO se incluye en agg: se recalcula desde impressions/reach sumados
                if 'frequency' in df.columns:
                    df = df.drop(columns=['frequency'])
                agg_dict = {**{c: 'sum' for c in sum_cols}, **{c: 'first' for c in text_cols}}

                before   = len(df)
                df       = df.groupby(group_cols, as_index=False).agg(agg_dict)
                label = 'adsets' if level == 'adset' else 'campañas'
                st.info(f"📊 {before} registros agregados → {len(df)} {label} únicas")

            df = calculate_kpis(df)
            df = add_recommendations(df)

            total_ads = len(df)
            days_selected = (date.today() - date.fromisoformat(date_from)).days + 1
            df, plan_limits = check_plan_limits(df, plan, days_selected)

            # ===== DATOS PARA NUEVA JERARQUÍA =====
            score_data = calculate_account_health_score(df)
            actions = get_priority_actions(df)

            # ===== 1. ACTION CENTER (arriba de todo) =====
            render_action_center(actions)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== 2. ACCOUNT STATUS (simple) =====
            render_account_status_simple(score_data)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== 3. TOP INSIGHTS =====
            render_top_insights(df)
            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== 4. DETALLED ANALYSIS (colapsable) =====
            st.markdown('<div class="section-label">Detalle</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📊 Análisis Detallado</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.8rem;color:rgba(232,230,240,0.4);margin-bottom:1rem;">Métricas avanzadas y visualizaciones para análisis profundo.</div>', unsafe_allow_html=True)

            # KPI Grid (8 métricas) - dentro de expander
            with st.expander("📈 KPIs Principales", expanded=False):
                render_kpi_grid(df, total_ads, level)
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Charts - dentro de expander
            with st.expander("📊 Gráficos de Desempeño", expanded=False):
                render_spend_charts(df, level)
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Salud de inversión - dentro de expander
            with st.expander("💰 Salud de Inversión", expanded=False):
                render_health_indicator(df)
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Tendencias semanales (si hay datos)
            has_date_data = 'date_start' in df.columns and not df['date_start'].isna().all()
            if has_date_data:
                with st.expander("📈 Tendencias Semanales", expanded=False):
                    trends = calculate_weekly_trends(df)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("CTR última semana", f"{trends['last_week']['ctr']:.2f}%",
                                  delta=f"{trends['ctr_change']:+.1f}% vs semana anterior",
                                  delta_color="normal" if trends['ctr_change'] >= 0 else "inverse")
                    with col2:
                        st.metric("CPC última semana", f"${trends['last_week']['cpc']:.2f}",
                                  delta=f"{trends['cpc_change']:+.1f}% vs semana anterior",
                                  delta_color="inverse" if trends['cpc_change'] >= 0 else "normal")
                    with col3:
                        st.metric("Gasto última semana", f"${trends['last_week']['spend']:,.2f}",
                                  delta=f"{trends['spend_change']:+.1f}% vs semana anterior")
                    st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # Mapa de saturación - dentro de expander
            with st.expander("🗺️ Mapa de Saturación", expanded=False):
                render_frequency_panel(df, level)
                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # ===== ANÁLISIS POR CAMPAÑA/ADSET =====
            star_analysis = generate_star_campaign_analysis(df)
            detailed      = generate_detailed_insights(df)

            # Campaña / Adset estrella - dentro de expander
            if star_analysis:
                with st.expander("⭐ Campaña Destacada", expanded=False):
                    star = star_analysis
                    if star['action_level'] == 'agresivo':
                        card_cls, badge_cls, badge_text = 'elite',   'elite',   '♛ Estrella — Escalar'
                    elif star['action_level'] == 'moderado':
                        card_cls, badge_cls, badge_text = 'solid',   'solid',   '⭐ Sólida — Optimizar'
                    else:
                        card_cls, badge_cls, badge_text = 'improve', 'improve', '◎ Mejorable — Revisar'

                    st.markdown('<div class="section-label">Destacada</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="star-card {card_cls}">
                        <div class="star-badge {badge_cls}">{badge_text}</div>
                        <div class="star-name">{star['name'][:55]}</div>
                        <div class="star-obj">Objetivo: {get_objective_label(star['objective'])}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("CTR", f"{star['ctr']:.2f}%",
                                  delta=f"bench {star['benchmark_ctr']:.1f}%",
                                  delta_color="normal" if star['ctr'] >= star['benchmark_ctr'] else "inverse")
                    with c2:
                        st.metric("CPC", f"${star['cpc']:.2f}" if star['cpc'] > 0 else "N/A",
                                  delta=f"bench ${star['benchmark_cpc']:.2f}",
                                  delta_color="normal" if 0 < star['cpc'] <= star['benchmark_cpc'] else "inverse")
                    with c3:
                        st.metric("Frecuencia", f"{star['frequency']:.1f}x")
                    with c4:
                        st.metric("Gasto", f"${star['spend']:,.2f}")

                    roi_estimate = estimate_roi_potential(pd.Series(star))
                    if roi_estimate and roi_estimate['estimated_conversions'] > 0:
                        st.markdown(f"""
                        <div class="roi-box">
                            <div class="roi-box-title">Estimación de ROI Potencial</div>
                            <div class="roi-row">Tasa de conversión estimada: <strong style="color:#F5F3FF;">{roi_estimate['conversion_rate_used']:.1f}%</strong></div>
                            <div class="roi-row">▸ ~{roi_estimate['estimated_conversions']:,} conversiones proyectadas</div>
                            <div class="roi-row">▸ Ingreso estimado: <strong style="color:#065F46;">${roi_estimate['estimated_revenue']:,.2f}</strong></div>
                            <div class="roi-row">▸ ROAS estimado: <strong style="color:#065F46;">{roi_estimate['estimated_roas']:.1f}x</strong></div>
                            <div class="roi-note">Estimación basada en promedios del mercado. Los resultados reales pueden variar.</div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="rec-box">
                        <div class="rec-title" style="color:{'#065F46' if card_cls=='elite' else '#1877F2' if card_cls=='solid' else '#92400E'};">{star['recommendation']}</div>
                        <div class="rec-text">📈 {star['projection']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown('<div style="margin-top:1rem; border-top:1px solid rgba(255,255,255,0.06); padding-top:1rem;"></div>', unsafe_allow_html=True)
                    st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#F5F3FF; margin-bottom:0.5rem;">Próximos pasos recomendados:</div>', unsafe_allow_html=True)
                    for step in star['next_steps']:
                        st.markdown(f"<div style='font-size:0.85rem; color:#1c1e21; padding-left:1rem; margin-bottom:0.25rem;'>{step}</div>", unsafe_allow_html=True)

                st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            # ===== ANÁLISIS DETALLADO POR CAMPAÑA =====
            render_campaign_cards_v2(detailed, level, plan_limits)
            st.markdown('<div style="margin:1rem 0;"></div>', unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== TABLA DE BENCHMARKS =====
            st.markdown('<div class="section-label">Comparativa</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Métricas vs Benchmarks del Sector</div>', unsafe_allow_html=True)
            render_benchmark_table(df, level)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== TABLA DE DATOS + EXPORT =====
            if plan_limits['can_see_alerts']:
                st.markdown('<div class="section-label">Datos</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-title">Tabla Completa</div>', unsafe_allow_html=True)
                render_performance_table(df, plan, plan_limits)

            if plan_limits['can_export']:
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                export_cols = [c for c in ['adset_name', 'campaign_name', 'objective',
                                            'spend', 'impressions', 'reach', 'clicks',
                                            'ctr', 'cpc', 'cpm', 'frequency', 'roas'] if c in df.columns]
                csv = df[export_cols].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "↓ Exportar reporte completo (CSV)",
                    csv,
                    f"ads_report_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    use_container_width=False
                )

    except Exception as e:
        st.markdown(f"""
        <div style="background: #fae0e0; border: 1px solid #f5c0c0;
             border-radius:8px; padding:1.25rem; font-size:0.875rem; color:#dd3c10;">
            <strong>Error al cargar datos</strong><br>
            <span style="color:#1c1e21;">{e}</span>
        </div>
        """, unsafe_allow_html=True)
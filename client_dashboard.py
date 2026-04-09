import streamlit as st
import os
from datetime import date, timedelta, datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from cryptography.fernet import Fernet

from facebook_client import FacebookClient
from analyzer import (
    calculate_kpis,
    add_recommendations,
    generate_insights,
    get_objective_label,
    generate_detailed_insights,
    generate_star_campaign_analysis,
    calculate_weekly_trends,
    estimate_roi_potential
)
from config import format_currency
from auth import logout
from database import save_user_credentials, get_user_by_id

ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'tu-clave-secreta-aqui')

def encrypt_text(text: str) -> str:
    if not text:
        return ""
    f = Fernet(ENCRYPTION_KEY.encode())
    return f.encrypt(text.encode()).decode()

def decrypt_text(encrypted: str) -> str:
    if not encrypted:
        return ""
    f = Fernet(ENCRYPTION_KEY.encode())
    return f.decrypt(encrypted.encode()).decode()


# ========== CSS PREMIUM (compartido con app.py) ==========
DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Satoshi:wght@300;400;500;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }
body, .stApp { background: #080810 !important; color: #E8E6F0; font-family: 'Satoshi', sans-serif; }
h1,h2,h3,h4 { font-family: 'Satoshi', sans-serif; }

/* ---- HEADER BAR ---- */
.dash-header {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2rem;
    gap: 1rem;
}
.dash-logo {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.1rem;
    font-weight: 800;
    color: #F5F3FF;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.dash-logo .logo-mark {
    width: 28px; height: 28px;
    background: linear-gradient(135deg, #C9A84C, #8A6AE0);
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
}
.dash-company {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: #F5F3FF;
}
.dash-sub {
    font-size: 0.85rem;
    color: rgba(232,230,240,0.4);
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
.plan-basic  { background: rgba(136,135,128,0.15); border: 1px solid rgba(136,135,128,0.3); color: #B4B2A9; }
.plan-pro    { background: rgba(138,106,224,0.15); border: 1px solid rgba(138,106,224,0.35); color: #A890F0; }
.plan-enterprise { background: rgba(201,168,76,0.15); border: 1px solid rgba(201,168,76,0.35); color: #C9A84C; }

/* ---- METRIC CARDS ---- */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 16px 16px;
}
.metric-card.green::after  { background: linear-gradient(90deg, transparent, #64DC96, transparent); }
.metric-card.gold::after   { background: linear-gradient(90deg, transparent, #C9A84C, transparent); }
.metric-card.purple::after { background: linear-gradient(90deg, transparent, #8A6AE0, transparent); }
.metric-card.blue::after   { background: linear-gradient(90deg, transparent, #60A5FA, transparent); }
.metric-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(232,230,240,0.35);
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1;
}
.metric-value.green  { color: #64DC96; }
.metric-value.gold   { color: #C9A84C; }
.metric-value.purple { color: #A890F0; }
.metric-value.blue   { color: #60A5FA; }
.metric-value.red    { color: #FC8181; }
.metric-value.white  { color: #F5F3FF; }

/* ---- SECTION HEADERS ---- */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8A6AE0;
    margin-bottom: 0.4rem;
}
.section-title {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F5F3FF;
    margin-bottom: 1.25rem;
}
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 2rem 0; }

/* ---- FILTER STRIP ---- */
.filter-strip {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}

/* ---- EXPANDER / CARD ---- */
.panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.panel-title {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #F5F3FF;
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
    border-radius: 14px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.health-card.optimal  { background: rgba(100,220,150,0.08); border: 1px solid rgba(100,220,150,0.2); }
.health-card.warning  { background: rgba(251,191,36,0.08);  border: 1px solid rgba(251,191,36,0.2); }
.health-card.critical { background: rgba(252,129,129,0.08); border: 1px solid rgba(252,129,129,0.2); }
.health-dot { font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; margin-bottom: 0.4rem; }
.health-dot.optimal  { color: #64DC96; }
.health-dot.warning  { color: #FBbf24; }
.health-dot.critical { color: #FC8181; }
.health-pct {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.75rem;
    font-weight: 800;
    line-height: 1;
}
.health-pct.optimal  { color: #64DC96; }
.health-pct.warning  { color: #FBbf24; }
.health-pct.critical { color: #FC8181; }
.health-amount { font-size: 0.78rem; color: rgba(232,230,240,0.4); margin-top: 0.25rem; }
.health-note {
    font-size: 0.65rem;
    color: rgba(232,230,240,0.3);
    margin-top: 0.25rem;
}

/* ---- STAR CAMPAIGN ---- */
.star-card {
    border-radius: 20px;
    padding: 1.75rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}
.star-card.elite    { background: rgba(100,220,150,0.08); border: 1px solid rgba(100,220,150,0.25); }
.star-card.solid    { background: rgba(96,165,250,0.08);  border: 1px solid rgba(96,165,250,0.25); }
.star-card.improve  { background: rgba(251,191,36,0.08);  border: 1px solid rgba(251,191,36,0.25); }
.star-badge {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.star-badge.elite   { color: #64DC96; }
.star-badge.solid   { color: #60A5FA; }
.star-badge.improve { color: #FBbf24; }
.star-name {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #F5F3FF;
    margin-bottom: 0.3rem;
}
.star-obj { font-size: 0.82rem; color: rgba(232,230,240,0.45); }

/* ---- ROI BOX ---- */
.roi-box {
    background: rgba(100,220,150,0.06);
    border: 1px solid rgba(100,220,150,0.15);
    border-radius: 14px;
    padding: 1.25rem;
    margin-top: 1rem;
}
.roi-box-title { font-family: 'Satoshi', sans-serif; font-size: 0.85rem; font-weight: 700; color: #64DC96; margin-bottom: 0.6rem; }
.roi-row { font-size: 0.85rem; color: rgba(232,230,240,0.65); padding: 0.2rem 0; }
.roi-note { font-size: 0.72rem; color: rgba(232,230,240,0.3); margin-top: 0.5rem; }

/* ---- RECOMMENDATION BOX ---- */
.rec-box {
    background: rgba(138,106,224,0.06);
    border: 1px solid rgba(138,106,224,0.18);
    border-radius: 14px;
    padding: 1.25rem;
    margin-top: 0.75rem;
}
.rec-title { font-family: 'Satoshi', sans-serif; font-size: 0.9rem; font-weight: 700; color: #A890F0; margin-bottom: 0.4rem; }
.rec-text  { font-size: 0.85rem; color: rgba(232,230,240,0.6); }

/* ---- ALERT BOX ---- */
.alert-box {
    background: rgba(252,129,129,0.06);
    border: 1px solid rgba(252,129,129,0.2);
    border-left: 3px solid #FC8181;
    border-radius: 0 14px 14px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.alert-title { font-family: 'Satoshi', sans-serif; font-size: 0.82rem; font-weight: 700; color: #FC8181; margin-bottom: 0.25rem; }
.alert-body  { font-size: 0.82rem; color: rgba(232,230,240,0.55); }

/* ---- CAMPAIGN ROW ---- */
.camp-card {
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid;
}
.camp-card.high   { background: rgba(252,129,129,0.05); border-color: #FC8181; }
.camp-card.medium { background: rgba(251,191,36,0.05);  border-color: #FBbf24; }
.camp-card.low    { background: rgba(100,220,150,0.05); border-color: #64DC96; }
.camp-name { font-family: 'Satoshi', sans-serif; font-size: 0.95rem; font-weight: 700; color: #F5F3FF; margin-bottom: 0.75rem; }
.camp-table { width: 100%; font-size: 0.8rem; border-collapse: collapse; }
.camp-table td { padding: 0.3rem 0.5rem 0.3rem 0; color: rgba(232,230,240,0.55); vertical-align: top; }
.camp-table td strong { color: rgba(232,230,240,0.8); display: block; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.15rem; }

/* ---- PLAN SIDEBAR ---- */
.plan-panel {
    border-radius: 16px;
    padding: 1.25rem;
    margin-top: 1rem;
}
.plan-panel.basic      { background: rgba(136,135,128,0.07); border: 1px solid rgba(136,135,128,0.15); }
.plan-panel.pro        { background: rgba(138,106,224,0.07); border: 1px solid rgba(138,106,224,0.2); }
.plan-panel.enterprise { background: rgba(201,168,76,0.07);  border: 1px solid rgba(201,168,76,0.2); }
.plan-name {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #F5F3FF;
    margin-bottom: 0.75rem;
}
.plan-item { font-size: 0.8rem; color: rgba(232,230,240,0.55); padding: 0.22rem 0; }
.plan-item.ok  { color: rgba(100,220,150,0.85); }
.plan-item.off { color: rgba(232,230,240,0.25); }

/* ---- STREAMLIT OVERRIDES ---- */
.stButton > button {
    background: linear-gradient(135deg, #8A6AE0 0%, #6A4AC0 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Satoshi', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }
.stExpander { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 14px !important; }
div[data-testid="stExpander"] > div:first-child { border-radius: 14px !important; }
.stDateInput input, .stTextInput input, .stSelectbox select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #E8E6F0 !important;
    border-radius: 10px !important;
}
.stRadio label { color: rgba(232,230,240,0.7) !important; }
.stMetric label { color: rgba(232,230,240,0.45) !important; font-size: 0.75rem !important; }
.stMetric [data-testid="metric-container"] > div:nth-child(2) { color: #F5F3FF !important; }
div[data-testid="stSidebar"] { background: #0D0D18 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
</style>
"""


def check_plan_limits(df: pd.DataFrame, plan: str, date_range_days: int):
    plan = plan.lower() if plan else 'basic'
    limits = {
        'basic':      {'max_campaigns': 3,      'max_days': 30,  'can_export': False, 'can_see_alerts': False},
        'pro':        {'max_campaigns': 20,     'max_days': 90,  'can_export': True,  'can_see_alerts': True},
        'enterprise': {'max_campaigns': 999999, 'max_days': 365, 'can_export': True,  'can_see_alerts': True}
    }
    limit = limits.get(plan, limits['basic'])

    if len(df) > limit['max_campaigns']:
        st.warning(f"⚠️ Tu plan {plan.upper()} muestra solo las {limit['max_campaigns']} mejores campañas")
        df = df.nlargest(limit['max_campaigns'], 'spend')

    if date_range_days > limit['max_days']:
        st.warning(f"⚠️ Tu plan {plan.upper()} permite máximo {limit['max_days']} días de historial")

    return df, limit


def render_metric_cards(df: pd.DataFrame):
    total_spend   = df['spend'].sum() if 'spend' in df.columns else 0
    conversions   = df['conversion_metric'].sum() if 'conversion_metric' in df.columns else 0
    roas          = df['roas'].mean() if 'roas' in df.columns else 0
    num_campaigns = len(df)

    roas_class = "green" if roas >= 2 else "gold" if roas >= 1 else "red"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card gold">
            <div class="metric-label">Inversión total</div>
            <div class="metric-value gold">{format_currency(total_spend)}</div>
        </div>
        <div class="metric-card purple">
            <div class="metric-label">Resultados</div>
            <div class="metric-value purple">{int(conversions):,}</div>
        </div>
        <div class="metric-card {'green' if roas >= 2 else 'blue'}">
            <div class="metric-label">ROAS Promedio</div>
            <div class="metric-value {roas_class}">{roas:.2f}x</div>
        </div>
        <div class="metric-card blue">
            <div class="metric-label">Campañas activas</div>
            <div class="metric-value blue">{num_campaigns}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


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
    display_cols = ['campaign_name', 'objective', 'spend', 'roas', 'ctr', 'cpc']
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
        'campaign_name': 'Campaña', 'objective': 'Objetivo', 'spend': 'Gasto',
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
            para ver recomendaciones personalizadas por campaña.
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
        icon, label = "◈", "Plan Basic"
        items = [
            ("ok",  "✓ 3 campañas máximo"),
            ("ok",  "✓ 30 días de historial"),
            ("off", "✗ Sin exportación"),
            ("off", "✗ Sin alertas avanzadas"),
        ]
        upgrade = '<div style="margin-top:0.75rem;font-size:0.75rem;color:rgba(138,106,224,0.7);">⬆ Mejorar a PRO</div>'
    elif plan == 'pro':
        icon, label = "⭐", "Plan Pro"
        items = [
            ("ok", "✓ 20 campañas máximo"),
            ("ok", "✓ 90 días de historial"),
            ("ok", "✓ Exportación a CSV"),
            ("ok", "✓ Alertas avanzadas"),
        ]
        upgrade = ''
    else:
        icon, label = "♛", "Plan Enterprise"
        items = [
            ("ok", "✓ Campañas ilimitadas"),
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
            <div class="dash-logo"><div class="logo-mark">◈</div> Ads Intelligence</div>
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

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Plan info en sidebar
    with st.sidebar:
        st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
        st.markdown('<div class="dash-logo" style="padding:1rem 0 0.5rem;"><div class="logo-mark">◈</div> Ads Intelligence</div>', unsafe_allow_html=True)
        render_plan_info(plan)

    # ========== FILTROS ==========
    st.markdown('<div class="section-label">Análisis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Filtros de análisis</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        today = date.today()
        max_days = 30 if plan == 'basic' else 90 if plan == 'pro' else 365
        date_range = st.date_input(
            "Rango de fechas",
            [today - timedelta(days=min(29, max_days - 1)), today],
            key="date_range_filter"
        )
    with col2:
        level = st.radio(
            "Nivel de análisis",
            ["Campañas", "Conjuntos de anuncios"],
            horizontal=True,
            key="level_filter"
        )
        level = "campaign" if level == "Campañas" else "adset"
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        refresh = st.button("↻ Actualizar datos", use_container_width=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ========== CONEXIÓN FACEBOOK ==========
    with st.expander("🔑 Configurar conexión Facebook Ads", expanded=not st.session_state.get('fb_configured', False)):
        st.markdown("""
        **Para conectar tu cuenta de Facebook Ads necesitas:**
        1. Crear una App en [developers.facebook.com](https://developers.facebook.com)
        2. Obtener un Access Token con permisos `ads_read`
        3. Copiar tu Account ID (empieza con `act_`)
        """)

        col1, col2 = st.columns(2)
        with col1:
            fb_app_id  = st.text_input("App ID",       type="password",              key="fb_app_id_input")
            fb_account = st.text_input("Account ID",   placeholder="act_123456789", key="fb_account_input")
        with col2:
            fb_token   = st.text_input("Access Token", type="password",              key="fb_token_input")

        if st.button("Guardar credenciales", use_container_width=True):
            if all([fb_app_id, fb_token, fb_account]):
                enc_app_id  = encrypt_text(fb_app_id)
                enc_token   = encrypt_text(fb_token)
                enc_account = encrypt_text(fb_account)

                save_user_credentials(st.session_state['user_id'], enc_app_id, enc_token, enc_account)

                st.session_state['fb_configured']   = True
                st.session_state['fb_app_id_enc']   = enc_app_id
                st.session_state['fb_token_enc']    = enc_token
                st.session_state['fb_account_enc']  = enc_account
                st.success("✅ Credenciales guardadas")
                st.rerun()
            else:
                st.error("Completa todos los campos")

    if st.session_state.get('fb_configured', False):
        st.markdown("""
        <div style="background:rgba(100,220,150,0.06); border:1px solid rgba(100,220,150,0.2);
             border-radius:12px; padding:0.75rem 1rem; font-size:0.82rem;
             color:rgba(100,220,150,0.85); margin-bottom:0.75rem;">
            ● Facebook Ads conectado correctamente
        </div>
        """, unsafe_allow_html=True)
        if st.button("↺ Cambiar credenciales"):
            st.session_state['fb_configured'] = False
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if not st.session_state.get('fb_configured', False):
        st.markdown("""
        <div style="background:rgba(138,106,224,0.06); border:1px solid rgba(138,106,224,0.18);
             border-radius:16px; padding:2rem; text-align:center;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
                 color:#A890F0; margin-bottom:0.5rem;">Conecta tu cuenta de Facebook Ads</div>
            <div style="font-size:0.85rem; color:rgba(232,230,240,0.4);">
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

    os.environ['APP_ID']        = fb_app_id
    os.environ['ACCESS_TOKEN']  = fb_token
    os.environ['AD_ACCOUNT_ID'] = fb_account

    # ========== DATOS ==========
    try:
        with st.spinner("Cargando datos…"):
            client = FacebookClient()
            raw    = client.get_ads_insights(date_from, date_to, level=level)
            df     = pd.DataFrame(raw)

            if df.empty:
                st.warning("No hay campañas activas en el período seleccionado.")
                return

            # Agrupar por campaña
            if 'campaign_id' in df.columns:
                sum_cols  = [c for c in ['impressions', 'clicks', 'spend'] if c in df.columns]
                avg_cols  = [c for c in ['ctr', 'cpc', 'cpm', 'frequency'] if c in df.columns]
                text_cols = [c for c in ['campaign_name', 'objective'] if c in df.columns]

                agg_dict = {**{c: 'sum' for c in sum_cols}, **{c: 'mean' for c in avg_cols}, **{c: 'first' for c in text_cols}}
                before   = len(df)
                df       = df.groupby('campaign_id', as_index=False).agg(agg_dict)
                st.info(f"📊 {before} registros diarios → {len(df)} campañas únicas")

            df = calculate_kpis(df)
            df = add_recommendations(df)

            days_selected = (date.today() - date.fromisoformat(date_from)).days + 1
            df, plan_limits = check_plan_limits(df, plan, days_selected)

            # ===== TÍTULO =====
            st.markdown(f"""
            <div style="padding: 0.5rem 0 1.5rem;">
                <div class="section-label">Dashboard</div>
                <div style="font-family:'Syne',sans-serif; font-size:1.9rem; font-weight:800;
                     letter-spacing:-0.03em; color:#F5F3FF;">Intelligence Report</div>
                <div style="font-size:0.82rem; color:rgba(232,230,240,0.35); margin-top:0.3rem;">
                    {date_from} → {date_to} · {len(df)} campañas
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ===== MÉTRICAS =====
            render_metric_cards(df)

            # ===== SALUD =====
            render_health_indicator(df)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # ===== ANÁLISIS AVANZADO =====
            st.markdown('<div class="section-label">Intelligence</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Análisis Detallado</div>', unsafe_allow_html=True)

            star_analysis = generate_star_campaign_analysis(df)
            detailed      = generate_detailed_insights(df)
            has_date_data = 'date_start' in df.columns and not df['date_start'].isna().all()

            # --- TENDENCIAS SEMANALES ---
            if has_date_data:
                st.markdown('<div class="section-label" style="margin-top:0.5rem;">Tendencias</div>', unsafe_allow_html=True)
                trends = calculate_weekly_trends(df)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CTR", f"{trends['last_week']['ctr']:.2f}%",
                              delta=f"{trends['ctr_change']:+.1f}%",
                              delta_color="normal" if trends['ctr_change'] >= 0 else "inverse")
                with col2:
                    st.metric("CPC", f"${trends['last_week']['cpc']:.2f}",
                              delta=f"{trends['cpc_change']:+.1f}%",
                              delta_color="inverse" if trends['cpc_change'] >= 0 else "normal")
                with col3:
                    st.metric("Gasto", f"${trends['last_week']['spend']:.2f}",
                              delta=f"{trends['spend_change']:+.1f}%")

                st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # --- ALERTAS DE FRECUENCIA ---
            high_freq = df[df['frequency'] > 5] if 'frequency' in df.columns else pd.DataFrame()
            if not high_freq.empty:
                st.markdown('<div class="section-label">Alertas</div>', unsafe_allow_html=True)
                for _, row in high_freq.iterrows():
                    st.markdown(f"""
                    <div class="alert-box">
                        <div class="alert-title">⚠ Saturación de frecuencia detectada</div>
                        <div class="alert-body"><strong>{row['campaign_name']}</strong> — Frecuencia: {row['frequency']:.1f} · Cambiar creatividad urgentemente</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # --- RESUMEN GENERAL ---
            st.markdown(f"""
            <div style="background:rgba(138,106,224,0.05); border:1px solid rgba(138,106,224,0.15);
                 border-radius:14px; padding:1rem 1.25rem; font-size:0.875rem;
                 color:rgba(232,230,240,0.6); margin-bottom:1.25rem;">
                {detailed['summary']}
            </div>
            """, unsafe_allow_html=True)

            # --- CAMPAÑA ESTRELLA ---
            if star_analysis:
                star = star_analysis
                if star['action_level'] == 'agresivo':
                    card_cls, badge_cls, badge_text = 'elite',   'elite',   '♛ Campaña Estrella — Escalar'
                elif star['action_level'] == 'moderado':
                    card_cls, badge_cls, badge_text = 'solid',   'solid',   '⭐ Campaña Sólida — Optimizar'
                else:
                    card_cls, badge_cls, badge_text = 'improve', 'improve', '◎ Campaña Mejorable — Revisar'

                st.markdown(f"""
                <div class="star-card {card_cls}">
                    <div class="star-badge {badge_cls}">{badge_text}</div>
                    <div class="star-name">{star['name'][:50]}</div>
                    <div class="star-obj">🎯 Objetivo: {star['objective']}</div>
                </div>
                """, unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("CTR", f"{star['ctr']:.2f}%",
                              delta=star['ctr_message'][:40], delta_color="normal")
                    st.caption(f"Benchmark: {star['benchmark_ctr']:.1f}%")
                with col2:
                    st.metric("CPC", f"${star['cpc']:.2f}",
                              delta=star['cpc_message'][:40], delta_color="normal")
                    st.caption(f"Benchmark: ${star['benchmark_cpc']:.2f}")
                with col3:
                    st.metric("Frecuencia", f"{star['frequency']:.1f}",
                              delta=star['frequency_message'], delta_color="normal")

                roi_estimate = estimate_roi_potential(pd.Series(star))
                if roi_estimate and roi_estimate['estimated_conversions'] > 0:
                    st.markdown(f"""
                    <div class="roi-box">
                        <div class="roi-box-title">💰 Estimación de ROI Potencial</div>
                        <div class="roi-row">Tasa de conversión estimada: <strong style="color:#F5F3FF;">{roi_estimate['conversion_rate_used']:.1f}%</strong></div>
                        <div class="roi-row">▸ ~{roi_estimate['estimated_conversions']:,} conversiones proyectadas</div>
                        <div class="roi-row">▸ Ingreso estimado: <strong style="color:#64DC96;">${roi_estimate['estimated_revenue']:,.2f}</strong></div>
                        <div class="roi-row">▸ ROAS estimado: <strong style="color:#64DC96;">{roi_estimate['estimated_roas']:.1f}x</strong></div>
                        <div class="roi-note">⚠ Estimación basada en promedios del mercado. Los resultados reales pueden variar.</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="rec-box">
                    <div class="rec-title">🎯 {star['recommendation']}</div>
                    <div class="rec-text">📈 Proyección: {star['projection']}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("📋 Próximos pasos recomendados"):
                    for step in star['next_steps']:
                        st.markdown(step)

                st.caption(f"💡 {star['verdict']}")

            if detailed['high_priority_count'] > 0:
                st.markdown(f"""
                <div style="background:rgba(252,129,129,0.07); border:1px solid rgba(252,129,129,0.2);
                     border-radius:12px; padding:0.75rem 1rem; font-size:0.82rem;
                     color:rgba(252,129,129,0.85); margin:1rem 0;">
                    ⚠ Hay <strong>{detailed['high_priority_count']}</strong> campañas que requieren atención inmediata.
                </div>
                """, unsafe_allow_html=True)

            st.markdown('<hr class="divider">', unsafe_allow_html=True)

            # --- ANÁLISIS POR CAMPAÑA ---
            st.markdown('<div class="section-label">Detalle</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-title">Análisis por Campaña</div>', unsafe_allow_html=True)

            for camp in detailed['campaigns']:
                priority_map = {
                    'alta':  ('high',   '🔴'),
                    'media': ('medium', '🟡'),
                }
                card_cls, icon = priority_map.get(camp['priority'], ('low', '🟢'))

                with st.expander(f"{icon} {camp['campaign_name'][:55]}  ·  ${camp['spend']:.2f}"):
                    st.markdown(f"""
                    <div class="camp-card {card_cls}">
                        <table class="camp-table">
                            <tr>
                                <td style="width:33%"><strong>Objetivo</strong>{camp['objective']}</td>
                                <td style="width:33%"><strong>CTR</strong>{camp['ctr']:.2f}%
                                    <span style="font-size:0.72rem;color:rgba(232,230,240,0.4);display:block;">{camp['ctr_message']}</span>
                                </td>
                                <td style="width:33%"><strong>CPC</strong>${camp['cpc']:.2f}
                                    <span style="font-size:0.72rem;color:rgba(232,230,240,0.4);display:block;">{camp['cpc_message']}</span>
                                </td>
                            </tr>
                            <tr>
                                <td><strong>Frecuencia</strong>{camp['frequency_message']}</td>
                                <td colspan="2"><strong>Acción recomendada</strong>{camp['action']}
                                    <span style="font-size:0.72rem;color:rgba(232,230,240,0.4);display:block;">{camp['action_detail']}</span>
                                </td>
                            </tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)

            # --- EXPORTAR ---
            if plan_limits['can_export']:
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                csv = df[['campaign_name', 'objective', 'spend', 'roas', 'ctr', 'cpc']].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "↓ Exportar a CSV",
                    csv,
                    f"reporte_{datetime.now().strftime('%Y%m%d')}.csv",
                    use_container_width=False
                )

    except Exception as e:
        st.markdown(f"""
        <div style="background:rgba(252,129,129,0.07); border:1px solid rgba(252,129,129,0.2);
             border-radius:14px; padding:1.25rem; font-size:0.875rem; color:#FC8181;">
            <strong>Error al cargar datos</strong><br>
            <span style="color:rgba(232,230,240,0.4);">{e}</span>
        </div>
        """, unsafe_allow_html=True)
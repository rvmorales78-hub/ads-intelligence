import os
from datetime import date, datetime, timedelta
from typing import Any, cast

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analyzer import add_recommendations, calculate_kpis, generate_insights
from config import format_currency, get_today_str, logger, validate_env
from env_manager import delete_env_keys, delete_profile, load_env_values, load_profiles, save_env_values, save_profile
from facebook_client import FacebookClient
from storage import StorageManager

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================
# El set_page_config se define en landing.py para evitar duplicados en la app principal.
# st.set_page_config(
#     page_title='Ads Intelligence',
#     page_icon='📊',
#     layout='wide',
#     initial_sidebar_state='expanded'
# )

# ============================================================================
# PALETA DE COLORES PROFESIONAL CON ALTO CONTRASTE
# ============================================================================
COLORS = {
    # Primarios
    'primary': '#4F46E5',      # Indigo 600
    'secondary': '#7C3AED',    # Purple 600
    'success': '#059669',      # Emerald 600
    'danger': '#DC2626',       # Red 600
    'warning': '#D97706',      # Amber 600
    'info': '#0891B2',         # Cyan 600
    
    # Fondos
    'dark': '#1E293B',         # Slate 800 - Sidebar
    'card_bg': '#E2E8F0',      # Slate 200
    'page_bg': '#CBD5E1',      # Slate 300
    'border': '#94A3B8',       # Slate 400
    
    # Textos
    'text_primary': '#0F172A',    # Slate 900
    'text_secondary': '#334155',  # Slate 700
    'text_light': '#475569',      # Slate 600
    'text_white': '#FFFFFF',      # Blanco
}

# ============================================================================
# CSS PERSONALIZADO - CONTRASTE CORREGIDO
# ============================================================================
CSS = f"""
<style>
    /* Fuente */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Fondo de página */
    .stApp {{
        background: {COLORS['page_bg']};
    }}
    
    /* ========== SIDEBAR ========== */
    [data-testid="stSidebar"] {{
        background: {COLORS['dark']};
        border-right: none;
    }}
    
    /* Texto en sidebar - BLANCO */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {{
        color: {COLORS['text_white']} !important;
    }}
    
    /* Inputs en sidebar */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea {{
        background-color: {COLORS['text_white']} !important;
        color: {COLORS['text_primary']} !important;
        border-radius: 10px !important;
        border: 1px solid #475569 !important;
    }}
    
    [data-testid="stSidebar"] input::placeholder {{
        color: {COLORS['text_light']} !important;
    }}
    
    /* Sidebar logo */
    .sidebar-logo {{
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #475569;
    }}
    
    .sidebar-logo h1 {{
        color: {COLORS['text_white']} !important;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 0;
    }}
    
    .sidebar-logo p {{
        color: {COLORS['text_white']} !important;
        font-size: 0.75rem;
        margin: 0;
    }}
    
    /* Botones en sidebar */
    [data-testid="stSidebar"] .stButton button {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_white']} !important;
        border-radius: 10px;
        font-weight: 500;
        width: 100%;
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        background-color: {COLORS['secondary']};
    }}
    
    /* Selectbox en sidebar */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
        background-color: {COLORS['text_white']};
        border-radius: 10px;
    }}
    
    /* Radio buttons en sidebar */
    [data-testid="stSidebar"] .stRadio div {{
        color: {COLORS['text_white']};
    }}
    
    /* ========== CARDS ========== */
    .card {{
        background: {COLORS['card_bg']};
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }}
    
    .card h4 {{
        color: {COLORS['text_primary']} !important;
        margin-bottom: 0.5rem;
    }}
    
    .card p {{
        color: {COLORS['text_secondary']} !important;
        margin: 0;
    }}
    
    /* ========== METRIC CARDS ========== */
    .metric-card {{
        background: {COLORS['card_bg']};
        border-radius: 20px;
        padding: 1.25rem;
        text-align: center;
        border-top: 3px solid {COLORS['primary']};
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }}
    
    .metric-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {COLORS['text_secondary']};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 800;
        color: {COLORS['text_primary']};
        line-height: 1.2;
        margin-top: 0.5rem;
    }}
    
    /* ========== TÍTULOS ========== */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
    }}
    
    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0.75rem;
        border-left: 4px solid {COLORS['primary']};
        color: {COLORS['text_primary']} !important;
    }}
    
    /* ========== TABLA ========== */
    .stDataFrame {{
        background: {COLORS['card_bg']};
        border-radius: 16px;
        overflow: hidden;
    }}

    .stDataFrame td, .stDataFrame th {{
        color: {COLORS['text_primary']} !important;
        background-color: {COLORS['card_bg']} !important;
        border-color: {COLORS['border']} !important;
    }}

    .stDataFrame th {{
        background-color: {COLORS['border']} !important;
        color: {COLORS['text_primary']} !important;
        font-weight: 700;
    }}

    .stDataFrame tr:nth-child(even) td {{
        background-color: #F8FAFC !important;
    }}
    
    /* ========== ALERTAS ========== */
    .stAlert {{
        border-radius: 12px;
        border-left-width: 4px;
    }}
    
    /* ========== BOTONES PRINCIPALES ========== */
    .stButton button {{
        background-color: {COLORS['primary']};
        color: {COLORS['text_white']} !important;
        border-radius: 10px;
        font-weight: 500;
        border: none;
        transition: all 0.2s;
    }}
    
    .stButton button:hover {{
        background-color: {COLORS['secondary']};
        transform: translateY(-1px);
    }}
    
    /* ========== RADIO BUTTONS ========== */
    .stRadio label {{
        color: {COLORS['text_primary']} !important;
    }}
    
    /* ========== DIVIDER ========== */
    hr {{
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: #E5E7EB;
    }}
    
    /* ========== EXPANDER ========== */
    .streamlit-expanderHeader {{
        color: {COLORS['text_primary']} !important;
    }}
    
    /* ========== INFO/WARNING/ERROR ========== */
    .stInfo {{
        background-color: #EFF6FF;
        color: #1E40AF;
    }}
    
    .stWarning {{
        background-color: #FFFBEB;
        color: #92400E;
    }}
    
    .stError {{
        background-color: #FEF2F2;
        color: #991B1B;
    }}
    
    .stSuccess {{
        background-color: #ECFDF5;
        color: #065F46;
    }}
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def rerun_page():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'stop'):
        st.stop()
    else:
        raise RuntimeError('Streamlit rerun is not supported in this version.')


def _is_valid_status(status_value):
    if pd.isna(status_value) or status_value is None:
        return True
    status_str = str(status_value).upper()
    invalid_statuses = {'ARCHIVED', 'DELETED', 'UNSET', 'ARCHIVADO', 'ELIMINADO', 'INACTIVE'}
    if status_str in invalid_statuses:
        return False
    valid_statuses = {'ACTIVE', 'PAUSED', 'PENDING_REVIEW', 'WITH_ISSUES', 'IN_PROCESS'}
    if status_str in valid_statuses:
        return True
    return True


def _find_status_column(df: pd.DataFrame) -> str | None:
    if 'effective_status' in df.columns:
        return 'effective_status'
    if 'status' in df.columns:
        return 'status'
    if 'configured_status' in df.columns:
        return 'configured_status'
    for candidate in ['entrega', 'delivery']:
        if candidate in df.columns:
            return candidate
    return None


# ============================================================================
# CARGA DE DATOS
# ============================================================================
@st.cache_data(show_spinner=False)
def load_data(date_from: str, date_to: str, level: str, filter_campaign: str, refresh_count: int = 0) -> pd.DataFrame:
    validate_env()
    client = FacebookClient()
    raw = client.get_ads_insights(date_from, date_to, level=level)
    StorageManager.save_raw(raw, level, get_today_str())
    StorageManager.upsert_master(raw, get_today_str())
    df = pd.DataFrame(raw)
    if df.empty:
        return df
    df['report_date'] = get_today_str()

    try:
        df_status = pd.DataFrame(client.get_campaigns_status())
        if not df_status.empty and 'campaign_id' in df_status.columns:
            df['campaign_id'] = df['campaign_id'].astype(str)
            df_status['campaign_id'] = df_status['campaign_id'].astype(str)

            df = df.merge(
                df_status[['campaign_id', 'effective_status', 'configured_status', 'objective']],
                on='campaign_id',
                how='left',
                suffixes=('', '_from_status')
            )

            if 'effective_status_from_status' in df.columns:
                df['effective_status'] = df['effective_status_from_status'].fillna(df.get('effective_status', 'UNKNOWN'))
                df = df.drop(columns=['effective_status_from_status'])
            else:
                df['effective_status'] = df.get('effective_status', 'UNKNOWN')

            if 'configured_status_from_status' in df.columns:
                df['configured_status'] = df['configured_status_from_status'].fillna(df.get('configured_status', 'UNKNOWN'))
                df = df.drop(columns=['configured_status_from_status'])

            if 'effective_status' in df.columns and 'campaign_name' in df.columns and 'campaign_name' in df_status.columns:
                missing_status = df['effective_status'].isna() | (df['effective_status'] == '')
                if missing_status.any():
                    status_by_name = df_status.set_index('campaign_name')['effective_status'].to_dict()
                    df.loc[missing_status, 'effective_status'] = df.loc[missing_status, 'campaign_name'].map(
                        lambda x: status_by_name.get(x, 'UNKNOWN')
                    )

            logger.info('✅ Fusión exitosa: %s filas con estados', len(df))
        else:
            logger.warning('No se obtuvieron estados, usando UNKNOWN')
            df['effective_status'] = 'UNKNOWN'
            df['configured_status'] = 'UNKNOWN'
    except Exception as e:
        logger.error('Error en fusión de estados: %s', e)
        df['effective_status'] = 'UNKNOWN'
        df['configured_status'] = 'UNKNOWN'

    status_column = 'effective_status'
    if status_column in df.columns:
        before_status_filter = len(df)
        df = df[df[status_column] == 'ACTIVE']
        logger.info('Filtro ACTIVAS: %s -> %s campañas', before_status_filter, len(df))
        if df.empty:
            st.warning('⚠️ No hay campañas ACTIVAS en el período seleccionado.')
            return df
    else:
        st.error("❌ No se encontró columna 'effective_status' para filtrar campañas activas")
        return pd.DataFrame()

    # Solo agrupar si estamos en nivel CAMPAIGN
    if level == 'campaign' and 'campaign_id' in df.columns:
        sum_columns = [col for col in ['impressions', 'clicks', 'spend'] if col in df.columns]
        avg_columns = [col for col in ['ctr', 'cpc', 'cpm', 'frequency'] if col in df.columns]

        agg_dict = {col: 'sum' for col in sum_columns}
        agg_dict.update({col: 'mean' for col in avg_columns})
        agg_dict['campaign_name'] = 'first'
        agg_dict['effective_status'] = 'first'
        if 'configured_status' in df.columns:
            agg_dict['configured_status'] = 'first'
        if 'objective' in df.columns:
            agg_dict['objective'] = 'first'

        before_group = len(df)
        df = df.groupby('campaign_id', as_index=False).agg(agg_dict)
        logger.info('Agrupado por campaña: %s -> %s filas', before_group, len(df))
    else:
        logger.info('Nivel ADSET: manteniendo datos por conjunto de anuncios')

    df = calculate_kpis(df)
    df = add_recommendations(df)
    if filter_campaign:
        df = df[df['campaign_name'].str.contains(filter_campaign, case=False, na=False)]
    return df


# ============================================================================
# RENDERIZADO DE COMPONENTES
# ============================================================================
def render_header(df: pd.DataFrame):
    if df.empty or 'spend' not in df.columns:
        total_spend = 0.0
        total_conversions = 0
        avg_roas = 0.0
        avg_cpa = 0.0
    else:
        total_spend = df['spend'].sum()
        total_conversions = df['conversion_metric'].sum() if 'conversion_metric' in df.columns else 0
        avg_roas = df['roas'].mean() if 'roas' in df.columns else 0.0
        avg_cpa = df['cpa'].mean() if 'cpa' in df.columns and not df['cpa'].isna().all() else 0.0

    cols = st.columns(4, gap='large')
    
    metrics = [
        {'label': 'Inversión Total', 'value': format_currency(total_spend), 'icon': '💰'},
        {'label': 'Resultados Totales', 'value': f'{int(total_conversions):,}', 'icon': '🎯'},
        {'label': 'ROAS Promedio', 'value': f'{avg_roas:.2f}x', 'icon': '📈'},
        {'label': 'CPA Promedio', 'value': format_currency(avg_cpa) if avg_cpa > 0 else 'N/A', 'icon': '💎'}
    ]
    
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{metric['icon']} {metric['label']}</div>
                <div class="metric-value">{metric['value']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_charts(df: pd.DataFrame, level: str):
    if df.empty:
        st.info('No hay datos suficientes para mostrar gráficos.')
        return
    
    # Determinar el campo de agrupación según nivel
    if level == 'campaign':
        group_col = 'campaign_name'
        title_prefix = 'Campañas'
    else:
        group_col = 'adset_name' if 'adset_name' in df.columns else 'campaign_name'
        title_prefix = 'Conjuntos de Anuncios'
    
    # Gráfico 1: Evolución (si hay datos diarios)
    if 'date_start' in df.columns:
        daily = df.groupby('date_start').agg({
            'spend': 'sum',
            'roas': 'mean',
            'ctr': 'mean'
        }).reset_index().sort_values('date_start')
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=daily['date_start'], y=daily['spend'],
            name='Gasto (USD)', line=dict(color=COLORS['primary'], width=3),
            fill='tozeroy', fillcolor=f'rgba(79, 70, 229, 0.1)'
        ))
        fig_line.add_trace(go.Scatter(
            x=daily['date_start'], y=daily['roas'],
            name='ROAS', line=dict(color=COLORS['success'], width=3, dash='dot')
        ))
        fig_line.add_trace(go.Scatter(
            x=daily['date_start'], y=daily['ctr'],
            name='CTR (%)', line=dict(color=COLORS['warning'], width=3, dash='dash')
        ))
        fig_line.update_layout(
            title='📈 Evolución Diaria',
            template='plotly_white',
            hovermode='x unified',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            margin=dict(l=40, r=40, t=60, b=40),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # Gráfico 2: Top 5 por inversión
    col1, col2 = st.columns(2, gap='large')
    
    with col1:
        top5_spend = df.nlargest(5, 'spend')[[group_col, 'spend']]
        fig_bar = px.bar(
            top5_spend, x=group_col, y='spend',
            color='spend', color_continuous_scale='Blues',
            title=f'💰 Top 5 {title_prefix} por Inversión',
            text='spend'
        )
        fig_bar.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        fig_bar.update_layout(
            template='plotly_white',
            xaxis_title='',
            yaxis_title='Gasto (USD)',
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        df_eff = df[df['efficiency_score'] > 0].nlargest(5, 'efficiency_score')
        if not df_eff.empty:
            fig_eff = px.bar(
                df_eff, x=group_col, y='efficiency_score',
                color='efficiency_score', color_continuous_scale='Greens',
                title=f'⭐ Top 5 {title_prefix} por Eficiencia',
                text='efficiency_score'
            )
            fig_eff.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_eff.update_layout(
                template='plotly_white',
                xaxis_title='',
                yaxis_title='Score de Eficiencia',
                showlegend=False,
                margin=dict(l=40, r=40, t=60, b=40)
            )
            st.plotly_chart(fig_eff, use_container_width=True)


def render_table(df: pd.DataFrame, level: str):
    """Muestra tabla según el nivel (campaign o adset)"""
    if df.empty:
        st.info('No hay datos de campañas para mostrar.')
        return

    status_col = _find_status_column(df)
    
    # ========== SELECCIONAR COLUMNA DE NOMBRE SEGÚN NIVEL ==========
    if level == 'campaign':
        name_col = 'campaign_name'
        name_label = '📊 Campaña'
    else:
        # Para nivel adset, mostrar adset_name si existe
        if 'adset_name' in df.columns and df['adset_name'].notna().any():
            name_col = 'adset_name'
            name_label = '🎯 Conjunto de Anuncios'
        else:
            # Fallback a campaign_name si no hay adset
            name_col = 'campaign_name'
            name_label = '📊 Campaña (sin desglose)'
            st.info("ℹ️ No hay datos a nivel de conjunto de anuncios. Mostrando por campaña.")
    
    # ========== SELECCIONAR COLUMNAS A MOSTRAR ==========
    display_cols = [name_col, 'objective']
    
    if status_col and status_col not in display_cols:
        display_cols.append(status_col)
    
    # Métricas principales
    metric_cols = ['spend', 'impressions', 'clicks', 'ctr', 'cpc', 'roas', 'cpa', 'recommendation']
    for col in metric_cols:
        if col in df.columns:
            display_cols.append(col)
    
    # Para nivel adset, mostrar también la campaña padre (opcional)
    if level == 'adset' and 'campaign_name' in df.columns and 'campaign_name' not in display_cols:
        display_cols.insert(1, 'campaign_name')
    
    existing_cols = [col for col in display_cols if col in df.columns]
    table_df = df[existing_cols].copy()
    
    # ========== RENOMBRAR COLUMNAS ==========
    rename_map = {
        name_col: name_label,
        'campaign_name': 'Campaña Padre',
        'objective': 'Objetivo',
        'spend': '💰 Gasto',
        'impressions': '👁️ Impresiones',
        'clicks': '🖱️ Clics',
        'ctr': '📈 CTR',
        'cpc': '💵 CPC',
        'roas': '📊 ROAS',
        'cpa': '🎯 CPA',
        'recommendation': '💡 Recomendación'
    }
    if status_col:
        rename_map[status_col] = '📌 Estado'
    
    table_df = table_df.rename(columns=rename_map)
    
    # ========== FORMATEAR NÚMEROS ==========
    def style_roas(val):
        if isinstance(val, (int, float)):
            if val > 2:
                return 'color: #059669; font-weight: 600'
            elif val > 1:
                return 'color: #D97706; font-weight: 500'
            elif val > 0:
                return 'color: #DC2626; font-weight: 500'
        return ''
    
    def style_status(val):
        status_colors = {
            'ACTIVE': 'color: #059669; font-weight: 500',
            'PAUSED': 'color: #D97706; font-weight: 500',
            'PENDING_REVIEW': 'color: #0891B2; font-weight: 500',
            'WITH_ISSUES': 'color: #DC2626; font-weight: 500',
        }
        return status_colors.get(str(val).upper(), '')
    
    format_map = {
        '💰 Gasto': '${:,.2f}',
        '👁️ Impresiones': '{:,.0f}',
        '🖱️ Clics': '{:,.0f}',
        '📈 CTR': '{:.2f}%',
        '💵 CPC': '${:.2f}',
        '📊 ROAS': '{:.2f}x',
        '🎯 CPA': '${:.2f}'
    }
    
    # Aplicar formatos solo a columnas que existen
    final_format = {k: v for k, v in format_map.items() if k in table_df.columns}
    styled = table_df.style.format(cast(Any, final_format))
    
    if '📊 ROAS' in table_df.columns:
        styled = styled.map(style_roas, subset=['📊 ROAS'])
    if '📌 Estado' in table_df.columns:
        styled = styled.map(style_status, subset=['📌 Estado'])
    
    # ========== MOSTRAR TABLA CON INFORMACIÓN ADICIONAL ==========
    st.dataframe(styled, use_container_width=True, height=400)
    
    # Mostrar resumen estadístico según nivel
    col1, col2, col3 = st.columns(3)
    with col1:
        if level == 'campaign':
            st.metric('📊 Total Campañas', len(table_df))
        else:
            st.metric('🎯 Total Conjuntos', len(table_df))
    with col2:
        st.metric('💰 Gasto Total', f"${df['spend'].sum():,.2f}")
    with col3:
        if 'roas' in df.columns and df['roas'].mean() > 0:
            st.metric('📊 ROAS Promedio', f"{df['roas'].mean():.2f}x")
        else:
            st.metric('📊 ROAS Promedio', 'N/A')


def render_alerts(summary: dict, df: pd.DataFrame):
    st.markdown('<div class="section-title">⚠️ Alertas y Recomendaciones</div>', unsafe_allow_html=True)
    
    if summary['alerts']:
        for alert in summary['alerts']:
            if 'ROAS crítico' in alert or 'sin conversiones' in alert:
                st.error(alert)
            elif 'CPA alto' in alert:
                st.warning(alert)
            else:
                st.info(alert)
    else:
        st.success('✅ No hay alertas críticas. Todas las campañas están funcionando correctamente.')
    
    if not df.empty:
        st.markdown('---')
        col_export, _ = st.columns([1, 3])
        with col_export:
            export_cols = ['campaign_name', 'objective', 'spend', 'roas', 'recommendation']
            existing_export = [col for col in export_cols if col in df.columns]
            csv = df[existing_export].to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label='📥 Exportar Plan de Acción (CSV)',
                data=csv,
                file_name=f'ads_plan_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )


# ============================================================================
# MAIN
# ============================================================================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <h1>📊 Ads Intelligence</h1>
            <p>Analytics & Optimization</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Perfiles
        env_values = load_env_values()
        profiles = load_profiles()
        profile_names = [profile.get('PROFILE_NAME', 'default') for profile in profiles]

        if 'PROFILE_NAME' not in st.session_state:
            for key, value in env_values.items():
                if value is not None:
                    st.session_state[key] = str(value)

        selected_profile = st.selectbox('📁 Perfil', [''] + profile_names, key='selected_profile')
        if st.button('Cargar Perfil', use_container_width=True) and selected_profile:
            profile = next((p for p in profiles if p.get('PROFILE_NAME') == selected_profile), {})
            for key, value in profile.items():
                if value is not None:
                    st.session_state[key] = str(value)
            rerun_page()
        
        st.markdown('---')
        
        # Credenciales
        st.markdown('### 🔑 Credenciales')
        profile_name = st.text_input('Nombre del perfil', key='PROFILE_NAME')
        app_id = st.text_input('APP ID', key='APP_ID')
        access_token = st.text_input('Access Token', type='password', key='ACCESS_TOKEN')
        ad_account_id = st.text_input('Account ID (act_...)', key='AD_ACCOUNT_ID')
        average_value = st.text_input('Valor promedio producto', value=env_values.get('AVERAGE_PRODUCT_VALUE', '50.0'), key='AVERAGE_PRODUCT_VALUE')
        fb_api_version = st.text_input('API Version', value=env_values.get('FB_API_VERSION', 'v20.0'), key='FB_API_VERSION')
        
        col1, col2 = st.columns(2)
        with col1:
            save_credentials = st.button('💾 Guardar', use_container_width=True)
        with col2:
            delete_current = st.button('🗑️ Eliminar', use_container_width=True)
        
        if save_credentials:
            values = {
                'PROFILE_NAME': profile_name or 'default',
                'APP_ID': app_id,
                'ACCESS_TOKEN': access_token,
                'AD_ACCOUNT_ID': ad_account_id,
                'AVERAGE_PRODUCT_VALUE': average_value,
                'FB_API_VERSION': fb_api_version
            }
            save_env_values(values)
            save_profile(values)
            st.success('✅ Credenciales guardadas')
            rerun_page()
        
        if delete_current:
            delete_env_keys(['APP_ID', 'ACCESS_TOKEN', 'AD_ACCOUNT_ID', 'AVERAGE_PRODUCT_VALUE', 'FB_API_VERSION', 'PROFILE_NAME'])
            st.success('✅ Credenciales eliminadas')
            rerun_page()
        
        st.markdown('---')
        
        # Filtros
        st.markdown('### 🎯 Filtros')
        today = date.today()
        default_start = today - timedelta(days=29)
        date_range = st.date_input('Rango', [default_start, today])
        level = st.radio('Nivel', ['campaign', 'adset'], index=0, horizontal=True)
        campaign_filter = st.text_input('Filtrar campaña', placeholder='Nombre...')
        
        refresh = st.button('🔄 Actualizar Datos', use_container_width=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-top: 2rem;">
            <p style="font-size: 0.7rem; color: #94A3B8;">
                Última actualización<br>
                {datetime.now().strftime('%d/%m/%Y %H:%M')}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    if hasattr(date_range, '__len__') and len(date_range) >= 2:
        date_from = date_range[0].isoformat()
        date_to = date_range[1].isoformat()
    else:
        date_from = default_start.isoformat()
        date_to = today.isoformat()

    if 'refresh_count' not in st.session_state:
        st.session_state.refresh_count = 0
    if refresh:
        st.session_state.refresh_count += 1

    credentials_ready = all(os.getenv(key) for key in ['APP_ID', 'ACCESS_TOKEN', 'AD_ACCOUNT_ID'])

    if not credentials_ready:
        st.warning('⚠️ Complete y guarde las credenciales en la barra lateral')
        df = pd.DataFrame()
    else:
        with st.spinner('Cargando datos...'):
            try:
                df = load_data(date_from, date_to, level, campaign_filter, st.session_state.refresh_count)
            except Exception as exc:
                st.error(f'Error: {exc}')
                df = pd.DataFrame()

    # Resumen ejecutivo
    summary = generate_insights(df)
    st.markdown(f"""
    <div class="card">
        <h4>📋 Resumen Ejecutivo</h4>
        <p>{summary['message']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # KPIs
    render_header(df)
    
    st.markdown('<br>', unsafe_allow_html=True)

    # Indicador de nivel actual
    if level == 'campaign':
        st.info('📊 **Vista: Resumen por Campaña** - Mostrando datos agregados por campaña')
    else:
        st.info('🎯 **Vista: Detalle por Conjunto de Anuncios** - Mostrando rendimiento por cada audiencia/segmentación')
    
    st.markdown('<br>', unsafe_allow_html=True)
    
    # Gráficos
    if not df.empty:
        render_charts(df, level)
    
    st.markdown('<div class="section-title">📋 Detalle de Campañas</div>', unsafe_allow_html=True)
    render_table(df, level)
    
    # Alertas
    if not df.empty:
        st.markdown('<br>', unsafe_allow_html=True)
        render_alerts(summary, df)


if __name__ == '__main__':
    main()
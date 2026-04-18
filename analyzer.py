"""Análisis de KPIs y recomendaciones inteligentes por tipo de campaña."""

import os
import numpy as np
import pandas as pd
from typing import Optional


def calculate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula KPIs según el objetivo de cada campaña."""
    df = df.copy()

    # Asegurar columnas necesarias y valores por defecto
    for col, default in [
        ('impressions', 0),
        ('clicks', 0),
        ('spend', 0.0),
        ('reach', 0),
        ('purchases', 0),
        ('purchase_value', 0.0),
        ('leads', 0),
        ('video_views', 0),
    ]:
        if col not in df.columns:
            df.loc[:, col] = default
        df.loc[:, col] = df[col].fillna(default)

    # KPIs base
    df.loc[:, 'ctr'] = np.where(
        df['impressions'] > 0,
        (df['clicks'] / df['impressions']) * 100,
        0
    )
    df.loc[:, 'cpc'] = np.where(
        df['clicks'] > 0,
        df['spend'] / df['clicks'],
        np.nan
    )
    df.loc[:, 'cpm'] = np.where(
        df['impressions'] > 0,
        (df['spend'] / df['impressions']) * 1000,
        0
    )
    df.loc[:, 'frequency'] = np.where(
        df['reach'] > 0,
        df['impressions'] / df['reach'],
        1
    )

    # Inicializar columnas
    df.loc[:, 'conversion_metric'] = 0
    df.loc[:, 'conversion_value']  = 0.0
    df.loc[:, 'cpa']               = np.nan
    df.loc[:, 'roas']              = 0.0
    df.loc[:, 'efficiency_score']  = 0.0

    return df


def get_objective_label(objective_code: str) -> str:
    """Mapea código de objetivo a nombre legible"""
    if not objective_code:
        return "No especificado"
    
    code = str(objective_code).upper()
    objective_map = {
        'APP_INSTALLS': 'Instalaciones',
        'BRAND_AWARENESS': 'Reconocimiento',
        'CONVERSIONS': 'Conversiones',
        'EVENT_RESPONSES': 'Eventos',
        'LEAD_GENERATION': 'Leads',
        'LINK_CLICKS': 'Tráfico',
        'MESSAGES': 'Mensajes',
        'OFFER_CLAIMS': 'Ofertas',
        'OUTCOME_ENGAGEMENT': 'Engagement',
        'OUTCOME_TRAFFIC': 'Tráfico',
        'PAGE_LIKES': 'Likes',
        'POST_ENGAGEMENT': 'Engagement',
        'PRODUCT_CATALOG_SALES': 'Ventas',
        'REACH': 'Alcance',
        'STORE_VISITS': 'Visitas',
        'VIDEO_VIEWS': 'Video',
        'UNKNOWN': 'No especificado'
    }
    return objective_map.get(code, code.capitalize())


def analyze_campaign_performance(row: pd.Series) -> dict:
    """Analiza el rendimiento de una campaña y genera insights detallados"""
    
    campaign_name = row.get('campaign_name', '')
    objective = str(row.get('objective', '')).upper()
    ctr = row.get('ctr', 0)
    cpc = row.get('cpc', 0) if row.get('cpc') else 0
    spend = row.get('spend', 0)
    frequency = row.get('frequency', 0)
    impressions = row.get('impressions', 0)
    clicks = row.get('clicks', 0)
    
    # Benchmarks por objetivo
    benchmarks = {
        'TRÁFICO': {'ctr_good': 2, 'ctr_excellent': 5, 'cpc_good': 0.50, 'cpc_excellent': 0.30, 'avg_ctr': 1.5, 'avg_cpc': 0.55},
        'ENGAGEMENT': {'ctr_good': 1.5, 'ctr_excellent': 3, 'cpc_good': 0.60, 'cpc_excellent': 0.40, 'avg_ctr': 1.2, 'avg_cpc': 0.50},
        'LEADS': {'ctr_good': 2, 'ctr_excellent': 4, 'cpc_good': 0.80, 'cpc_excellent': 0.50, 'avg_ctr': 1.8, 'avg_cpc': 0.75},
        'CONVERSIONES': {'ctr_good': 1.5, 'ctr_excellent': 3, 'cpc_good': 0.70, 'cpc_excellent': 0.45, 'avg_ctr': 1.3, 'avg_cpc': 0.65},
        'RECONOCIMIENTO': {'ctr_good': 1, 'ctr_excellent': 2, 'cpc_good': 0.40, 'cpc_excellent': 0.25, 'avg_ctr': 0.8, 'avg_cpc': 0.35},
        'VIDEO': {'ctr_good': 1.5, 'ctr_excellent': 3, 'cpc_good': 0.50, 'cpc_excellent': 0.30, 'avg_ctr': 1.2, 'avg_cpc': 0.45},
        'DEFAULT': {'ctr_good': 1, 'ctr_excellent': 2, 'cpc_good': 0.60, 'cpc_excellent': 0.40, 'avg_ctr': 0.9, 'avg_cpc': 0.55}
    }
    
    bench = benchmarks.get(objective, benchmarks['DEFAULT'])
    
    # Evaluar CTR con comparativa
    if ctr >= bench['ctr_excellent']:
        ctr_rating = 'excelente'
        ctr_emoji = '🚀'
        multiplier = int(ctr / bench['avg_ctr']) if bench['avg_ctr'] > 0 else 2
        ctr_message = f'{multiplier}x mejor que el benchmark ({bench["avg_ctr"]:.1f}%)'
    elif ctr >= bench['ctr_good']:
        ctr_rating = 'bueno'
        ctr_emoji = '✅'
        ctr_message = f'CTR {ctr:.1f}% está por encima del promedio ({bench["avg_ctr"]:.1f}%)'
    elif ctr > 0:
        ctr_rating = 'bajo'
        ctr_emoji = '⚠️'
        ctr_message = f'CTR {ctr:.1f}% está por debajo del promedio ({bench["avg_ctr"]:.1f}%)'
    else:
        ctr_rating = 'sin_datos'
        ctr_emoji = '❌'
        ctr_message = 'Sin datos de CTR'
    
    # Evaluar CPC con comparativa
    if cpc > 0:
        if cpc <= bench['cpc_excellent']:
            cpc_rating = 'excelente'
            cpc_emoji = '💎'
            cpc_message = f'CPC ${cpc:.2f} es un {int((bench["avg_cpc"]/cpc)*100)}% más económico que el promedio (${bench["avg_cpc"]:.2f})'
        elif cpc <= bench['cpc_good']:
            cpc_rating = 'bueno'
            cpc_emoji = '✅'
            cpc_message = f'CPC ${cpc:.2f} está en rango normal (promedio ${bench["avg_cpc"]:.2f})'
        else:
            cpc_rating = 'alto'
            cpc_emoji = '💰'
            percent_above = int((cpc / bench['avg_cpc'] - 1) * 100)
            cpc_message = f'CPC ${cpc:.2f} es {percent_above}% más caro que el promedio (${bench["avg_cpc"]:.2f})'
    else:
        cpc_rating = 'sin_datos'
        cpc_emoji = '❌'
        cpc_message = 'Sin datos de CPC'
    
    # Evaluar frecuencia (saturación)
    if frequency > 5:
        frequency_rating = 'saturada'
        frequency_emoji = '🔄'
        frequency_message = f'Frecuencia {frequency:.1f} - Audiencia saturada, cambiar creatividad'
    elif frequency > 3:
        frequency_rating = 'media'
        frequency_emoji = '📊'
        frequency_message = f'Frecuencia {frequency:.1f} - Monitorear, cerca de saturación'
    else:
        frequency_rating = 'buena'
        frequency_emoji = '✅'
        frequency_message = f'Frecuencia {frequency:.1f} - Saludable'
    
    # Generar acción recomendada detallada
    if ctr_rating == 'excelente' and cpc_rating == 'excelente':
        action = '🚀 AUMENTAR PRESUPUESTO +20-30%'
        action_detail = 'Escalar gradualmente y duplicar para nuevas audiencias'
        priority = 'alta'
        expected_result = f'Al escalar a ${spend * 1.3:.0f} (+30%), podrías obtener ~{int(clicks * 1.25):,} clics'
    elif ctr_rating == 'excelente':
        action = '✅ MANTENER Y PROBAR VARIACIONES'
        action_detail = 'La creatividad funciona, prueba cambios en copy o llamados a acción'
        priority = 'media'
        percentile = min(99, int((ctr / bench['avg_ctr']) * 50)) if bench['avg_ctr'] > 0 else 90
        expected_result = f'CTR excelente - Mejor que el {percentile}% de los anuncios similares'
    elif ctr_rating == 'bueno' and cpc_rating == 'bueno':
        action = '📊 OPTIMIZAR CREATIVIDAD'
        action_detail = 'Prueba 2-3 variaciones de imagen/video para mejorar CTR'
        priority = 'media'
        expected_result = 'Potencial de mejorar CTR en 30-50%'
    elif ctr_rating == 'bajo' and spend > 50:
        action = '🔴 PAUSAR O REDISEÑAR'
        action_detail = 'Gasto alto con bajo rendimiento. Rediseña creatividad o segmentación'
        priority = 'alta'
        expected_result = 'Ahorro de ${spend:.0f} si pausas ahora'
    elif ctr_rating == 'bajo':
        action = '⚠️ REVISAR SEGMENTACIÓN'
        action_detail = 'Prueba nuevas audiencias o intereses similares'
        priority = 'media'
        expected_result = 'Potencial de mejorar CTR cambiando audiencia'
    else:
        action = '📈 MONITOREAR RENDIMIENTO'
        action_detail = 'Sin acciones urgentes, revisar en 7 días'
        priority = 'baja'
        expected_result = 'Monitoreo preventivo'
    
    return {
        'ctr_rating': ctr_rating,
        'ctr_emoji': ctr_emoji,
        'ctr_message': ctr_message,
        'cpc_rating': cpc_rating,
        'cpc_emoji': cpc_emoji,
        'cpc_message': cpc_message,
        'frequency_rating': frequency_rating,
        'frequency_emoji': frequency_emoji,
        'frequency_message': frequency_message,
        'action': action,
        'action_detail': action_detail,
        'priority': priority,
        'expected_result': expected_result,
        'benchmark_ctr': bench['avg_ctr'],
        'benchmark_cpc': bench['avg_cpc']
    }


def get_campaign_verdict(row: pd.Series, analysis: dict) -> str:
    """Genera un veredicto profesional para la campaña"""
    ctr_rating = analysis['ctr_rating']
    cpc_rating = analysis['cpc_rating']
    spend = row.get('spend', 0)

    if ctr_rating == 'excelente' and cpc_rating in ['excelente', 'bueno']:
        if spend > 100:
            return "🏆 **CABALLO DE BATALLA** - Escala agresivamente"
        else:
            return "⭐ **PROMESA** - Escala para validar"
    elif ctr_rating == 'excelente' and cpc_rating == 'alto':
        return "📊 **BUEN CTR, CPC ALTO** - Optimiza segmentación"
    elif ctr_rating == 'bueno' and cpc_rating == 'excelente':
        return "💎 **CPC ECONÓMICO** - Mejora creatividad para explotar"
    elif ctr_rating == 'bueno' and cpc_rating == 'bueno':
        return "✅ **SÓLIDA** - Mantén y optimiza gradualmente"
    elif ctr_rating == 'bajo' and spend > 50:
        return "🔴 **CRÍTICA** - Pausar o rediseñar urgentemente"
    elif ctr_rating == 'bajo':
        return "⚠️ **ATENCIÓN** - Requiere mejoras en creatividad"
    else:
        return "📈 **MONITOREAR** - Sin acciones urgentes"


def generate_star_campaign_analysis(df: pd.DataFrame) -> Optional[dict]:
    """Genera análisis detallado de la mejor campaña"""

    if df.empty:
        return None

    campaigns = []
    for _, row in df.iterrows():
        try:
            analysis = analyze_campaign_performance(row)
        except Exception:
            continue
        campaigns.append({
            'name': row.get('campaign_name', ''),
            'objective': row.get('objective', ''),
            'spend': row.get('spend', 0),
            'ctr': row.get('ctr', 0),
            'cpc': row.get('cpc', 0),
            'frequency': row.get('frequency', 0),
            'clicks': row.get('clicks', 0),
            'ctr_rating': analysis['ctr_rating'],
            'cpc_rating': analysis['cpc_rating'],
            'ctr_message': analysis['ctr_message'],
            'cpc_message': analysis['cpc_message'],
            'frequency_message': analysis['frequency_message'],
            'benchmark_ctr': analysis['benchmark_ctr'],
            'benchmark_cpc': analysis['benchmark_cpc']
        })

    campaigns.sort(key=lambda x: (
        0 if x['ctr_rating'] == 'excelente' else 1 if x['ctr_rating'] == 'bueno' else 2,
        x['cpc']
    ))

    if not campaigns:
        return None

    star = campaigns[0]

    current_spend = star['spend']
    projected_spend = current_spend * 1.3
    current_clicks = star['clicks']
    projected_clicks = int(current_clicks * 1.25)

    if star['ctr_rating'] == 'excelente' and star['cpc_rating'] in ['excelente', 'bueno']:
        action_level = "agresivo"
        recommendation = f"🚀 **AUMENTAR PRESUPUESTO +30%** esta semana"
        next_steps = [
            f"✅ Incrementar de ${current_spend:.0f} a ${projected_spend:.0f}",
            "✅ Duplicar campaña para nueva audiencia similar",
            "✅ Probar 2-3 variaciones del título/CTA"
        ]
        projection = f"📊 Al escalar a ${projected_spend:.0f}, proyectas ~{projected_clicks:,} clics (CTR estimado: {star['ctr']:.1f}%)"
    elif star['ctr_rating'] == 'excelente':
        action_level = "moderado"
        recommendation = f"✅ **MANTENER Y OPTIMIZAR** - La creatividad funciona"
        next_steps = [
            "✅ Probar variaciones del copy",
            "✅ Crear versión para remarketing",
            "✅ Monitorear frecuencia semanalmente"
        ]
        projection = f"📊 CTR en el top 5% - Potencial de escalar manteniendo eficiencia"
    else:
        action_level = "conservador"
        recommendation = f"📊 **OPTIMIZAR GRADUALMENTE**"
        next_steps = [
            "✅ Probar nuevas imágenes/videos",
            "✅ Ajustar segmentación de audiencia",
            "✅ Revisar oferta y llamado a acción"
        ]
        projection = f"📊 Potencial de mejorar CTR en 30-50% con optimizaciones"

    return {
        'name': star['name'],
        'objective': star['objective'],
        'spend': star['spend'],
        'ctr': star['ctr'],
        'cpc': star['cpc'],
        'frequency': star['frequency'],
        'clicks': star['clicks'],
        'ctr_message': star['ctr_message'],
        'cpc_message': star['cpc_message'],
        'frequency_message': star['frequency_message'],
        'benchmark_ctr': star['benchmark_ctr'],
        'benchmark_cpc': star['benchmark_cpc'],
        'action_level': action_level,
        'recommendation': recommendation,
        'next_steps': next_steps,
        'projection': projection,
        'verdict': get_campaign_verdict(pd.Series(star), star)
    }


def generate_detailed_insights(df: pd.DataFrame) -> dict:
    """Genera análisis detallado del dashboard"""
    
    if df.empty:
        return {'campaigns': [], 'star_campaign': None, 'summary': 'No hay datos para analizar', 'total_spend': 0, 'avg_ctr': 0, 'avg_cpc': 0}
    
    # Analizar cada campaña
    campaigns_analysis = []
    for _, row in df.iterrows():
        try:
            analysis = analyze_campaign_performance(row)
        except Exception:
            continue
        campaigns_analysis.append({
            'campaign_name': row.get('campaign_name', ''),
            'adset_name': row.get('adset_name', ''),
            'objective': row.get('objective', ''),
            'spend': row.get('spend', 0),
            'ctr': row.get('ctr', 0),
            'cpc': row.get('cpc', 0) if row.get('cpc') else 0,
            'frequency': row.get('frequency', 0),
            'clicks': row.get('clicks', 0),
            'impressions': row.get('impressions', 0),
            'reach': row.get('reach', 0),
            'cpm': row.get('cpm', 0),
            'roas': row.get('roas', 0),
            **analysis
        })
    
    # Ordenar por prioridad (alta primero)
    priority_order = {'alta': 0, 'media': 1, 'baja': 2}
    campaigns_analysis.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    # Identificar campaña estrella (mejor CTR con CPC bajo)
    star_campaign = None
    for camp in campaigns_analysis:
        if camp['ctr_rating'] == 'excelente' and camp['cpc_rating'] in ['excelente', 'bueno']:
            star_campaign = camp
            break
    
    # Si no hay estrella, tomar la de mayor prioridad
    if not star_campaign and campaigns_analysis:
        star_campaign = campaigns_analysis[0]
    
    # Generar resumen
    total_spend = df['spend'].sum()
    avg_ctr = df['ctr'].mean()
    avg_cpc = df['cpc'].mean() if 'cpc' in df.columns else 0
    
    summary = f"💰 Gasto total: ${total_spend:,.2f} | 📊 CTR promedio: {avg_ctr:.1f}% | 💵 CPC promedio: ${avg_cpc:.2f}"
    
    if star_campaign:
        summary += f" | ⭐ Campaña destacada: {star_campaign['campaign_name'][:30]}"
    
    # Contar campañas por prioridad
    high_priority = sum(1 for c in campaigns_analysis if c['priority'] == 'alta')
    
    return {
        'campaigns': campaigns_analysis,
        'star_campaign': star_campaign,
        'summary': summary,
        'total_spend': total_spend,
        'avg_ctr': avg_ctr,
        'avg_cpc': avg_cpc,
        'high_priority_count': high_priority
    }


def calculate_weekly_trends(df: pd.DataFrame, date_column: str = 'date_start') -> dict:
    """Calcula tendencias semanales de rendimiento"""
    
    if df.empty or date_column not in df.columns:
        return {'ctr_change': 0, 'cpc_change': 0, 'spend_change': 0}
    
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    df = df[df[date_column].notna()]
    
    if df.empty:
        return {'ctr_change': 0, 'cpc_change': 0, 'spend_change': 0}
    
    df['week'] = df[date_column].dt.isocalendar().week
    df['year'] = df[date_column].dt.year
    
    weekly = df.groupby(['year', 'week']).agg({
        'ctr': 'mean',
        'cpc': 'mean',
        'spend': 'sum'
    }).reset_index()
    
    if len(weekly) < 2:
        return {'ctr_change': 0, 'cpc_change': 0, 'spend_change': 0}
    
    last = weekly.iloc[-1]
    previous = weekly.iloc[-2]
    
    ctr_change = ((last['ctr'] - previous['ctr']) / previous['ctr'] * 100) if previous['ctr'] > 0 else 0
    cpc_change = ((last['cpc'] - previous['cpc']) / previous['cpc'] * 100) if previous['cpc'] > 0 else 0
    spend_change = ((last['spend'] - previous['spend']) / previous['spend'] * 100) if previous['spend'] > 0 else 0
    
    return {
        'ctr_change': ctr_change,
        'cpc_change': cpc_change,
        'spend_change': spend_change,
        'last_week': last,
        'previous_week': previous
    }


def estimate_roi_potential(row: pd.Series) -> Optional[dict]:
    """Estima ROI potencial basado en CPC y conversión estimada"""
    
    cpc = float(row.get('cpc', 0) or 0)
    spend = float(row.get('spend', 0) or 0)
    avg_order_value = float(os.getenv('AVERAGE_PRODUCT_VALUE', 50))
    
    conversion_rates = {
        'TRÁFICO': 0.02,
        'ENGAGEMENT': 0.01,
        'LEADS': 0.05,
        'CONVERSIONES': 0.03,
        'DEFAULT': 0.015
    }
    
    objective = str(row.get('objective', '')).upper()
    conv_rate = conversion_rates.get(objective, conversion_rates['DEFAULT'])
    
    if cpc > 0 and spend > 0:
        clicks = spend / cpc
        estimated_conversions = clicks * conv_rate
        estimated_revenue = estimated_conversions * avg_order_value
        estimated_roas = estimated_revenue / spend if spend > 0 else 0
        
        return {
            'estimated_conversions': int(estimated_conversions),
            'estimated_revenue': estimated_revenue,
            'estimated_roas': estimated_roas,
            'conversion_rate_used': conv_rate * 100,
            'is_projection': True
        }
    
    return None


def add_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Genera recomendaciones simples para la tabla (compatibilidad)"""
    df = df.copy()
    recommendations = []
    for _, row in df.iterrows():
        analysis = analyze_campaign_performance(row)
        recommendations.append(f"{analysis['ctr_emoji']} {analysis['ctr_message'][:50]} | {analysis['action']}")

    df['recommendation'] = recommendations
    return df


def generate_insights(df: pd.DataFrame) -> dict:
    """Genera resumen ejecutivo básico (compatibilidad)"""
    
    if df.empty:
        return {'message': 'No hay datos para el período seleccionado.', 'alerts': []}
    
    total_spend = df['spend'].sum()
    avg_ctr = df['ctr'].mean()
    
    # Campañas con problemas
    warnings = df[df['ctr'] < 1]
    alert_count = len(warnings)
    
    message = f"💰 Gasto total: ${total_spend:,.2f} | 📊 CTR promedio: {avg_ctr:.1f}% | ⚠️ {alert_count} campañas requieren atención"
    
    alerts = []
    for _, row in warnings.iterrows():
        alerts.append(f"⚠️ {row['campaign_name']}: CTR bajo ({row['ctr']:.1f}%)")
    
    return {'message': message, 'alerts': alerts[:5]}


def calculate_account_health_score(df: pd.DataFrame) -> dict:
    """Calcula un score 0-100 del health de la cuenta de ads."""
    if df.empty:
        return {'score': 0, 'grade': 'F', 'color': '#FC8181', 'breakdown': {
            'performance': 0, 'performance_max': 35,
            'cpc_efficiency': 0, 'cpc_max': 25,
            'audience': 0, 'audience_max': 20,
            'distribution': 0, 'distribution_max': 20
        }}

    has_roas = 'roas' in df.columns and df['roas'].fillna(0).sum() > 0

    # 1. Performance (0-35 pts)
    if has_roas:
        avg_roas = df['roas'].mean()
        perf_score = 35 if avg_roas >= 4 else 27 if avg_roas >= 2 else 15 if avg_roas >= 1 else 5
    else:
        avg_ctr = df['ctr'].mean() if 'ctr' in df.columns else 0
        perf_score = 32 if avg_ctr >= 3 else 22 if avg_ctr >= 1.5 else 10 if avg_ctr >= 0.8 else 2

    # 2. Eficiencia de CPC (0-25 pts)
    cpc_vals = df['cpc'].dropna() if 'cpc' in df.columns else pd.Series(dtype=float)
    cpc_vals = cpc_vals[cpc_vals > 0]
    if cpc_vals.empty:
        cpc_score = 12
    else:
        avg_cpc = cpc_vals.mean()
        cpc_score = 25 if avg_cpc <= 0.30 else 18 if avg_cpc <= 0.60 else 10 if avg_cpc <= 1.0 else 3

    # 3. Salud de audiencia / frecuencia (0-20 pts)
    if 'frequency' in df.columns:
        avg_freq = df['frequency'].mean()
        freq_score = 20 if avg_freq <= 2 else 14 if avg_freq <= 3 else 6 if avg_freq <= 5 else 0
    else:
        freq_score = 10

    # 4. Distribución del presupuesto (0-20 pts)
    total_spend = df['spend'].sum() if 'spend' in df.columns else 0
    if total_spend > 0 and len(df) > 1:
        spend_pcts = df['spend'] / total_spend
        cv = float(spend_pcts.std() / spend_pcts.mean()) if spend_pcts.mean() > 0 else 0
        conc_score = 20 if cv <= 0.4 else 13 if cv <= 0.8 else 5
    else:
        conc_score = 12

    total = perf_score + cpc_score + freq_score + conc_score

    if total >= 85:
        grade, color = 'A+', '#64DC96'
    elif total >= 75:
        grade, color = 'A', '#64DC96'
    elif total >= 65:
        grade, color = 'B+', '#86EFAC'
    elif total >= 55:
        grade, color = 'B', '#FBbf24'
    elif total >= 40:
        grade, color = 'C', '#FBbf24'
    elif total >= 25:
        grade, color = 'D', '#FC8181'
    else:
        grade, color = 'F', '#FC8181'

    return {
        'score': total,
        'grade': grade,
        'color': color,
        'breakdown': {
            'performance': perf_score, 'performance_max': 35,
            'cpc_efficiency': cpc_score, 'cpc_max': 25,
            'audience': freq_score, 'audience_max': 20,
            'distribution': conc_score, 'distribution_max': 20
        }
    }


def get_priority_actions(df: pd.DataFrame) -> list:
    """Genera lista de acciones priorizadas por impacto."""
    actions = []

    # --- ANÁLISIS GLOBAL: Consolidación de Campañas ---
    if 'campaign_name' in df.columns:
        num_campaigns = df['campaign_name'].nunique()
        if num_campaigns >= 4:
            actions.append({
                'priority': 2.5, 'urgency': 'OPORTUNIDAD',
                'color': '#1877F2', 'bg': '#e7f3ff',
                'border': '#bde4ff', 'icon': '🧩',
                'title': 'Estructura Fragmentada',
                'detail': f'Detectamos {num_campaigns} campañas activas. Demasiadas campañas dividen el presupuesto y limitan el aprendizaje de Meta.',
                'action': 'Consolida campañas con el mismo objetivo (1 o 2 máximo) usando Presupuesto Advantage+ (CBO).',
                'confidence': 'High',
                'impact': 'High',
                'time_context': 'Estrategia global'
            })

    for _, row in df.iterrows():
        name = str(row.get('adset_name') or row.get('campaign_name') or 'Sin nombre')[:40]
        spend   = float(row.get('spend', 0) or 0)
        ctr     = float(row.get('ctr', 0) or 0)
        freq    = float(row.get('frequency', 0) or 0)
        roas    = float(row.get('roas', 0) or 0)

        if freq > 6:
            confidence = 'High'
            impact = 'High' if spend > 50 else 'Medium' if spend > 20 else 'Low'
            time_context = 'Audience fatigue detected'
            actions.append({
                'priority': 1, 'urgency': 'CRÍTICO',
                'color': '#dd3c10', 'bg': '#fae0e0',
                'border': '#f5c0c0', 'icon': '🔴',
                'title': f'Creatividad agotada — {name}',
                'detail': f'Frecuencia {freq:.1f}x · La audiencia ha visto este anuncio demasiadas veces. CTR y conversión caen.',
                'action': 'Crear 3 variaciones nuevas de imagen/video esta semana. Rotar creatividades.',
                'confidence': confidence,
                'impact': impact,
                'time_context': time_context
            })
        elif roas > 0 and roas < 1 and spend > 30:
            confidence = 'High'
            impact = 'High' if spend > 50 else 'Medium' if spend > 20 else 'Low'
            time_context = 'Losing money daily'
            actions.append({
                'priority': 2, 'urgency': 'URGENTE',
                'color': '#dd3c10', 'bg': '#fae0e0',
                'border': '#f5c0c0', 'icon': '🔴',
                'title': f'Pérdida activa — {name}',
                'detail': f'ROAS {roas:.2f}x · ${spend:.0f} gastados sin retorno positivo.',
                'action': 'Pausar inmediatamente. Revisar segmentación y oferta antes de reactivar.',
                'confidence': confidence,
                'impact': impact,
                'time_context': time_context
            })
        elif freq > 4:
            confidence = 'Medium'
            impact = 'High' if spend > 50 else 'Medium' if spend > 20 else 'Low'
            time_context = 'Performance declining'
            actions.append({
                'priority': 3, 'urgency': 'ATENCIÓN',
                'color': '#92400E', 'bg': '#FFFBEB',
                'border': '#FDE68A', 'icon': '🟡',
                'title': f'Frecuencia elevada — {name}',
                'detail': f'Frecuencia {freq:.1f}x · Señales tempranas de saturación de audiencia.',
                'action': 'Renovar creatividad o ampliar audiencia lookalike antes de que el rendimiento caiga.',
                'confidence': confidence,
                'impact': impact,
                'time_context': time_context
            })
        elif ctr < 0.5 and spend > 20:
            confidence = 'Medium'
            impact = 'High' if spend > 50 else 'Medium' if spend > 20 else 'Low'
            time_context = 'Low engagement'
            actions.append({
                'priority': 4, 'urgency': 'ATENCIÓN',
                'color': '#92400E', 'bg': '#FFFBEB',
                'border': '#FDE68A', 'icon': '🟡',
                'title': f'CTR crítico — {name}',
                'detail': f'CTR {ctr:.2f}% · Creatividad sin tracción. ${spend:.0f} invertidos sin impacto.',
                'action': 'A/B test: nuevo visual + copy. Probar formato carrusel vs imagen única vs video.',
                'confidence': confidence,
                'impact': impact,
                'time_context': time_context
            })
        elif (roas >= 3 or (roas == 0 and ctr >= 2.5)) and spend > 5:
            confidence = 'High'
            impact = 'High' if spend > 50 else 'Medium' if spend > 20 else 'Low'
            time_context = 'High potential'
            actions.append({
                'priority': 5, 'urgency': 'OPORTUNIDAD',
                'color': '#065F46', 'bg': '#ECFDF5',
                'border': '#A7F3D0', 'icon': '🟢',
                'title': f'Escalar presupuesto — {name}',
                'detail': f'{"ROAS " + str(round(roas,1)) + "x" if roas > 0 else "CTR " + str(round(ctr,1)) + "%"} · Por encima del benchmark.',
                'action': 'Aumentar presupuesto +20-30%. Duplicar campaña para audiencias lookalike.',
                'confidence': confidence,
                'impact': impact,
                'time_context': time_context
            })

    actions.sort(key=lambda x: x['priority'])
    return actions[:8]
import streamlit as st
from database import init_db

init_db()

st.set_page_config(
    page_title="Ads Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    section.main > div { max-width: 1280px; margin: 0 auto; padding: 0 1.5rem; }
    .stApp { background: #080810; }
    .block-container { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)

# ========== NAVEGACIÓN ==========
if 'page' not in st.session_state:
    st.session_state.page = 'landing'

if st.session_state.page == 'login':
    from auth import login_page
    login_page()
    st.stop()

if st.session_state.page == 'demo':
    st.markdown("""
    <div style='padding: 4rem 0; color: #E8E6F0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>Demo de Ads Intelligence</h1>
        <p style='max-width: 680px; color: rgba(232,230,240,0.75); margin-bottom: 1.5rem;'>Aquí puedes mostrar un video de demo, capturas de pantalla o un dashboard de ejemplo para que los usuarios vean la experiencia antes de registrarse.</p>
        <div style='background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 2rem;'>
            <p style='color: rgba(232,230,240,0.8);'>Demo no disponible aún. Esta sección se puede extender con un video incrustado o un walkthrough interactivo.</p>
        </div>
        <button style='margin-top: 2rem; background: #8A6AE0; color: white; border: none; padding: 0.85rem 1.5rem; border-radius: 999px; cursor: pointer;' onclick="window.location.href='?';">Volver al landing</button>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if st.session_state.page == 'dashboard' and st.session_state.get('authenticated', False):
    if st.session_state.get('user_type') == 'admin':
        from admin_dashboard import admin_dashboard
        admin_dashboard()
    else:
        from client_dashboard import client_dashboard
        client_dashboard()
    st.stop()

# ========== CSS PREMIUM ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Satoshi:wght@300;400;500;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body, .stApp {
    background: #080810 !important;
    color: #E8E6F0;
    font-family: 'Satoshi', sans-serif;
}

/* ---- NOISE OVERLAY ---- */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

/* ---- GLOBALS ---- */
h1, h2, h3, h4 { font-family: 'Satoshi', sans-serif; font-weight: 700; }

/* ---- NAV ---- */
.nav-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Satoshi', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #F0EEF8;
}
.nav-logo .logo-mark {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #C9A84C, #8A6AE0);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.nav-links {
    display: flex;
    gap: 2.5rem;
}
.nav-links a {
    color: rgba(232,230,240,0.55);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 400;
    letter-spacing: 0.02em;
    transition: color 0.2s;
}
.nav-links a:hover { color: #E8E6F0; }

/* ---- HERO ---- */
.hero-section {
    position: relative;
    padding: 7rem 0 6rem;
    text-align: center;
    overflow: hidden;
}
.hero-glow {
    position: absolute;
    top: -120px; left: 50%;
    transform: translateX(-50%);
    width: 700px; height: 500px;
    background: radial-gradient(ellipse at center, rgba(138,106,224,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-glow-gold {
    position: absolute;
    top: 60px; left: 50%;
    transform: translateX(-50%);
    width: 400px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(201,168,76,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 1rem;
    background: rgba(201,168,76,0.12);
    border: 1px solid rgba(201,168,76,0.3);
    border-radius: 40px;
    font-size: 0.75rem;
    font-weight: 500;
    color: #C9A84C;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}
.hero-title {
    font-family: 'Satoshi', sans-serif;
    font-size: clamp(2.8rem, 5vw, 4.2rem);
    font-weight: 800;
    line-height: 1.08;
    letter-spacing: -0.03em;
    color: #F5F3FF;
    margin-bottom: 1.5rem;
}
.hero-title .gold { color: #C9A84C; }
.hero-title .dim { color: rgba(245,243,255,0.5); }
.hero-sub {
    font-size: 1.125rem;
    font-weight: 300;
    color: rgba(232,230,240,0.6);
    max-width: 520px;
    margin: 0 auto 2.5rem;
    line-height: 1.7;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 4rem;
    padding-top: 2.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.stat-item { text-align: center; }
.stat-number {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #F5F3FF;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(232,230,240,0.4);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ---- SECTION ---- */
.section-label {
    display: inline-block;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #8A6AE0;
    margin-bottom: 0.75rem;
}
.section-title {
    font-family: 'Satoshi', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    font-weight: 700;
    letter-spacing: -0.025em;
    color: #F5F3FF;
    line-height: 1.2;
    margin-bottom: 1rem;
}
.section-sub {
    font-size: 1rem;
    color: rgba(232,230,240,0.5);
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.6;
}
.section-header {
    text-align: center;
    margin-bottom: 3.5rem;
}
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 4rem 0;
}

/* ---- FEATURE CARDS ---- */
.feat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
}
.feat-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 2rem;
    transition: transform 0.3s, border-color 0.3s;
    position: relative;
    overflow: hidden;
}
.feat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,168,76,0.4), transparent);
    opacity: 0;
    transition: opacity 0.3s;
}
.feat-card:hover { transform: translateY(-4px); border-color: rgba(201,168,76,0.2); }
.feat-card:hover::before { opacity: 1; }
.feat-icon {
    width: 44px; height: 44px;
    background: rgba(138,106,224,0.12);
    border: 1px solid rgba(138,106,224,0.2);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 1.25rem;
}
.feat-card h3 {
    font-family: 'Satoshi', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #F5F3FF;
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}
.feat-card p {
    font-size: 0.875rem;
    color: rgba(232,230,240,0.5);
    line-height: 1.6;
}

/* ---- PRICING ---- */
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    align-items: start;
}
.price-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 2rem;
    position: relative;
    transition: transform 0.3s;
}
.price-card:hover { transform: translateY(-4px); }
.price-card.popular {
    background: rgba(138,106,224,0.07);
    border-color: rgba(138,106,224,0.35);
}
.popular-badge {
    position: absolute;
    top: -13px; left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, #8A6AE0, #6A4AC0);
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 30px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    white-space: nowrap;
}
.price-plan-name {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(232,230,240,0.45);
    margin-bottom: 0.75rem;
}
.price-amount {
    font-family: 'Satoshi', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    color: #F5F3FF;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.price-amount .currency { font-size: 1.4rem; vertical-align: top; margin-top: 0.5rem; display: inline-block; }
.price-amount .period {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.875rem;
    font-weight: 400;
    color: rgba(232,230,240,0.35);
    margin-left: 0.2rem;
}
.price-desc {
    font-size: 0.8rem;
    color: rgba(232,230,240,0.4);
    margin-bottom: 1.75rem;
    line-height: 1.5;
}
.feat-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.75rem;
}
.feat-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.45rem 0;
    font-size: 0.85rem;
    color: rgba(232,230,240,0.65);
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.feat-list li:last-child { border-bottom: none; }
.check {
    width: 16px; height: 16px;
    background: rgba(100,220,150,0.15);
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.6rem;
    color: #64DC96;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ---- TESTIMONIALS ---- */
.testi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
}
.testi-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 2rem;
}
.quote-mark {
    font-family: 'Satoshi', sans-serif;
    font-size: 3rem;
    color: rgba(201,168,76,0.3);
    line-height: 1;
    margin-bottom: 0.75rem;
}
.testi-text {
    font-size: 0.95rem;
    color: rgba(232,230,240,0.7);
    line-height: 1.7;
    margin-bottom: 1.25rem;
    font-weight: 300;
}
.testi-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.author-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Satoshi', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
}
.av-1 { background: rgba(138,106,224,0.2); color: #8A6AE0; }
.av-2 { background: rgba(201,168,76,0.2); color: #C9A84C; }
.author-name {
    font-family: 'Satoshi', sans-serif;
    font-size: 0.875rem;
    font-weight: 700;
    color: #F5F3FF;
}
.author-role {
    font-size: 0.75rem;
    color: rgba(232,230,240,0.35);
}

/* ---- CTA FINAL ---- */
.cta-section {
    background: rgba(138,106,224,0.06);
    border: 1px solid rgba(138,106,224,0.18);
    border-radius: 28px;
    padding: 4rem 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    margin: 2rem 0;
}
.cta-section::before {
    content: '';
    position: absolute;
    top: -80px; left: 50%;
    transform: translateX(-50%);
    width: 500px; height: 300px;
    background: radial-gradient(ellipse, rgba(138,106,224,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.cta-title {
    font-family: 'Satoshi', sans-serif;
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    font-weight: 800;
    letter-spacing: -0.025em;
    color: #F5F3FF;
    margin-bottom: 0.75rem;
}
.cta-sub {
    font-size: 1rem;
    color: rgba(232,230,240,0.5);
    margin-bottom: 2rem;
}
.trial-note {
    font-size: 0.78rem;
    color: rgba(232,230,240,0.3);
    margin-top: 0.75rem;
}

/* ---- FOOTER ---- */
.footer-wrap {
    padding: 2.5rem 0;
    border-top: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2rem;
}
.footer-copy { font-size: 0.8rem; color: rgba(232,230,240,0.25); }
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { font-size: 0.8rem; color: rgba(232,230,240,0.25); text-decoration: none; }

/* ---- BUTTON OVERRIDES ---- */
.stButton > button {
    background: linear-gradient(135deg, #8A6AE0 0%, #6A4AC0 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-family: 'Satoshi', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.7rem 2rem !important;
    transition: opacity 0.2s, transform 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.btn-secondary > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
}
</style>
""", unsafe_allow_html=True)

# Smooth scroll for anchor links
st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});
</script>
""", unsafe_allow_html=True)

# ========== NAV ==========
col_logo, col_links, col_cta = st.columns([2, 4, 2])

with col_logo:
    st.markdown("""
    <div class="nav-logo" style="padding: 1.5rem 0;">
        <div class="logo-mark">◈</div>
        Ads Intelligence
    </div>
    """, unsafe_allow_html=True)

with col_links:
    st.markdown("""
    <div class="nav-links" style="justify-content: center; padding: 1.5rem 0;">
        <a href="#inicio">Inicio</a>
        <a href="#caracteristicas">Características</a>
        <a href="#precios">Precios</a>
        <a href="#testimonios">Testimonios</a>
    </div>
    """, unsafe_allow_html=True)

with col_cta:
    st.markdown('<div style="padding-top: 1.1rem;">', unsafe_allow_html=True)
    if st.button("Acceso Clientes →", key="nav_cta"):
        st.session_state.page = 'login'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ========== HERO ==========
st.markdown('<div id="inicio"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-section">
    <div class="hero-glow"></div>
    <div class="hero-glow-gold"></div>
    <div class="hero-badge">✦ Powered by Inteligencia Artificial</div>
    <h1 class="hero-title">
        Campañas más rentables.<br>
        <span class="gold">Decisiones más rápidas.</span><br>
        <span class="dim">Sin esfuerzo manual.</span>
    </h1>
    <p class="hero-sub">
        La plataforma de análisis publicitario que convierte tus datos de Facebook Ads en acciones concretas.
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns([1, 1.5, 0.3, 1.5, 1])
with c2:
    if st.button("🚀 Comenzar Gratis", key="hero_cta1", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()
with c4:
    st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
    if st.button("Ver demo →", key="hero_cta2", use_container_width=True):
        st.session_state.page = 'demo'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex; justify-content:center; gap:3rem; padding: 3rem 0 1rem; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 2rem;">
    <div class="stat-item">
        <div class="stat-number">+340%</div>
        <div class="stat-label">ROI promedio</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">12 hrs</div>
        <div class="stat-label">Ahorradas por semana</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">2,400+</div>
        <div class="stat-label">Campañas optimizadas</div>
    </div>
    <div class="stat-item">
        <div class="stat-number">99.9%</div>
        <div class="stat-label">Uptime garantizado</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== CARACTERÍSTICAS ==========
st.markdown('<div id="caracteristicas"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-label">Plataforma</span>
    <h2 class="section-title">Todo lo que necesitas para<br>escalar tus campañas</h2>
    <p class="section-sub">Desde el análisis hasta la ejecución, en un solo lugar.</p>
</div>
<div class="feat-grid">
    <div class="feat-card">
        <div class="feat-icon">📈</div>
        <h3>Análisis Automático</h3>
        <p>Conecta tu cuenta y obtén métricas clave procesadas en tiempo real, sin esfuerzo manual.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🧠</div>
        <h3>Recomendaciones con IA</h3>
        <p>Sabe exactamente qué acción tomar: escalar, optimizar o pausar cada campaña.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">⚡</div>
        <h3>Ahorro de Tiempo</h3>
        <p>Reportes automáticos. Dashboard unificado. Olvídate de hojas de cálculo.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🔔</div>
        <h3>Alertas Inteligentes</h3>
        <p>Recibe notificaciones cuando una campaña supera umbrales de gasto o bajo rendimiento.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📊</div>
        <h3>Benchmarking</h3>
        <p>Compara el rendimiento de tus campañas contra promedios del sector en tu industria.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📤</div>
        <h3>Exportación Avanzada</h3>
        <p>Genera reportes en PDF o CSV personalizados para tus clientes con un clic.</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== PRECIOS ==========
st.markdown('<div id="precios"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-label">Precios</span>
    <h2 class="section-title">Planes diseñados<br>para cada etapa</h2>
    <p class="section-sub">Sin contratos largos. Cancela cuando quieras.</p>
</div>
<div class="pricing-grid">
    <div class="price-card">
        <div class="price-plan-name">Basic</div>
        <div class="price-amount"><span class="currency">$</span>29<span class="period">/mes</span></div>
        <p class="price-desc">Ideal para freelancers y proyectos pequeños.</p>
        <ul class="feat-list">
            <li><span class="check">✓</span> Hasta 3 campañas activas</li>
            <li><span class="check">✓</span> 30 días de historial</li>
            <li><span class="check">✓</span> Dashboard básico</li>
            <li><span class="check">✓</span> Alertas por email</li>
        </ul>
    </div>
    <div class="price-card popular">
        <div class="popular-badge">⭐ Más popular</div>
        <div class="price-plan-name">Pro</div>
        <div class="price-amount"><span class="currency">$</span>79<span class="period">/mes</span></div>
        <p class="price-desc">Para agencias y equipos en crecimiento.</p>
        <ul class="feat-list">
            <li><span class="check">✓</span> Hasta 20 campañas activas</li>
            <li><span class="check">✓</span> 90 días de historial</li>
            <li><span class="check">✓</span> Exportación CSV + PDF</li>
            <li><span class="check">✓</span> Alertas avanzadas</li>
            <li><span class="check">✓</span> Recomendaciones IA prioritarias</li>
        </ul>
    </div>
    <div class="price-card">
        <div class="price-plan-name">Enterprise</div>
        <div class="price-amount"><span class="currency">$</span>199<span class="period">/mes</span></div>
        <p class="price-desc">Solución completa para grandes operaciones.</p>
        <ul class="feat-list">
            <li><span class="check">✓</span> Campañas ilimitadas</li>
            <li><span class="check">✓</span> 365 días de historial</li>
            <li><span class="check">✓</span> Soporte prioritario 24/7</li>
            <li><span class="check">✓</span> White label</li>
            <li><span class="check">✓</span> API access</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== TESTIMONIOS ==========
st.markdown('<div id="testimonios"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section-header">
    <span class="section-label">Testimonios</span>
    <h2 class="section-title">Lo que dicen quienes<br>ya lo usan</h2>
</div>
<div class="testi-grid">
    <div class="testi-card">
        <div class="quote-mark">"</div>
        <p class="testi-text">Reduje el 80% del tiempo que dedicaba a reportes. Las recomendaciones de la IA son increíblemente precisas y accionables.</p>
        <div class="testi-author">
            <div class="author-avatar av-1">MG</div>
            <div>
                <div class="author-name">María González</div>
                <div class="author-role">Media Buyer · Agencia Crecer</div>
            </div>
        </div>
    </div>
    <div class="testi-card">
        <div class="quote-mark">"</div>
        <p class="testi-text">Descubrí una campaña que estaba perdiendo $2,000 al mes. La pausé gracias a una alerta automática. En dos semanas recuperé la inversión.</p>
        <div class="testi-author">
            <div class="author-avatar av-2">CR</div>
            <div>
                <div class="author-name">Carlos Ruiz</div>
                <div class="author-role">Director de Marketing · Ecom Pro</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ========== CTA FINAL ==========
st.markdown("""
<div class="cta-section">
    <span class="section-label">Empieza hoy</span>
    <h2 class="cta-title">¿Listo para multiplicar<br>tu retorno publicitario?</h2>
    <p class="cta-sub">14 días gratis. Sin tarjeta de crédito. Cancela cuando quieras.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("🚀 Probar Gratis 14 Días", key="cta_final", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()

# ========== FOOTER ==========
st.markdown("""
<div class="footer-wrap">
    <div class="nav-logo" style="font-size:0.9rem;">
        <div class="logo-mark" style="width:24px;height:24px;font-size:0.75rem;">◈</div>
        Ads Intelligence
    </div>
    <div class="footer-copy">© 2024 Ads Intelligence. Todos los derechos reservados.</div>
    <div class="footer-links">
        <a href="#">Privacidad</a>
        <a href="#">Términos</a>
        <a href="#">Contacto</a>
    </div>
</div>
""", unsafe_allow_html=True)
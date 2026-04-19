import streamlit as st
import traceback
import os
from database import init_db
from auth import register_page # Importar la nueva página de registro


try:
    init_db()
except Exception as exc:
    st.error(f"Error inicializando la base de datos: {exc}")
    st.stop()

st.set_page_config(
    page_title="Ads Intelligence",
    page_icon="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Oculta el header por defecto de Streamlit y el botón de la sidebar */
    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    .stApp > header { display: none; }

    /* Centra el contenido principal */
    section.main > div { max-width: 1280px; margin: 0 auto; padding: 0 1.5rem; }
    .stApp { background: #FFFFFF; }
    .block-container { 
        padding-top: 0 !important; 
        max-width: 1280px !important; 
        margin: 0 auto !important; 
    }

/* Fix white texts */
label p, [data-testid="stWidgetLabel"] p, [data-testid="stCaptionContainer"] {
    color: #0F172A !important;
}

/* Fix all input text colors */
div[data-testid="stTextInput"] input, 
div[data-baseweb="input"] input, 
.stTextInput input,
input[type="text"],
input[type="password"],
input[type="number"],
input[type="email"] {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    background-color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# ========== NAVEGACIÓN ==========
# Revisa si la navegación se está pidiendo por query params (para botones en HTML)
query_params = st.query_params
if "page" in query_params:
    # The new st.query_params API gets the first value of a parameter directly.
    page_to_go = query_params["page"]
    if page_to_go in ['login', 'register', 'demo', 'landing', 'strategy']:
        st.session_state.page = page_to_go
        st.query_params.clear() # Use the corresponding setter to clear params

if 'page' not in st.session_state:
    st.session_state.page = 'landing'

if st.session_state.page == 'login':
    from auth import login_page
    login_page()
    st.stop()

if st.session_state.page == 'register': # Nueva página de registro
    register_page()
    st.stop()


if st.session_state.page == 'demo':
    st.markdown("""
    <div style='padding: 4rem 0; color: #E8E6F0;'>
        <h1 style='font-size: 2.5rem; margin-bottom: 1rem;'>Demo de Ads Intelligence</h1>
        <p style='max-width: 680px; color: #334155; margin-bottom: 1.5rem;'>Aquí puedes mostrar un video de demo, capturas de pantalla o un dashboard de ejemplo para que los usuarios vean la experiencia antes de registrarse.</p>
        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; padding: 2rem;'>
            <p style='color: #1E293B;'>Demo no disponible aún. Esta sección se puede extender con un video incrustado o un walkthrough interactivo.</p>
        </div>
        <button style='margin-top: 2rem; background: #4F46E5; color: white; border: none; padding: 0.85rem 1.5rem; border-radius: 999px; cursor: pointer;' onclick="window.location.href='?';">Volver al landing</button>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

if st.session_state.page == 'strategy':
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
        .stApp > header { display: none; }
        .stApp { background: #FFFFFF; color: #E8E6F0; font-family: 'Satoshi', sans-serif; }
        .block-container { max-width: 900px !important; padding-top: 3rem !important; padding-bottom: 4rem !important; }
        .strategy-box { background: #F8FAFC; border: 1px solid #F8FAFC; border-radius: 20px; padding: 3rem; margin-top: 1rem; }
        .strategy-box h1 { color: #0F172A; font-size: 2.2rem; margin-bottom: 1rem; line-height: 1.2; }
        .strategy-box h2 { color: #6366F1; margin-top: 2.5rem; font-size: 1.6rem; border-bottom: 1px solid #F8FAFC; padding-bottom: 0.5rem; }
        .strategy-box h3 { color: #0F172A; margin-top: 1.5rem; font-size: 1.2rem; }
        .strategy-box p, .strategy-box li { color: #334155; line-height: 1.6; margin-bottom: 0.8rem; font-size: 0.95rem; }
        .strategy-box hr { border-color: #E2E8F0; margin: 2rem 0; }
        .back-btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: #F8FAFC; border-radius: 8px; color: #0F172A; text-decoration: none; font-size: 0.9rem; transition: background 0.2s; }
        .back-btn:hover { background: #E2E8F0; }
    </style>
    <a href='?' class='back-btn'>← Volver al Inicio</a>
    <div class='strategy-box'>
    """, unsafe_allow_html=True)
    try:
        with open("ESTRATEGIA_META_ADS.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())
    except Exception:
        st.warning("El archivo de guía estratégica no se encontró. Verifica que ESTRATEGIA_META_ADS.md exista.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if st.session_state.page == 'dashboard' and st.session_state.get('authenticated', False):
    if st.session_state.get('user_type') == 'admin':
        from admin_dashboard import admin_dashboard
        admin_dashboard()
    else:
        try:
            from client_dashboard import client_dashboard
            client_dashboard()
        except Exception as e:
            st.error(f"Error al cargar el dashboard: {e}")
            st.text(traceback.format_exc())
            st.stop()
    st.stop()

# ========== CSS PREMIUM ==========
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body, .stApp {
    background: #FFFFFF !important;
    color: #0F172A;
    font-family: 'Roboto', sans-serif;
}

/* ---- BOTÓN DE ACCIÓN PERSONALIZADO EN NAV ---- */
.nav-action-button {
    background: #0F172A;
    color: white !important;
    border: none;
    border-radius: 6px;
    font-family: 'Roboto', sans-serif;
    font-weight: 700;
    font-size: 0.9rem; /* Ajustado para el header */
    padding: 0.6rem 1.2rem;
    transition: background-color 0.2s;
    text-decoration: none;
    display: inline-block;
}
.nav-action-button:hover {
    background: #1E293B;
}

/* ---- GLOBALS ---- */
html { scroll-behavior: smooth; }
h1, h2, h3, h4 { font-family: 'Segoe UI', 'Roboto', sans-serif; font-weight: 700; }

/* Forzar centrado de textos que Streamlit suele sobreescribir a la izquierda */
.hero-title, .hero-sub, .stat-item,
.section-header, .section-title, .section-sub, 
.feat-card h3, .feat-card p, 
.price-plan-name, .price-amount, .price-desc, 
.testi-text, .cta-title, .cta-sub, .quote-mark {
    text-align: center !important;
    margin-left: auto !important;
    margin-right: auto !important;
}
.feat-icon { margin: 0 auto 1.25rem !important; }
.testi-author { justify-content: center !important; }

/* ---- NAV ---- */
.nav-links {
    display: flex;
    gap: 2.5rem;
}
.nav-links a {
    color: #475569;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
    transition: color 0.2s;
}
.nav-links a:hover { color: #0F172A; }

/* ---- HEADER ---- */
.main-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #E2E8F0;
    position: sticky;
    top: 0;
    background: #FFFFFF;
    z-index: 100;
    width: 100%;
    left: 0;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.2rem;
    font-weight: 700;
    color: #0F172A;
    text-decoration: none;
}
.nav-logo .logo-mark {
    width: 30px;
    height: 30px;
    border-radius: 6px;
    object-fit: contain;
}
.nav-actions { display: flex; align-items: center; gap: 0.75rem; }
.nav-toggle { display: none; }

/* ---- MOBILE NAV ---- */
.mobile-nav-panel {
    position: fixed;
    top: 0; right: 0; bottom: 0; left: 0;
    background: #FFFFFF;
    z-index: 99;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    transform: translateX(100%);
    transition: transform 0.3s ease;
}
.mobile-nav-panel a {
    color: #0F172A;
    text-decoration: none;
    font-size: 1.5rem;
    font-weight: 500;
}
#nav-toggle-cb:checked ~ .mobile-nav-panel { transform: translateX(0); }
#nav-toggle-cb:checked ~ .main-header .nav-toggle span:nth-child(1) { transform: rotate(45deg) translate(5px, 5px); }
#nav-toggle-cb:checked ~ .main-header .nav-toggle span:nth-child(2) { opacity: 0; }
#nav-toggle-cb:checked ~ .main-header .nav-toggle span:nth-child(3) { transform: rotate(-45deg) translate(5px, -5px); }

/* ---- HERO ---- */
.hero-section {
    position: relative;
    padding: 5rem 0 5rem;
    text-align: center;
    background-color: #F1F5F9;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.4rem 1rem;
    background: #F8FAFC;
    border: 1px solid #0F172A;
    border-radius: 40px;
    font-size: 0.8rem;
    font-weight: 500;
    color: #0F172A;
    margin-bottom: 2rem;
}
.hero-title {
    font-size: clamp(2.5rem, 5vw, 3.8rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    color: #0F172A;
    margin-bottom: 1.5rem;
}
.hero-title .gold { color: #0F172A; }
.hero-title .dim { color: #475569; }
.hero-sub {
    font-size: 1.1rem;
    font-weight: 400;
    color: #475569;
    max-width: 520px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 3rem;
    padding-top: 2.5rem;
    border-top: 1px solid #E2E8F0;
}
.stat-item { text-align: center; }
.stat-number {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0F172A;
}
.stat-label {
    font-size: 0.75rem;
    color: #475569;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ---- SECTION ---- */
.section-label {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #0F172A;
    margin-bottom: 0.75rem;
}
.section-title {
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
    margin-bottom: 1rem;
}
.section-sub {
    font-size: 1rem;
    color: #475569;
    max-width: 500px;
    margin: 0 auto;
    line-height: 1.6;
    text-align: center;
}
.section-header {
    text-align: center;
    margin-bottom: 3.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.divider {
    border: none;
    border-top: 1px solid #F1F5F9;
    margin: 4rem 0;
}

/* ---- FEATURE CARDS ---- */
.feat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
}
.feat-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 2rem;
    transition: box-shadow 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.feat-card:hover { box-shadow: 0 4px 12px #E2E8F0; }
.feat-icon {
    width: 44px; height: 44px;
    background: #F8FAFC;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    color: #0F172A;
    margin-bottom: 1.25rem;
}
.feat-card h3 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.5rem;
}
.feat-card p {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.6;
}

/* ---- PRICING ---- */
.pricing-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    align-items: stretch;
}
.price-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.price-card.popular {
    border-width: 2px;
    border-color: #0F172A;
}
.popular-badge {
    position: absolute;
    top: -13px; left: 50%;
    transform: translateX(-50%);
    background: #0F172A;
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 30px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
}
.price-plan-name {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.75rem;
}
.price-amount {
    font-size: 3rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.price-amount .currency { font-size: 1.4rem; vertical-align: top; margin-top: 0.5rem; display: inline-block; }
.price-amount .period {
    font-size: 0.875rem;
    font-weight: 400;
    color: #475569;
    margin-left: 0.2rem;
}
.price-desc {
    font-size: 0.85rem;
    color: #475569;
    margin-bottom: 1.75rem;
    line-height: 1.5;
}
.feat-list {
    list-style: none;
    padding: 0;
    margin: 0 0 1.75rem;
    flex-grow: 1;
    width: 100%;
}
.feat-list li {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.5rem 0;
    font-size: 0.9rem;
    color: #0F172A;
}
.check {
    width: 18px; height: 18px;
    background: #F8FAFC;
    border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.7rem;
    color: #0F172A;
    flex-shrink: 0;
    margin-top: 2px;
}

/* ---- TESTIMONIALS ---- */
.testi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
}
.testi-card {
    background: #F1F5F9;
    border-radius: 8px;
    padding: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.quote-mark {
    font-size: 3rem;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 0.75rem;
}
.testi-text {
    font-size: 1rem;
    color: #0F172A;
    line-height: 1.6;
    margin-bottom: 1.25rem;
    font-weight: 400;
}
.testi-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.author-avatar {
    width: 40px; height: 40px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
}
.av-1 { background: #F8FAFC; color: #0F172A; }
.av-2 { background: #F8FAFC; color: #0F172A; }
.author-name {
    font-size: 0.9rem;
    font-weight: 700;
    color: #0F172A;
}
.author-role {
    font-size: 0.75rem;
    color: #475569;
}

/* ---- CTA FINAL ---- */
.cta-section {
    background: #F1F5F9;
    border-radius: 16px;
    padding: 4rem 2rem;
    text-align: center;
    margin: 2rem 0;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.cta-title {
    font-size: clamp(1.8rem, 3vw, 2.4rem);
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0.75rem;
}
.cta-sub {
    font-size: 1rem;
    color: #475569;
    margin-bottom: 2rem;
    max-width: 500px;
    margin-left: auto;
    margin-right: auto;
}
.trial-note {
    font-size: 0.8rem;
    color: #475569;
    margin-top: 0.75rem;
}

/* ---- FOOTER ---- */
.footer-wrap {
    padding: 2.5rem 0;
    border-top: 1px solid #E2E8F0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2rem;
}
.footer-copy { font-size: 0.8rem; color: #475569; }
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { font-size: 0.8rem; color: #475569; text-decoration: none; }

/* ---- BUTTON OVERRIDES ---- */
.stButton > button {
    background: #0F172A !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Roboto', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.75rem 2rem !important;
    transition: background-color 0.2s !important;
}
.stButton > button:hover {
    background: #1E293B !important;

    color: white !important;
    border-color: transparent !important;}
.btn-secondary > button {
    background: #E4E6EB !important;
    color: #0F172A !important;
    border: none !important;
}
.btn-secondary > button:hover {
    background: #d8dbdf !important;
}

/* ---- RESPONSIVE DESIGN ---- */
@media (max-width: 1024px) {
    .feat-grid, .pricing-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .hero-stats {
        gap: 2rem;
        flex-wrap: wrap;
    }
}

@media (max-width: 768px) {
    .feat-grid, .pricing-grid, .testi-grid {
        grid-template-columns: 1fr;
    }
    /* Hamburger Menu */
    .main-nav, .nav-actions { display: none; }
    .nav-toggle {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        width: 24px;
        height: 24px;
        background: transparent;
        border: none;
        cursor: pointer;
        padding: 0;
        z-index: 101;
    }
    .nav-toggle span {
        width: 24px;
        height: 2px;
        background: #0F172A;
        border-radius: 10px;
        transition: all 0.3s ease;
        transform-origin: 1px;
    }
    .hero-section {
        padding: 4rem 0 3rem;
    }
    .hero-stats {
        flex-direction: column;
        gap: 1.5rem;
    }
    .cta-section {
        padding: 3rem 1.5rem;
    }
    .footer-wrap {
        flex-direction: column;
        gap: 1.25rem;
        text-align: center;
    }
    .footer-links {
        justify-content: center;
    }
}
</style>
""", unsafe_allow_html=True)

# ========== NAV ==========
st.markdown("""
<input type="checkbox" id="nav-toggle-cb" style="display: none;">
<header class="main-header">
    <a href="#inicio" class="nav-logo">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="logo-mark" alt="Logo">
        Ads Intelligence
    </a>
    <nav class="main-nav">
        <div class="nav-links">
            <a href="#inicio">Inicio</a>
            <a href="#caracteristicas">Características</a>
            <a href="#precios">Precios</a>
            <a href="#testimonios">Testimonios</a>
            <a href="/?page=strategy">Guía de Estrategia</a>
        </div>
    </nav>
    <div class="nav-actions">
        <a href="/?page=login" class="nav-action-button">Acceso Clientes</a>
    </div>
    <label for="nav-toggle-cb" class="nav-toggle" aria-label="Abrir menú">
        <span></span>
        <span></span>
        <span></span>
    </label>
</header>

<!-- Panel para navegación móvil -->
<div class="mobile-nav-panel">
    <a href="#inicio" onclick="document.getElementById('nav-toggle-cb').checked = false;">Inicio</a>
    <a href="#caracteristicas" onclick="document.getElementById('nav-toggle-cb').checked = false;">Características</a>
    <a href="#precios" onclick="document.getElementById('nav-toggle-cb').checked = false;">Precios</a>
    <a href="#testimonios" onclick="document.getElementById('nav-toggle-cb').checked = false;">Testimonios</a>
    <a href="/?page=strategy">Guía de Estrategia</a>
    <a href="/?page=login" class="nav-action-button" style="margin-top: 2rem;">Acceso Clientes</a>
    <script>
        document.querySelectorAll('.mobile-nav-panel a').forEach(link => {
            link.addEventListener('click', () => {
                document.getElementById('nav-toggle-cb').checked = false;
            });
        });
    </script>
</div>
""", unsafe_allow_html=True)

# ========== HERO ==========
st.markdown('<div id="inicio"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-section">
    <div class="hero-badge">✦ Powered by Inteligencia Artificial</div>
    <h1 class="hero-title">
        Campañas más rentables.<br>
        <span class="gold">Decisiones más rápidas.</span><br>
        <span class="dim">Sin análisis manual.</span>
    </h1>
    <p class="hero-sub">
        La plataforma de análisis publicitario que convierte tus datos de Facebook Ads en acciones concretas.
    </p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    if st.button("🚀 Comenzar Gratis", key="hero_cta1", use_container_width=True):
        st.session_state.page = 'register' # Este botón ahora va al registro
        st.rerun()
st.markdown("""
<div style="display:flex; justify-content:center; gap:3rem; padding: 3rem 0 1rem; border-top: 1px solid #F8FAFC; margin-top: 2rem;">
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

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

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

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

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
        <div class="price-plan-name">Gratis</div>
        <div class="price-amount"><span class="currency">$</span>0<span class="period">/para siempre</span></div>
        <p class="price-desc">Ideal para probar la plataforma con un proyecto.</p>
        <ul class="feat-list">
            <li><span class="check">✓</span> 1 campaña activa*</li>
            <li><span class="check">✓</span> 30 días de historial</li>
            <li><span class="check">✓</span> Dashboard básico</li>
            <li><span class="check">✓</span> Alertas por email</li>
        </ul>
        <div style="font-size: 0.7rem; color: #94A3B8; margin-top: 1rem; line-height: 1.4;">
            *Si tienes varias, analizaremos la de mayor inversión.
        </div>
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

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

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

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ========== CTA FINAL ==========
st.markdown("""
<div class="cta-section">
    <span class="section-label">Empieza hoy</span>
    <h2 class="cta-title">¿Listo para multiplicar<br>tu retorno publicitario?</h2>
    <p class="cta-sub">Empieza gratis. Sin tarjeta de crédito. Mejora tu plan cuando quieras.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    if st.button("🚀 Comenzar Gratis Ahora", key="cta_final", use_container_width=True):
        st.session_state.page = 'register' # Este botón ahora va al registro
        st.rerun()

# ========== FOOTER ==========
st.markdown("""
<div class="footer-wrap">
    <div class="nav-logo" style="font-size:0.9rem; color: #475569; align-items: center;">
        <img src="https://impulsolocal.com.mx/wp-content/uploads/2026/04/Logo-1.png" class="logo-mark" style="width:24px;height:24px;" alt="Logo">
        Ads Intelligence
    </div>
    <div class="footer-copy">© 2026 Ads Intelligence. Todos los derechos reservados.</div>
    <div class="footer-links">
        <a href="#">Privacidad</a>
        <a href="#">Términos</a>
        <a href="#">Contacto</a>
    </div>
</div>
""", unsafe_allow_html=True)
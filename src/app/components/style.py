"""Styles CSS globaux pour l'application YPerf - Design Premium"""

CSS = """
<style>
/* ============================================================
   FONTS + RESET (Google Fonts - Outfit & Inter)
   ============================================================ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

h1, h2, h3, .kpi-value, .pred-value, .hero-banner h1 {
    font-family: 'Outfit', sans-serif;
}

/* Main content area — minimal clean white/gray background */
.main .block-container {
    background-color: #f8fafc;
    background-image: radial-gradient(#e2e8f0 1px, transparent 1px);
    background-size: 20px 20px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

/* ============================================================
   SIDEBAR — Premium Dark Glassmorphism
   ============================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
section[data-testid="stSidebar"] [data-testid="stSlider"] p,
section[data-testid="stSidebar"] [data-testid="stSlider"] div,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #f8fafc !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}
/* Selectbox in sidebar */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: rgba(255, 255, 255, 0.06) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #f8fafc !important;
}
/* Radio buttons in sidebar */
section[data-testid="stSidebar"] .stRadio > div > label {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 4px 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    border: 1px solid transparent;
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    box-sizing: border-box;
    font-size: 0.95rem;
    font-weight: 500;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255,255,255,0.08);
    transform: translateX(4px);
    border-color: rgba(255,255,255,0.1);
}
/* Selected radio item */
section[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: linear-gradient(90deg, rgba(59,130,246,0.2) 0%, rgba(37,99,235,0.05) 100%);
    border-color: rgba(59,130,246,0.4);
    box-shadow: inset 4px 0 0 #3b82f6, 0 4px 15px rgba(0,0,0,0.2);
    transform: translateX(4px);
    font-weight: 600;
}

/* ============================================================
   HERO BANNER — Vibrant & Dynamic
   ============================================================ */
.hero-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 40%, #3b82f6 100%);
    color: white;
    padding: 48px 56px;
    border-radius: 24px;
    margin-bottom: 36px;
    box-shadow: 0 20px 40px rgba(37,99,235,0.25), inset 0 1px 0 rgba(255,255,255,0.2);
    position: relative;
    overflow: hidden;
    animation: fadeInDown 0.6s ease-out;
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
    border-radius: 50%;
    animation: pulse 8s infinite alternate;
}
@keyframes pulse {
    0% { transform: scale(1); opacity: 0.5; }
    100% { transform: scale(1.1); opacity: 1; }
}
.hero-banner h1 {
    font-size: 3rem;
    font-weight: 900;
    margin: 0 0 12px 0;
    letter-spacing: -1px;
    position: relative;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.hero-banner p {
    font-size: 1.15rem;
    opacity: 0.9;
    margin: 0;
    line-height: 1.6;
    position: relative;
    max-width: 80%;
}
.hero-rings {
    font-size: 2.5rem;
    letter-spacing: 8px;
    margin-bottom: 20px;
    display: block;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

/* ============================================================
   KPI CARDS — Glassmorphism & Hover FX
   ============================================================ */
.kpi-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03), inset 0 0 0 1px rgba(255,255,255,1);
    border-left: 5px solid;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%);
    pointer-events: none;
}
.kpi-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 32px rgba(0,0,0,0.08), inset 0 0 0 1px rgba(255,255,255,1);
}
.kpi-card.gold   { border-left-color: #f59e0b; }
.kpi-card.blue   { border-left-color: #3b82f6; }
.kpi-card.red    { border-left-color: #ef4444; }
.kpi-card.green  { border-left-color: #10b981; }
.kpi-card.black  { border-left-color: #334155; }

.kpi-icon {
    font-size: 1.8rem;
    position: absolute;
    right: 20px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0.15;
    font-size: 4rem;
    transition: all 0.3s;
}
.kpi-card:hover .kpi-icon {
    opacity: 0.25;
    transform: translateY(-50%) scale(1.1);
}
.kpi-value { font-size: 2.2rem; font-weight: 800; color: #0f172a; margin: 0; line-height: 1; }
.kpi-label { font-size: 0.8rem; color: #64748b; font-weight: 600; margin: 8px 0 0 0; text-transform: uppercase; letter-spacing: 1px; }

/* ============================================================
   SECTION HEADERS
   ============================================================ */
.section-header {
    background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 16px 24px;
    border-radius: 16px;
    margin: 40px 0 24px 0;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

/* ============================================================
   INSIGHT / WARNING BLOCKS
   ============================================================ */
.insight-block {
    background: linear-gradient(135deg, #f0fdfa 0%, #ccfbf1 100%);
    border-radius: 16px;
    padding: 18px 24px;
    border-left: 4px solid #0d9488;
    margin: 16px 0;
    font-size: 0.95rem;
    color: #115e59;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(13,148,136,0.08);
}
.insight-block strong { color: #0f766e; font-weight: 700; }

.warning-block {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border-radius: 16px;
    padding: 18px 24px;
    border-left: 4px solid #d97706;
    margin: 16px 0;
    font-size: 0.95rem;
    color: #92400e;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(217,119,6,0.08);
}

/* ============================================================
   PREDICTION CARD
   ============================================================ */
.pred-card {
    background: linear-gradient(145deg, #020617, #1e3a8a, #3b82f6);
    color: white;
    border-radius: 24px;
    padding: 32px 24px;
    text-align: center;
    box-shadow: 0 12px 30px rgba(37,99,235,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    transition: transform 0.3s, box-shadow 0.3s;
    position: relative;
    overflow: hidden;
}
.pred-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: url('data:image/svg+xml;utf8,<svg width="20" height="20" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><circle cx="2" cy="2" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
    opacity: 0.5;
}
.pred-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 40px rgba(37,99,235,0.4);
}
.pred-value { font-size: 3.5rem; font-weight: 900; margin: 12px 0; letter-spacing: -2px; position: relative; }
.pred-label { font-size: 0.85rem; opacity: 0.8; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 600; position: relative; }

/* ============================================================
   TABS — Modern Pill Design
   ============================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(241, 245, 249, 0.8);
    backdrop-filter: blur(8px);
    padding: 6px;
    border-radius: 16px;
    border: none;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    padding: 10px 20px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.95rem;
    color: #64748b;
    transition: all 0.3s ease;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #3b82f6 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
}

/* ============================================================
   ST.METRIC
   ============================================================ */
[data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 25px rgba(0,0,0,0.06);
    border-color: #e2e8f0;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: #64748b !important;
}
[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    color: #0f172a !important;
}

/* ============================================================
   BUTTONS — Dynamic Gradients
   ============================================================ */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.5px !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(37,99,235,0.3) !important;
    transition: all 0.3s ease !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    box-shadow: 0 8px 25px rgba(37,99,235,0.4) !important;
    transform: translateY(-2px) !important;
}

/* ============================================================
   DATAFRAME
   ============================================================ */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    border: 1px solid #e2e8f0;
}
[data-testid="stDataFrame"] table {
    font-family: 'Inter', sans-serif;
}

/* ============================================================
   EXPANDER
   ============================================================ */
[data-testid="stExpander"] {
    border-radius: 16px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    overflow: hidden;
    background: white;
    transition: all 0.3s ease;
}
[data-testid="stExpander"]:hover {
    box-shadow: 0 6px 15px rgba(0,0,0,0.05);
}
[data-testid="stExpander"] summary {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
}

/* ============================================================
   SELECTBOX / SLIDER
   ============================================================ */
[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border-color: #cbd5e1 !important;
    transition: all 0.3s ease;
    background: white;
}
[data-baseweb="select"] > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 4px rgba(59,130,246,0.1) !important;
}

/* ============================================================
   MEDALS BADGES
   ============================================================ */
.badge-gold   { background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #451a03; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; display: inline-block; box-shadow: 0 2px 8px rgba(245,158,11,0.3); border: 1px solid #fcd34d; }
.badge-silver { background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%); color: #334155; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; display: inline-block; box-shadow: 0 2px 8px rgba(148,163,184,0.2); border: 1px solid #e2e8f0; }
.badge-bronze { background: linear-gradient(135deg, #d97706 0%, #b45309 100%); color: #fffbeb; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.8rem; display: inline-block; box-shadow: 0 2px 8px rgba(180,83,9,0.3); border: 1px solid #d97706; }

/* ============================================================
   ATHLETE CARD
   ============================================================ */
.athlete-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid #f1f5f9;
}
.athlete-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    border-color: #e2e8f0;
}
.athlete-name { font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; color: #0f172a; margin: 12px 0 4px 0; }
.athlete-stats { font-size: 0.85rem; color: #64748b; font-weight: 500; }

/* ============================================================
   DIVIDER
   ============================================================ */
hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 32px 0;
}

/* ============================================================
   SPINNER
   ============================================================ */
[data-testid="stSpinner"] {
    color: #3b82f6 !important;
}

/* ============================================================
   ALERT / INFO
   ============================================================ */
[data-testid="stAlert"] {
    border-radius: 16px !important;
    font-size: 0.95rem !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

/* ============================================================
   FOOTER
   ============================================================ */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.8rem;
    padding: 32px 0 20px 0;
    border-top: 1px dashed #cbd5e1;
    margin-top: 64px;
    letter-spacing: 0.5px;
    font-family: 'Inter', sans-serif;
}

/* ============================================================
   PLOTLY CHARTS
   ============================================================ */
[data-testid="stArrowVegaLiteChart"],
.js-plotly-plot {
    border-radius: 16px;
    background: white;
    padding: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.02);
    border: 1px solid #f1f5f9;
}

/* ============================================================
   GLOBAL HEADINGS
   ============================================================ */
h1 {
    font-weight: 900 !important;
    letter-spacing: -1px !important;
    color: #0f172a !important;
}
h2 {
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
    color: #1e293b !important;
}
h3 {
    font-weight: 700 !important;
    color: #334155 !important;
}
</style>
"""

"""
Styles CSS globaux pour l'application YPerf
"""

CSS = """
<style>
/* ============================================================
   GLOBAL
   ============================================================ */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ============================================================
   SIDEBAR — thème sombre olympique
   ============================================================ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a2e 0%, #1a1a4e 55%, #0d1b2a 100%) !important;
}
section[data-testid="stSidebar"] * {
    color: #f0f0f0 !important;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}
section[data-testid="stSidebar"] .stRadio > div > label {
    background: rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 4px 0;
    transition: background 0.25s, transform 0.15s;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.05);
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    box-sizing: border-box;
}
section[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255,255,255,0.18);
    transform: translateX(4px);
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.8rem;
}

/* ============================================================
   HERO BANNER
   ============================================================ */
.hero-banner {
    background: linear-gradient(135deg, #0d0d3b 0%, #1a237e 35%, #283593 65%, #1565C0 100%);
    color: white;
    padding: 36px 40px;
    border-radius: 20px;
    margin-bottom: 28px;
    box-shadow: 0 8px 32px rgba(21,101,192,0.4);
}
.hero-banner h1 {
    font-size: 2.4rem;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.hero-banner p {
    font-size: 1.05rem;
    opacity: 0.85;
    margin: 0;
    line-height: 1.5;
}
.hero-rings {
    font-size: 2rem;
    letter-spacing: 6px;
    margin-bottom: 16px;
    display: block;
}

/* ============================================================
   KPI CARDS
   ============================================================ */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px 18px;
    box-shadow: 0 3px 16px rgba(0,0,0,0.08);
    border-left: 5px solid;
    transition: transform 0.22s, box-shadow 0.22s;
    height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 32px rgba(0,0,0,0.14);
}
.kpi-card.gold   { border-color: #FFD700; background: linear-gradient(135deg, #fff 60%, #fffde7); }
.kpi-card.blue   { border-color: #1E88E5; background: linear-gradient(135deg, #fff 60%, #e3f2fd); }
.kpi-card.red    { border-color: #E53935; background: linear-gradient(135deg, #fff 60%, #ffebee); }
.kpi-card.green  { border-color: #43A047; background: linear-gradient(135deg, #fff 60%, #e8f5e9); }
.kpi-card.black  { border-color: #37474f; background: linear-gradient(135deg, #fff 60%, #eceff1); }
.kpi-icon  { font-size: 1.5rem; margin-bottom: 4px; line-height: 1; }
.kpi-value { font-size: 1.9rem; font-weight: 800; color: #1a1a2e; margin: 0; line-height: 1.1; }
.kpi-label { font-size: 0.78rem; color: #6b7280; font-weight: 500; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 0.5px; }

/* ============================================================
   SECTION HEADERS
   ============================================================ */
.section-header {
    background: linear-gradient(90deg, #1e3a5f, #1976D2);
    color: white;
    padding: 11px 20px;
    border-radius: 10px;
    margin: 24px 0 14px 0;
    font-weight: 600;
    font-size: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ============================================================
   STORY / INSIGHT BLOCKS
   ============================================================ */
.insight-block {
    background: linear-gradient(135deg, #e8f0fe, #f0f4ff);
    border-radius: 12px;
    padding: 14px 18px;
    border-left: 4px solid #1E88E5;
    margin: 10px 0;
    font-size: 0.93rem;
    color: #1a237e;
    line-height: 1.55;
}
.insight-block strong { color: #0d47a1; }

.warning-block {
    background: linear-gradient(135deg, #fff8e1, #fff3e0);
    border-radius: 12px;
    padding: 14px 18px;
    border-left: 4px solid #FF8F00;
    margin: 10px 0;
    font-size: 0.93rem;
    color: #E65100;
}

/* ============================================================
   MEDAL BADGES
   ============================================================ */
.badge-gold   { background:#FFD700; color:#000; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; display:inline-block; }
.badge-silver { background:#C0C0C0; color:#000; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; display:inline-block; }
.badge-bronze { background:#CD7F32; color:#fff; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; display:inline-block; }

/* ============================================================
   ATHLETE CARD
   ============================================================ */
.athlete-card {
    background: white;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.09);
    text-align: center;
    transition: transform 0.2s;
}
.athlete-card:hover { transform: translateY(-3px); }
.athlete-name  { font-size: 1rem; font-weight: 700; color: #1a1a2e; margin: 8px 0 4px 0; }
.athlete-stats { font-size: 0.82rem; color: #6b7280; }

/* ============================================================
   PREDICTION CARD
   ============================================================ */
.pred-card {
    background: linear-gradient(135deg, #1a237e, #283593);
    color: white;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
    box-shadow: 0 6px 24px rgba(26,35,126,0.35);
}
.pred-value { font-size: 3rem; font-weight: 800; margin: 8px 0; }
.pred-label { font-size: 0.85rem; opacity: 0.8; letter-spacing: 0.5px; text-transform: uppercase; }

/* ============================================================
   TABS
   ============================================================ */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 0.9rem;
}

/* ============================================================
   DATAFRAME
   ============================================================ */
[data-testid="stDataFrame"] {
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}

/* ============================================================
   FOOTER
   ============================================================ */
.footer {
    text-align: center;
    color: #9e9e9e;
    font-size: 0.78rem;
    padding: 24px 0 12px 0;
    border-top: 1px solid #e5e7eb;
    margin-top: 48px;
}
</style>
"""

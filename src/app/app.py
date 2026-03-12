import streamlit as st
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import APP_CONFIG
from src.data.data_loader import load_raw_data
from src.data.data_cleaner import clean_data
from src.app.views import home, exploration, athletes, predictions
from src.app.components.style import CSS

st.set_page_config(**APP_CONFIG)

# ── Inject global CSS ─────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data
def get_data():
    df = load_raw_data()
    return clean_data(df)


df = get_data()

# ── Sidebar navigation ────────────────────────────────────────────────────
PAGES = {
    "🏠  Accueil": "home",
    "🔍  Exploration": "exploration",
    "🏃  Athlètes": "athletes",
    "🔮  Prédictions 2028": "predictions",
}

with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center; padding: 12px 0 6px 0;">
            <span style="font-size:2.4rem;">🏅</span>
            <div style="font-size:1.4rem; font-weight:800; letter-spacing:-0.5px; margin-top:4px;">YPerf</div>
            <div style="font-size:0.75rem; opacity:0.7; margin-top:2px;">Analyse des JO · Los Angeles 2028</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "Navigation",
        options=list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.divider()

    # Statistiques dataset
    n_athletes = df["Name"].nunique()
    n_countries = df["NOC"].nunique()
    yr_min, yr_max = int(df["Year"].min()), int(df["Year"].max())

    st.markdown(
        f"""
        <div style="font-size:0.78rem; opacity:0.75; line-height:1.8;">
        📊 <b>{len(df):,}</b> participations<br>
        🏃 <b>{n_athletes:,}</b> athlètes<br>
        🌍 <b>{n_countries}</b> pays<br>
        📅 <b>{yr_min} – {yr_max}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown(
        "<div style='font-size:0.72rem; opacity:0.55; text-align:center;'>Ynov Bachelor 3 · Data & IA · 2026</div>",
        unsafe_allow_html=True,
    )

# ── Page routing ──────────────────────────────────────────────────────────
key = PAGES[page]
if key == "home":
    home.show(df)
elif key == "exploration":
    exploration.show(df)
elif key == "athletes":
    athletes.show(df)
elif key == "predictions":
    predictions.show(df)

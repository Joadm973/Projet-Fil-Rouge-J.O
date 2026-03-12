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

st.set_page_config(**APP_CONFIG)


@st.cache_data
def get_data():
    df = load_raw_data()
    return clean_data(df)


df = get_data()

# ── Sidebar navigation ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏅 YPerf")
    st.markdown("*Analyse des Performances Olympiques*")
    st.divider()
    page = st.radio(
        "Navigation",
        options=["🏠 Accueil", "🔍 Exploration", "🏃 Athlètes", "🔮 Prédictions 2028"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"📁 {len(df):,} lignes | {df['Year'].min()}–{df['Year'].max()}")
    st.caption("Ynov Bachelor 3 — Data & IA — 2026")

# ── Page routing ──────────────────────────────────────────────────────────
if page == "🏠 Accueil":
    home.show(df)
elif page == "🔍 Exploration":
    exploration.show(df)
elif page == "🏃 Athlètes":
    athletes.show(df)
elif page == "🔮 Prédictions 2028":
    predictions.show(df)

"""
Composants HTML réutilisables — cartes KPI, badges, blocs narratifs
"""
import streamlit as st


# ── Palette olympique ─────────────────────────────────────────────────────
MEDAL_COLORS = {"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}
PLOTLY_THEME = dict(
    template="plotly_white",
    font_family="Inter, Segoe UI, sans-serif",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


def kpi_card(icon: str, value: str, label: str, color: str = "blue") -> str:
    """Retourne le HTML d'une carte KPI colorée."""
    return f"""
    <div class="kpi-card {color}">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <p class="kpi-label">{label}</p>
    </div>
    """


def render_kpis(items: list[dict]):
    """
    Affiche une rangée de cartes KPI.

    items = [{"icon": "🏅", "value": "1 234", "label": "Médailles", "color": "gold"}, ...]
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.markdown(
                kpi_card(
                    item["icon"], item["value"], item["label"], item.get("color", "blue")
                ),
                unsafe_allow_html=True,
            )


def section_header(title: str):
    """Affiche un header de section stylisé."""
    st.markdown(
        f'<div class="section-header">{title}</div>',
        unsafe_allow_html=True,
    )


def insight(text: str):
    """Affiche un bloc narratif bleu."""
    st.markdown(
        f'<div class="insight-block">💡 {text}</div>',
        unsafe_allow_html=True,
    )


def warning_insight(text: str):
    """Affiche un bloc narratif orange."""
    st.markdown(
        f'<div class="warning-block">⚠️ {text}</div>',
        unsafe_allow_html=True,
    )


def prediction_card(country: str, value: int, flag: str = ""):
    """Affiche la carte résultat de prédiction."""
    st.markdown(
        f"""
        <div class="pred-card">
            <div class="pred-label">Médailles prédites 2028</div>
            <div class="pred-value">{flag} {value}</div>
            <div class="pred-label">{country}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_banner(title: str, subtitle: str):
    """Affiche le hero banner principal."""
    st.markdown(
        f"""
        <div class="hero-banner">
            <span class="hero-rings">⭕🔵🟡⚫🟢🔴</span>
            <h1>🏅 {title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

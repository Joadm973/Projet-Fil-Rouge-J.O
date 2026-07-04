"""
Composants HTML réutilisables — cartes KPI, badges, blocs narratifs
"""
import streamlit as st


# ── Palette olympique ─────────────────────────────────────────────────────
MEDAL_COLORS = {"Gold": "#f59e0b", "Silver": "#9ca3af", "Bronze": "#b45309"}

PLOTLY_THEME = dict(
    template="plotly_white",
    font=dict(family="Inter, Segoe UI, sans-serif", size=12, color="#374151"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(248,250,252,0.5)",
    margin=dict(t=48, r=16, b=40, l=16),
    title_font=dict(size=14, color="#0f172a", family="Inter, Segoe UI, sans-serif"),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#e5e7eb",
        font_size=12,
        font_family="Inter, Segoe UI, sans-serif",
    ),
)

_AXIS_STYLE = dict(
    gridcolor="#f1f5f9",
    linecolor="#e2e8f0",
    tickfont=dict(size=11, color="#6b7280"),
    title_font=dict(size=12, color="#374151"),
    zeroline=False,
)


def polish_fig(fig):
    """Apply consistent axis + grid styling to any Plotly figure."""
    fig.update_xaxes(**_AXIS_STYLE)
    fig.update_yaxes(**_AXIS_STYLE)
    return fig


def st_plotly(fig, **kwargs):
    """Polish + render a Plotly figure via st.plotly_chart."""
    polish_fig(fig)
    kwargs.setdefault("width", "stretch")
    st.plotly_chart(fig, **kwargs)


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

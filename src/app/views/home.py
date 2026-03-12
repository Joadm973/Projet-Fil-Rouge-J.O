import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.analysis.exploratory import medals_by_year, participation_over_time


def show(df):
    st.title("🏅 YPerf — Performances Olympiques")
    st.markdown(
        "**Exploration des Jeux Olympiques historiques & Prédictions pour Los Angeles 2028**"
    )
    st.divider()

    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]

    # ── KPIs ──────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Éditions", df["Year"].nunique())
    c2.metric("🏃 Athlètes", f"{df['Name'].nunique():,}")
    c3.metric("🌍 Pays", df["NOC"].nunique())
    c4.metric("🏋️ Sports", df["Sport"].nunique())

    st.divider()

    # ── Médailles par édition + répartition genre ──────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        st.subheader("📊 Médailles distribuées par édition")
        mby = medals_by_year(df)
        fig = px.bar(
            mby,
            x="Year",
            y="Count",
            color="Medal",
            barmode="stack",
            color_discrete_map={
                "Gold": "#FFD700",
                "Silver": "#C0C0C0",
                "Bronze": "#CD7F32",
            },
            labels={"Count": "Médailles", "Year": "Année"},
        )
        fig.update_layout(legend_title_text="Médaille", height=360)
        st.plotly_chart(fig, width='stretch')

    with col_r:
        st.subheader("⚤ Répartition par genre")
        genders = df.groupby("Sex")["Name"].nunique().reset_index()
        genders["Sex"] = genders["Sex"].map({"M": "Hommes", "F": "Femmes"})
        fig2 = px.pie(
            genders,
            values="Name",
            names="Sex",
            hole=0.45,
            color_discrete_sequence=["#1E88E5", "#E91E63"],
        )
        fig2.update_layout(height=360)
        st.plotly_chart(fig2, width='stretch')

    # ── Évolution participation ────────────────────────────────────────────
    st.subheader("📈 Évolution de la participation aux JO d'été")
    part = participation_over_time(df)
    fig3 = px.line(
        part,
        x="Year",
        y=["Athlètes", "Pays", "Sports"],
        markers=True,
        labels={"value": "Nombre", "Year": "Année", "variable": ""},
    )
    fig3.update_layout(height=360)
    st.plotly_chart(fig3, width='stretch')

import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.analysis.exploratory import top_athletes as compute_top_athletes


def show(df):
    st.title("🏃 Athlètes")
    st.divider()

    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

    # ── Filtres (sidebar) ─────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("⚙️ Filtres athlètes")
        sports_list = ["Tous"] + sorted(df["Sport"].unique().tolist())
        sel_sport = st.selectbox("Sport", sports_list, key="ath_sport")
        countries_list = ["Tous"] + sorted(df["Team"].unique().tolist())
        sel_country = st.selectbox("Pays", countries_list, key="ath_country")
        medal_filter = st.multiselect(
            "Médailles",
            ["Gold", "Silver", "Bronze"],
            default=["Gold", "Silver", "Bronze"],
            key="ath_medals",
        )

    filtered = medals_df[medals_df["Medal"].isin(medal_filter)]
    if sel_sport != "Tous":
        filtered = filtered[filtered["Sport"] == sel_sport]
    if sel_country != "Tous":
        filtered = filtered[filtered["Team"] == sel_country]

    # ── Top 20 athlètes ───────────────────────────────────────────────────
    top = (
        filtered.groupby(["Name", "Team", "Sport"])
        .size()
        .nlargest(20)
        .reset_index(name="Médailles")
    )

    st.subheader("🥇 Top 20 athlètes les plus médaillés")
    fig = px.bar(
        top,
        x="Médailles",
        y="Name",
        orientation="h",
        color="Sport",
        hover_data=["Team"],
        labels={"Name": "Athlète"},
    )
    fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, width='stretch')

    # ── Détail médailles des Top 10 ───────────────────────────────────────
    st.subheader("📊 Détail or / argent / bronze — Top 10")
    top10_names = top["Name"].head(10)
    detail = (
        filtered[filtered["Name"].isin(top10_names)]
        .groupby(["Name", "Medal"])
        .size()
        .reset_index(name="Count")
    )
    fig2 = px.bar(
        detail,
        x="Name",
        y="Count",
        color="Medal",
        barmode="group",
        color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
        labels={"Count": "Médailles", "Name": "Athlète"},
    )
    fig2.update_layout(height=420, xaxis_tickangle=-30)
    st.plotly_chart(fig2, width='stretch')

    # ── Tableau ───────────────────────────────────────────────────────────
    st.subheader("📋 Tableau des performances")
    st.dataframe(
        top.rename(columns={"Name": "Athlète", "Team": "Pays"}).reset_index(drop=True),
        width='stretch',
        hide_index=True,
    )

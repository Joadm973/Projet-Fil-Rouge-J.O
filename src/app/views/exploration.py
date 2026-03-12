import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def show(df):
    st.title("🔍 Exploration des Données")
    st.divider()

    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]

    # ── Filtres (sidebar) ─────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("⚙️ Filtres exploration")
        year_range = st.slider(
            "Fourchette d'années",
            int(df["Year"].min()),
            int(df["Year"].max()),
            (int(df["Year"].min()), int(df["Year"].max())),
        )

    filtered = medals_df[
        (medals_df["Year"] >= year_range[0]) & (medals_df["Year"] <= year_range[1])
    ]

    # ── Top 15 pays ───────────────────────────────────────────────────────
    st.subheader("🏆 Top 15 pays par médailles")
    top_teams = filtered.groupby("Team").size().nlargest(15).index
    top_data = (
        filtered[filtered["Team"].isin(top_teams)]
        .groupby(["Team", "Medal"])
        .size()
        .reset_index(name="Count")
    )
    fig = px.bar(
        top_data,
        x="Team",
        y="Count",
        color="Medal",
        barmode="stack",
        color_discrete_map={"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"},
        labels={"Count": "Médailles", "Team": "Pays"},
    )
    fig.update_layout(xaxis_tickangle=-40, height=420)
    st.plotly_chart(fig, width='stretch')

    col_l, col_r = st.columns(2)

    # ── Top sports ────────────────────────────────────────────────────────
    with col_l:
        st.subheader("🏋️ Top 10 sports")
        top_sports = (
            filtered.groupby("Sport").size().nlargest(10).reset_index(name="Count")
        )
        fig2 = px.bar(
            top_sports,
            y="Sport",
            x="Count",
            orientation="h",
            color="Count",
            color_continuous_scale="Blues",
            labels={"Count": "Médailles"},
        )
        fig2.update_layout(height=420, showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig2, width='stretch')

    # ── Évolution Or — Top 5 pays ─────────────────────────────────────────
    with col_r:
        st.subheader("📆 Évolution médailles d'or — Top 5")
        gold = filtered[filtered["Medal"] == "Gold"]
        top5 = gold.groupby("Team").size().nlargest(5).index
        gold_evo = (
            gold[gold["Team"].isin(top5)]
            .groupby(["Year", "Team"])
            .size()
            .reset_index(name="Or")
        )
        fig3 = px.line(
            gold_evo,
            x="Year",
            y="Or",
            color="Team",
            markers=True,
            labels={"Or": "Médailles d'or", "Year": "Année"},
        )
        fig3.update_layout(height=420)
        st.plotly_chart(fig3, width='stretch')

    # ── Carte mondiale ────────────────────────────────────────────────────
    st.subheader("🗺️ Carte mondiale des médailles")
    medals_by_noc = (
        filtered.groupby(["NOC", "Team"]).size().reset_index(name="Total")
    )
    fig_map = px.choropleth(
        medals_by_noc,
        locations="NOC",
        color="Total",
        hover_name="Team",
        color_continuous_scale="YlOrRd",
        labels={"Total": "Médailles"},
        title=f"Total des médailles par pays ({year_range[0]}–{year_range[1]})",
    )
    fig_map.update_layout(height=460)
    st.plotly_chart(fig_map, width='stretch')

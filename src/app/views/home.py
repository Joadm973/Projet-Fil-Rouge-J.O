"""Page d'accueil de l'application YPerf, présentant les KPIs globaux, les visualisations historiques et les insights clés sur les performances olympiques."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.analysis.exploratory import medals_by_year, participation_over_time
from src.app.components.cards import (
    render_kpis, section_header, insight, hero_banner, MEDAL_COLORS, PLOTLY_THEME, st_plotly
)

CHART_H = 380


def show(df: pd.DataFrame):
    """Affiche la page d'accueil avec les KPIs globaux, les visualisations historiques et les insights clés."""
    # ── Hero ──────────────────────────────────────────────────────────────
    hero_banner(
        "YPerf — Performances Olympiques",
        "Explorez 60 ans d'histoire olympique et découvrez les prédictions pour Los Angeles 2028 🇺🇸",
    )

    # ── KPIs ──────────────────────────────────────────────────────────────
    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    last_year = int(df["Year"].max())
    last_edition = df[df["Year"] == last_year]
    gold_leaders = medals_df[medals_df["Medal"] == "Gold"].groupby("Team").size()
    top_country = gold_leaders.idxmax() if len(gold_leaders) else "—"

    render_kpis([
        {"icon": "📅", "value": str(df["Year"].nunique()), "label": "Éditions des JO", "color": "blue"},
        {"icon": "🏃", "value": f"{df['Name'].nunique():,}", "label": "Athlètes uniques", "color": "green"},
        {"icon": "🌍", "value": str(df["NOC"].nunique()), "label": "Pays représentés", "color": "red"},
        {"icon": "🏋️", "value": str(df["Sport"].nunique()), "label": "Sports différents", "color": "black"},
        {"icon": "🥇", "value": f"{len(medals_df[medals_df['Medal']=='Gold']):,}", "label": "Médailles d'or totales", "color": "gold"},
    ])

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1 : Médailles par édition + répartition genre ─────────────────
    section_header("📊 Vue d'ensemble historique")
    col_l, col_r = st.columns([3, 2])

    with col_l:
        mby = medals_by_year(df)
        fig = px.bar(
            mby, x="Year", y="Count", color="Medal",
            barmode="stack",
            color_discrete_map=MEDAL_COLORS,
            labels={"Count": "Médailles", "Year": "Année", "Medal": "Type"},
            title="Médailles distribuées par édition",
        )
        fig.update_layout(**PLOTLY_THEME, height=CHART_H, legend_title_text="",
                          title_font_size=14)
        fig.update_traces(marker_line_width=0)
        st_plotly(fig)

    with col_r:
        # Gender participation evolution (area chart, not simple pie)
        gender_year = df.groupby(["Year", "Sex"])["Name"].nunique().reset_index()
        gender_year["Sex"] = gender_year["Sex"].map({"M": "Hommes", "F": "Femmes"})
        fig2 = px.area(
            gender_year, x="Year", y="Name", color="Sex",
            color_discrete_map={"Hommes": "#1E88E5", "Femmes": "#E91E63"},
            labels={"Name": "Athlètes", "Year": "Année", "Sex": "Genre"},
            title="Évolution de la parité hommes / femmes",
        )
        fig2.update_layout(**PLOTLY_THEME, height=CHART_H, legend_title_text="",
                           title_font_size=14)
        st_plotly(fig2)

    insight(
        "Les JO 2020 (Tokyo) ont enregistré le plus grand nombre d'athlètes. "
        "La parité hommes/femmes a spectaculairement progressé : les femmes représentent "
        "aujourd'hui près de <strong>50 %</strong> des participations."
    )

    # ── Row 2 : Carte mondiale + Top 10 pays ──────────────────────────────
    section_header("🌍 Rayonnement mondial")
    col_map, col_bar = st.columns([3, 2])

    with col_map:
        # Agrégation par NOC pour éviter les doublons géographiques causés par les sous-équipes (ex: USA-1, USA-2)
        noc_totals = medals_df.groupby("NOC").size().reset_index(name="Total")
        main_teams = medals_df.groupby(["NOC", "Team"]).size().reset_index(name="count")
        main_teams = main_teams.sort_values("count", ascending=False).drop_duplicates("NOC")
        medals_by_noc = noc_totals.merge(main_teams[["NOC", "Team"]], on="NOC")

        fig_map = px.choropleth(
            medals_by_noc, locations="NOC", color="Total",
            hover_name="Team", hover_data={"NOC": False},
            color_continuous_scale="YlOrRd",
            labels={"Total": "Médailles"},
            title="Total des médailles par pays (toutes éditions)",
        )
        fig_map.update_layout(
            **PLOTLY_THEME, height=CHART_H,
            geo=dict(showframe=False, showcoastlines=True,
                     coastlinecolor="#dddddd", bgcolor="rgba(0,0,0,0)"),
            coloraxis_colorbar=dict(title="Médailles", thickness=12),
            title_font_size=14,
        )
        st_plotly(fig_map)

    with col_bar:
        top10 = (
            medals_df.groupby("Team").size()
            .nlargest(10).reset_index(name="Médailles")
        )
        fig_top = px.bar(
            top10, y="Team", x="Médailles", orientation="h",
            color="Médailles", color_continuous_scale="Blues",
            title="Top 10 pays toutes médailles (1896-2024)",
            labels={"Team": ""},
        )
        fig_top.update_layout(
            **PLOTLY_THEME, height=CHART_H, yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False, title_font_size=14,
        )
        fig_top.update_traces(marker_line_width=0)
        st_plotly(fig_top)

    # ── Row 3 : Participation + Treemap sports ─────────────────────────────
    section_header("📈 Tendances & Sports")
    col_part, col_tree = st.columns(2)

    with col_part:
        part = participation_over_time(df)
        fig3 = px.line(
            part, x="Year", y=["Athlètes", "Pays", "Sports"],
            markers=True,
            color_discrete_sequence=["#1E88E5", "#43A047", "#E53935"],
            labels={"value": "Nombre", "Year": "Année", "variable": ""},
            title="Évolution de la participation aux JO d'été",
        )
        fig3.update_layout(**PLOTLY_THEME, height=360, title_font_size=14,
                           legend=dict(orientation="h", yanchor="bottom", y=1.02))
        fig3.update_traces(line_width=2.5)
        st_plotly(fig3)

    with col_tree:
        sport_medals = medals_df.groupby("Sport").size().reset_index(name="Médailles")
        fig_tree = px.treemap(
            sport_medals, path=["Sport"], values="Médailles",
            color="Médailles", color_continuous_scale="Blues",
            title="Répartition des médailles par sport",
        )
        fig_tree.update_layout(
            **PLOTLY_THEME, height=360, title_font_size=14,
        )
        st_plotly(fig_tree)

    insight(
        f"Le pays le plus lauréat en médailles d'or toutes éditions confondues est "
        f"<strong>{top_country}</strong>. "
        "L'édition de {last_year} à Paris a vu la participation de "
        f"<strong>{last_edition['NOC'].nunique()}</strong> pays."
        .format(last_year=last_year)
    )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )

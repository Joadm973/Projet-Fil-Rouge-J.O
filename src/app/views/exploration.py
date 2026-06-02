import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.app.components.cards import (
    section_header, insight, warning_insight, MEDAL_COLORS, PLOTLY_THEME
)

CHART_H = 420


def show(df: pd.DataFrame):
    st.title("🔍 Exploration des Données")
    st.markdown("Analysez les performances olympiques selon vos critères — pays, sports, disciplines et tendances.")

    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

    # ── Filtres globaux dans la sidebar ───────────────────────────────────
    with st.sidebar:
        st.subheader("⚙️ Filtres")
        year_range = st.slider(
            "Période",
            int(df["Year"].min()), int(df["Year"].max()),
            (int(df["Year"].min()), int(df["Year"].max())),
        )
        season_opts = ["Toutes", "Summer", "Winter"]
        season = st.selectbox("Saison", season_opts, index=1) if "Season" in df.columns else "Summer"
        gender_opts = ["Tous", "M", "F"]
        gender = st.radio("Genre", gender_opts, horizontal=True)

    # Appliquer les filtres
    filt = medals_df.copy()
    filt = filt[(filt["Year"] >= year_range[0]) & (filt["Year"] <= year_range[1])]
    if "Season" in filt.columns and season != "Toutes":
        filt = filt[filt["Season"] == season]
    if gender != "Tous":
        filt = filt[filt["Sex"] == gender]

    n_medals = len(filt)
    n_countries = filt["NOC"].nunique()
    n_sports = filt["Sport"].nunique()

    # Mini-KPIs période
    c1, c2, c3 = st.columns(3)
    c1.metric("🏅 Médailles sur la période", f"{n_medals:,}")
    c2.metric("🌍 Pays médaillés", str(n_countries))
    c3.metric("🏋️ Sports", str(n_sports))

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Pays", "🏋️ Sports", "📆 Tendances", "🔥 Heatmap"])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — PAYS
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        section_header("🏆 Classement des pays")

        col_left, col_right = st.columns([2, 1])
        with col_left:
            n_top = st.slider("Nombre de pays", 5, 30, 15, key="top_n_countries")

        top_teams = filt.groupby("Team").size().nlargest(n_top).index
        top_data = (
            filt[filt["Team"].isin(top_teams)]
            .groupby(["Team", "Medal"])
            .size()
            .reset_index(name="Count")
        )
        fig = px.bar(
            top_data, x="Team", y="Count", color="Medal",
            barmode="stack",
            color_discrete_map=MEDAL_COLORS,
            labels={"Count": "Médailles", "Team": "Pays", "Medal": "Type"},
            title=f"Top {n_top} pays — {year_range[0]}–{year_range[1]}",
        )
        fig.update_layout(**PLOTLY_THEME, height=CHART_H, xaxis_tickangle=-35,
                          legend_title_text="", title_font_size=13)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, width='stretch')

        # Carte choroplèthe
        section_header("🗺️ Carte mondiale des médailles")
        medals_by_noc = filt.groupby(["NOC", "Team"]).size().reset_index(name="Total")
        fig_map = px.choropleth(
            medals_by_noc, locations="NOC", color="Total",
            hover_name="Team", hover_data={"NOC": False},
            color_continuous_scale="YlOrRd",
            labels={"Total": "Médailles"},
            title=f"Médailles par pays ({year_range[0]}–{year_range[1]})",
        )
        fig_map.update_layout(
            **PLOTLY_THEME, height=460,
            geo=dict(showframe=False, showcoastlines=True,
                     coastlinecolor="#e0e0e0", bgcolor="rgba(0,0,0,0)"),
            coloraxis_colorbar=dict(title="Médailles", thickness=12),
            title_font_size=13,
            margin=dict(l=0, r=0, t=36, b=0),
        )
        st.plotly_chart(fig_map, width='stretch')

        # Sunburst pays → médaille
        section_header("🌐 Répartition pays → type de médaille")
        top6 = filt.groupby("Team").size().nlargest(6).index
        sun_data = (
            filt[filt["Team"].isin(top6)]
            .groupby(["Team", "Medal"])
            .size()
            .reset_index(name="Count")
        )
        fig_sun = px.sunburst(
            sun_data, path=["Team", "Medal"], values="Count",
            color="Medal", color_discrete_map=MEDAL_COLORS,
            title="Top 6 pays — composition des médailles",
        )
        fig_sun.update_layout(**PLOTLY_THEME, height=480, title_font_size=13,
                              margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_sun, width='stretch')

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — SPORTS
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        col_sl, col_sr = st.columns(2)

        with col_sl:
            section_header("🏋️ Top sports par médailles")
            top_sports = filt.groupby("Sport").size().nlargest(15).reset_index(name="Count")
            fig2 = px.bar(
                top_sports, y="Sport", x="Count", orientation="h",
                color="Count", color_continuous_scale="Blues",
                labels={"Count": "Médailles", "Sport": ""},
                title="Top 15 sports — nombre de médailles",
            )
            fig2.update_layout(
                **PLOTLY_THEME, height=520,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=13,
            )
            fig2.update_traces(marker_line_width=0)
            st.plotly_chart(fig2, width='stretch')

        with col_sr:
            section_header("⚤ Médailles par genre dans les sports")
            gender_sport = (
                filt.groupby(["Sport", "Sex"]).size().reset_index(name="Count")
            )
            gender_sport["Sex"] = gender_sport["Sex"].map({"M": "Hommes", "F": "Femmes"})
            top_s_gender = gender_sport[
                gender_sport["Sport"].isin(
                    filt.groupby("Sport").size().nlargest(10).index
                )
            ]
            fig_gs = px.bar(
                top_s_gender, y="Sport", x="Count", color="Sex",
                orientation="h", barmode="group",
                color_discrete_map={"Hommes": "#1E88E5", "Femmes": "#E91E63"},
                labels={"Count": "Médailles", "Sport": ""},
                title="Genres — top 10 sports",
            )
            fig_gs.update_layout(
                **PLOTLY_THEME, height=520,
                yaxis={"categoryorder": "total ascending"},
                legend_title_text="", title_font_size=13,
            )
            st.plotly_chart(fig_gs, width='stretch')

        # Treemap hiérarchique
        section_header("🗂️ Treemap Sport → Médaille")
        tree_data = (
            filt.groupby(["Sport", "Medal"]).size().reset_index(name="Count")
        )
        fig_tree = px.treemap(
            tree_data, path=["Sport", "Medal"], values="Count",
            color="Medal", color_discrete_map=MEDAL_COLORS,
            title="Hiérarchie Sport → Type de médaille",
        )
        fig_tree.update_layout(
            **PLOTLY_THEME, height=460, title_font_size=13,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_tree, width='stretch')

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — TENDANCES
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        section_header("📈 Évolution Or — comparaison pays")
        all_teams = sorted(filt["Team"].unique())
        default_teams = ["United States", "Soviet Union", "China", "Great Britain", "France"]
        default_teams = [t for t in default_teams if t in all_teams][:5]
        sel_teams = st.multiselect("Pays à comparer", all_teams, default=default_teams)

        if sel_teams:
            gold_evo = (
                filt[
                    (filt["Medal"] == "Gold") & (filt["Team"].isin(sel_teams))
                ]
                .groupby(["Year", "Team"])
                .size()
                .reset_index(name="Or")
            )
            fig_evo = px.line(
                gold_evo, x="Year", y="Or", color="Team",
                markers=True,
                labels={"Or": "Médailles d'or", "Year": "Année"},
                title="Évolution des médailles d'or par pays",
            )
            fig_evo.update_layout(**PLOTLY_THEME, height=420, legend_title_text="",
                                   title_font_size=13)
            fig_evo.update_traces(line_width=2.5)
            st.plotly_chart(fig_evo, width='stretch')
        else:
            st.info("Sélectionnez au moins un pays.")

        # Parité temporelle
        section_header("⚤ Évolution de la parité de genre dans les sports")
        parity = (
            df[df["Year"] >= year_range[0]]
            .groupby(["Year", "Sex"])["Name"].nunique().reset_index()
        )
        parity["Sex"] = parity["Sex"].map({"M": "Hommes", "F": "Femmes"})
        pivot_p = parity.pivot(index="Year", columns="Sex", values="Name").fillna(0)
        pivot_p["Ratio F/(F+H)"] = (
            pivot_p.get("Femmes", 0) / (pivot_p.get("Femmes", 0) + pivot_p.get("Hommes", 0)) * 100
        )
        pivot_p = pivot_p.reset_index()
        fig_par = px.area(
            parity, x="Year", y="Name", color="Sex",
            color_discrete_map={"Hommes": "#90CAF9", "Femmes": "#F48FB1"},
            labels={"Name": "Athlètes uniques", "Year": "Année"},
            title="Évolution de la parité hommes / femmes",
        )
        fig_par.update_layout(**PLOTLY_THEME, height=360, legend_title_text="",
                               title_font_size=13)
        st.plotly_chart(fig_par, width='stretch')

        insight(
            "La part des femmes aux JO est passée de quasi-zéro en 1960 à près de "
            "<strong>50 %</strong> lors des dernières éditions. Une tendance continue vers la parité."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — HEATMAP
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        section_header("🔥 Heatmap : médailles d'or — top pays × éditions")

        top_hm = filt[filt["Medal"] == "Gold"].groupby("Team").size().nlargest(15).index
        hm_data = (
            filt[(filt["Medal"] == "Gold") & (filt["Team"].isin(top_hm))]
            .groupby(["Year", "Team"])
            .size()
            .unstack(fill_value=0)
        )
        fig_hm = px.imshow(
            hm_data.T,
            color_continuous_scale="YlOrRd",
            labels=dict(x="Année", y="Pays", color="Médailles d'or"),
            title="Heatmap — médailles d'or par pays et par édition",
            aspect="auto",
        )
        fig_hm.update_layout(**PLOTLY_THEME, height=480, title_font_size=13,
                              margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_hm, width='stretch')

        insight(
            "Les cases jaune-orange foncé révèlent les dominations historiques. "
            "Les États-Unis et l'URSS montrent une présence quasi-systématique jusqu'en 1991."
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )


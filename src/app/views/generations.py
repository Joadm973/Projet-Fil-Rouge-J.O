"""Vue Nouvelles générations — détection des talents émergents."""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.app.components.cards import PLOTLY_THEME, insight, section_header, warning_insight, st_plotly
from src.models.generations import (
    detect_breakout_athletes,
    detect_generation_shift,
    detect_new_gen_athletes,
    detect_new_medaling_nations,
)

CHART_H = 420


@st.cache_data
def _new_gen(df: pd.DataFrame) -> pd.DataFrame:
    return detect_new_gen_athletes(df)


@st.cache_data
def _breakout(df: pd.DataFrame) -> pd.DataFrame:
    return detect_breakout_athletes(df)


@st.cache_data
def _shift(df: pd.DataFrame) -> pd.DataFrame:
    return detect_generation_shift(df)


@st.cache_data
def _new_nations(df: pd.DataFrame) -> pd.DataFrame:
    return detect_new_medaling_nations(df)


def show(df: pd.DataFrame) -> None:
    st.title("🌱 Nouvelles générations olympiques")
    st.markdown(
        "Identification des **athlètes émergents** et des **nations montantes** "
        "basée sur les tendances 2016–2024, en vue de Los Angeles 2028."
    )

    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Talents 2016+",
        "⚡ Breakouts 2020+",
        "🔄 Renouvellement par sport",
        "🌍 Nouvelles nations médaillées",
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — NOUVEAUX TALENTS (debut 2016+)
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        section_header("🚀 Talents émergents — 1ère participation olympique en 2016 ou après")

        ng = _new_gen(df)

        # KPIs
        k1, k2, k3 = st.columns(3)
        k1.metric("Athlètes nouvelle génération", f"{len(ng):,}")
        k2.metric("Ayant débuté en 2020+", int((ng["debut_year"] >= 2020).sum()))
        k3.metric("Disciplines représentées", ng["Sport"].nunique())

        st.markdown("---")

        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            sports_ng = ["Tous"] + sorted(ng["Sport"].unique())
            sel_sport = st.selectbox("Discipline", sports_ng, key="ng_sport")
            debut_min = st.selectbox("Débuts depuis", [2016, 2020, 2024], key="ng_debut")
            top_n = st.slider("Afficher top N", 10, 30, 15, key="ng_topn")

        filtered = ng[ng["debut_year"] >= debut_min]
        if sel_sport != "Tous":
            filtered = filtered[filtered["Sport"] == sel_sport]
        top = filtered.head(top_n)

        with col_f2:
            if not top.empty:
                fig = px.bar(
                    top,
                    x="score", y="Name",
                    orientation="h",
                    color="score",
                    color_continuous_scale="Viridis",
                    hover_data=["Team", "Sport", "debut_year", "gold", "silver", "bronze"],
                    text="score",
                    title=f"Top {top_n} talents (Or=3pts, Argent=2pts, Bronze=1pt)",
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    **PLOTLY_THEME, height=CHART_H,
                    coloraxis_showscale=False,
                    yaxis={"categoryorder": "total ascending"},
                    title_font_size=13,
                )
                st_plotly(fig)

        st.markdown("---")

        # Scatter debut_year vs score
        section_header("Trajectoire des talents par édition de début")
        fig_sc = px.scatter(
            ng.head(200),
            x="debut_year", y="score",
            color="Sport",
            size="nb_medals",
            hover_name="Name",
            hover_data=["Team", "nb_editions"],
            title="Score vs année de début — top 200 talents (bulles = nb médailles)",
        )
        fig_sc.update_layout(
            **PLOTLY_THEME, height=420,
            xaxis=dict(tickmode="array", tickvals=[2016, 2020, 2024]),
            title_font_size=13,
        )
        st_plotly(fig_sc)

        with st.expander("📋 Tableau complet"):
            st.dataframe(
                filtered[["Name", "Team", "Sport", "debut_year", "nb_editions",
                           "gold", "silver", "bronze", "score"]].head(100),
                width="stretch",
                hide_index=True,
            )

        insight(
            "Un athlète est considéré <strong>nouvelle génération</strong> si sa 1ère "
            "participation olympique (été) date de 2016 ou après. Le score combine "
            "Or=3 pts, Argent=2 pts, Bronze=1 pt — il reflète la valeur sportive, "
            "pas seulement le volume de médailles."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — BREAKOUTS (1ère médaille en 2020+, aucune avant)
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        section_header("⚡ Athlètes en percée — 1ère médaille en 2020 ou après")

        bo = _breakout(df)

        k1, k2, k3 = st.columns(3)
        k1.metric("Athlètes en percée", f"{len(bo):,}")
        k2.metric("Disciplines", bo["Sport"].nunique())
        k3.metric("Nations représentées", bo["Team"].nunique())

        st.markdown("---")

        col_b1, col_b2 = st.columns([1, 3])
        with col_b1:
            sports_bo = ["Tous"] + sorted(bo["Sport"].unique())
            sel_sport_bo = st.selectbox("Discipline", sports_bo, key="bo_sport")
            top_bo = st.slider("Afficher top N", 10, 30, 15, key="bo_topn")

        filt_bo = bo.copy()
        if sel_sport_bo != "Tous":
            filt_bo = filt_bo[filt_bo["Sport"] == sel_sport_bo]
        top_bo_df = filt_bo.head(top_bo)

        with col_b2:
            if not top_bo_df.empty:
                fig_bo = px.bar(
                    top_bo_df,
                    x="score", y="Name",
                    orientation="h",
                    color="score",
                    color_continuous_scale="Plasma",
                    hover_data=["Team", "Sport", "first_medal_year", "medals_recent"],
                    text="score",
                    title=f"Top {top_bo} percées olympiques depuis 2020",
                )
                fig_bo.update_traces(textposition="outside")
                fig_bo.update_layout(
                    **PLOTLY_THEME, height=CHART_H,
                    coloraxis_showscale=False,
                    yaxis={"categoryorder": "total ascending"},
                    title_font_size=13,
                )
                st_plotly(fig_bo)

        # Distribution par sport
        st.markdown("---")
        section_header("Répartition des percées par discipline")

        by_sport = (
            bo.groupby("Sport")
            .agg(count=("Name", "count"), total_score=("score", "sum"))
            .reset_index()
            .sort_values("count", ascending=False)
            .head(20)
        )

        fig_sport_bo = px.bar(
            by_sport,
            x="count", y="Sport",
            orientation="h",
            color="count",
            color_continuous_scale="Oranges",
            text="count",
            title="Nombre d'athlètes en percée par discipline (2020+)",
        )
        fig_sport_bo.update_traces(textposition="outside")
        fig_sport_bo.update_layout(
            **PLOTLY_THEME, height=420,
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            title_font_size=13,
        )
        st_plotly(fig_sport_bo)

        insight(
            "Ces athlètes n'avaient <strong>aucune médaille olympique avant 2020</strong>. "
            "Leur irruption sur la scène olympique en fait les favoris à surveiller pour 2028, "
            "notamment ceux qui combinent youth et régularité sur deux éditions."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — RENOUVELLEMENT PAR SPORT
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        section_header("🔄 Taux de renouvellement des dominants par discipline")
        st.markdown(
            "Compare les **top 10 athlètes médaillés** par sport entre 2008–2016 et 2020–2024. "
            "Un taux élevé = les anciens champions ont cédé la place à de nouveaux visages."
        )

        gs = _shift(df)

        k1, k2 = st.columns(2)
        k1.metric("Sports avec renouvellement total (100%)", int((gs["renewal_rate"] == 1.0).sum()))
        k2.metric("Sports avec continuité (< 50%)", int((gs["renewal_rate"] < 0.5).sum()))

        st.markdown("---")

        fig_gs = px.bar(
            gs.head(20),
            x="renewal_rate", y="Sport",
            orientation="h",
            color="renewal_rate",
            color_continuous_scale="RdYlGn",
            text=gs.head(20)["renewal_rate"].apply(lambda x: f"{x*100:.0f}%"),
            hover_data=["top_old_count", "top_new_count", "overlap"],
            title="Top 20 sports par taux de renouvellement des dominants",
        )
        fig_gs.update_traces(textposition="outside")
        fig_gs.update_layout(
            **PLOTLY_THEME, height=CHART_H,
            coloraxis_showscale=False,
            yaxis={"categoryorder": "total ascending"},
            xaxis=dict(tickformat=".0%", range=[0, 1.15]),
            title_font_size=13,
        )
        st_plotly(fig_gs)

        # Sports avec continuité — champions qui durent
        st.markdown("---")
        section_header("Champions de longévité — sports à faible renouvellement")

        low_renewal = gs[gs["renewal_rate"] < 0.5].sort_values("renewal_rate")

        if not low_renewal.empty:
            fig_low = px.bar(
                low_renewal,
                x="renewal_rate", y="Sport",
                orientation="h",
                color="overlap",
                color_continuous_scale="Blues",
                text=low_renewal["renewal_rate"].apply(lambda x: f"{x*100:.0f}%"),
                hover_data=["overlap", "top_old_count", "top_new_count"],
                title="Sports où les anciens dominants tiennent encore le haut",
            )
            fig_low.update_traces(textposition="outside")
            fig_low.update_layout(
                **PLOTLY_THEME, height=max(300, len(low_renewal) * 28),
                yaxis={"categoryorder": "total ascending"},
                xaxis=dict(tickformat=".0%"),
                title_font_size=13,
            )
            st_plotly(fig_low)

        with st.expander("📋 Tableau complet"):
            st.dataframe(gs, width="stretch", hide_index=True)

        insight(
            "Un <strong>taux de 100%</strong> signifie que les 10 athlètes dominants en 2020–2024 "
            "sont totalement différents de ceux de 2008–2016. Ces sports sont les plus propices "
            "à l'émergence de nouvelles stars pour Los Angeles 2028."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — NOUVELLES NATIONS MÉDAILLÉES
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        section_header("🌍 Nations remportant leur 1ère médaille depuis 2016")

        nn = _new_nations(df)

        k1, k2 = st.columns(2)
        k1.metric("Nouvelles nations médaillées", len(nn))
        k2.metric("Médailles cumulées", int(nn["medals_total"].sum()))

        st.markdown("---")

        if not nn.empty:
            fig_nn = px.bar(
                nn,
                x="medals_total", y="Team",
                orientation="h",
                color="first_medal_year",
                color_continuous_scale="Teal",
                text="medals_total",
                hover_data=["NOC", "first_medal_year", "Sports"],
                title="Nations ayant décroché leur 1ère médaille en 2016 ou après",
            )
            fig_nn.update_traces(textposition="outside")
            fig_nn.update_layout(
                **PLOTLY_THEME, height=max(320, len(nn) * 30),
                yaxis={"categoryorder": "total ascending"},
                coloraxis_colorbar=dict(title="Année", thickness=12),
                title_font_size=13,
            )
            st_plotly(fig_nn)

            st.markdown("---")
            section_header("Carte des nouvelles nations médaillées")

            fig_map = px.choropleth(
                nn,
                locations="NOC",
                color="medals_total",
                hover_name="Team",
                hover_data={"first_medal_year": True, "Sports": True, "NOC": False},
                color_continuous_scale="Greens",
                labels={"medals_total": "Médailles totales", "first_medal_year": "1ère médaille"},
                title="Nouvelles nations médaillées depuis 2016",
            )
            fig_map.update_layout(
                **PLOTLY_THEME, height=460,
                geo=dict(showframe=False, showcoastlines=True,
                         coastlinecolor="#e0e0e0", bgcolor="rgba(0,0,0,0)"),
                coloraxis_colorbar=dict(title="Médailles", thickness=12),
                title_font_size=13,
            )
            st_plotly(fig_map)

            with st.expander("📋 Détail par nation"):
                st.dataframe(
                    nn[["Team", "NOC", "first_medal_year", "medals_total", "Sports"]],
                    width="stretch",
                    hide_index=True,
                )

        insight(
            "Ces nations participaient aux JO sans jamais monter sur le podium "
            "avant 2016. Leur percée récente reflète soit l'<strong>émergence d'un talent "
            "individuel</strong> (ex: Fiji en Rugby Sevens), soit un "
            "<strong>développement sportif national</strong> ciblé."
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )

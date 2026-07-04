"""Vue Multi-sources — fusion données JO (CSV) et World Bank API."""
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
from src.data.api_fetcher import enrich_medals_with_country_data, fetch_country_metadata

CHART_H = 420

MEDAL_VALUES = ["Gold", "Silver", "Bronze"]


@st.cache_data
def _get_country_meta() -> pd.DataFrame:
    return fetch_country_metadata()


@st.cache_data
def _get_enriched(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    agg = (
        medals.groupby(["NOC", "Team"])
        .size()
        .reset_index(name="medals")
    )
    meta = fetch_country_metadata()
    return enrich_medals_with_country_data(agg, meta)


@st.cache_data
def _get_enriched_by_year(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    agg = (
        medals.groupby(["NOC", "Team", "Year"])
        .size()
        .reset_index(name="medals")
    )
    meta = fetch_country_metadata()
    keep = [c for c in ["NOC", "country_name", "population", "region",
                         "income_level", "gdp_per_capita"] if c in meta.columns]
    return agg.merge(meta[keep], on="NOC", how="left")


def show(df: pd.DataFrame) -> None:
    st.title("🌐 Analyse multi-sources")
    st.markdown(
        "Les données des JO (source **Kaggle/CSV**) sont enrichies avec les "
        "métadonnées pays de la **World Bank API** (population, PIB, région). "
        "Cette fusion permet des analyses inédites comme les médailles par habitant."
    )

    # ── Source banner ─────────────────────────────────────────────────────
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(
            """
            <div style="border:1px solid #1E88E5;border-radius:8px;padding:12px 16px;margin-bottom:8px;">
            <div style="font-size:0.8rem;opacity:0.7;">Source 1 — Données JO</div>
            <div style="font-weight:700;">CSV Kaggle · 120K lignes</div>
            <div style="font-size:0.78rem;opacity:0.65;">Participations, médailles, sports, 1896–2024</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_s2:
        st.markdown(
            """
            <div style="border:1px solid #43A047;border-radius:8px;padding:12px 16px;margin-bottom:8px;">
            <div style="font-size:0.8rem;opacity:0.7;">Source 2 — World Bank API</div>
            <div style="font-weight:700;">API REST · 250+ pays</div>
            <div style="font-size:0.78rem;opacity:0.65;">Population, PIB/hab., région, niveau de revenu</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Load data ─────────────────────────────────────────────────────────
    with st.spinner("Chargement des données World Bank…"):
        enriched = _get_enriched(df)
        meta = _get_country_meta()

    matched = enriched["population"].notna().sum()
    total = len(enriched)

    k1, k2, k3 = st.columns(3)
    k1.metric("Pays dans le CSV", total)
    k2.metric("Avec données World Bank", matched)
    k3.metric("Taux de couverture", f"{matched/total*100:.0f}%")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "🏅 Médailles par habitant",
        "🌍 Analyse par région",
        "💰 Médailles vs PIB",
        "📊 Données brutes fusionnées",
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — MÉDAILLES PAR MILLION D'HABITANTS
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        section_header("🏅 Efficacité olympique — médailles par million d'habitants")

        per_cap = (
            enriched.dropna(subset=["medals_per_million", "population"])
            .query("population > 500_000")
            .sort_values("medals_per_million", ascending=False)
        )

        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            top_n = st.slider("Top N pays", 10, 30, 20, key="pc_topn")
            min_medals = st.slider("Médailles minimum", 1, 50, 10, key="pc_minmed")

        filt = per_cap[per_cap["medals"] >= min_medals].head(top_n)

        with col_f2:
            if not filt.empty:
                fig = px.bar(
                    filt,
                    x="medals_per_million", y="Team",
                    orientation="h",
                    color="medals_per_million",
                    color_continuous_scale="YlOrRd",
                    hover_data={"medals": True, "population": True,
                                "medals_per_million": ":.3f", "Team": False},
                    text=filt["medals_per_million"].apply(lambda x: f"{x:.2f}"),
                    title=f"Top {top_n} pays — médailles pour 1 million d'habitants (total historique)",
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    **PLOTLY_THEME, height=CHART_H,
                    coloraxis_showscale=False,
                    yaxis={"categoryorder": "total ascending"},
                    title_font_size=13,
                )
                st_plotly(fig)

        # Scatter population vs medals
        st.markdown("---")
        section_header("Volume médailles vs population (toutes éditions confondues)")

        scatter_df = enriched.dropna(subset=["population", "region"]).query("medals > 0")
        fig_sc = px.scatter(
            scatter_df,
            x="population", y="medals",
            color="region",
            size="medals",
            hover_name="Team",
            hover_data={"medals_per_million": ":.3f", "population": True},
            log_x=True,
            title="Population (log) vs médailles — par région",
        )
        fig_sc.update_layout(
            **PLOTLY_THEME, height=420,
            xaxis_title="Population (log)",
            yaxis_title="Médailles totales",
            title_font_size=13,
        )
        st_plotly(fig_sc)

        insight(
            "La <strong>médaille par habitant</strong> corrige le biais de taille. "
            "Des petits pays comme la Finlande ou la Jamaïque se distinguent "
            "bien plus qu'avec le classement brut des médailles."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — ANALYSE PAR RÉGION
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        section_header("🌍 Répartition des médailles par région (World Bank)")

        region_df = (
            enriched.dropna(subset=["region"])
            .groupby("region")
            .agg(
                medals=("medals", "sum"),
                nb_countries=("NOC", "count"),
                total_pop=("population", "sum"),
            )
            .reset_index()
            .sort_values("medals", ascending=False)
        )
        region_df["medals_per_million"] = (
            region_df["medals"] / region_df["total_pop"] * 1_000_000
        ).round(3)

        col_r1, col_r2 = st.columns(2)

        with col_r1:
            fig_reg = px.pie(
                region_df,
                names="region",
                values="medals",
                title="Part des médailles par région (toutes éditions)",
                hole=0.35,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            fig_reg.update_traces(textposition="inside", textinfo="percent+label")
            fig_reg.update_layout(**PLOTLY_THEME, height=360, title_font_size=13)
            st_plotly(fig_reg)

        with col_r2:
            fig_reg2 = px.bar(
                region_df.sort_values("medals_per_million", ascending=True),
                x="medals_per_million", y="region",
                orientation="h",
                color="medals_per_million",
                color_continuous_scale="Teal",
                text=region_df.sort_values("medals_per_million")["medals_per_million"].apply(
                    lambda x: f"{x:.2f}"
                ),
                title="Médailles par million d'habitants — par région",
            )
            fig_reg2.update_traces(textposition="outside")
            fig_reg2.update_layout(
                **PLOTLY_THEME, height=360,
                coloraxis_showscale=False,
                title_font_size=13,
            )
            st_plotly(fig_reg2)

        # Évolution régionale dans le temps
        st.markdown("---")
        section_header("Évolution du poids régional par édition (depuis 1992)")

        enriched_yr = _get_enriched_by_year(df)
        trend_df = (
            enriched_yr.dropna(subset=["region"])
            .query("Year >= 1992")
            .groupby(["Year", "region"])["medals"].sum()
            .reset_index()
        )
        total_by_year = trend_df.groupby("Year")["medals"].transform("sum")
        trend_df["share_pct"] = (trend_df["medals"] / total_by_year * 100).round(1)

        fig_trend = px.area(
            trend_df, x="Year", y="share_pct", color="region",
            title="Part de chaque région dans le total des médailles (1992–2024)",
            labels={"share_pct": "Part (%)", "Year": "Édition"},
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_trend.update_layout(
            **PLOTLY_THEME, height=400,
            yaxis_title="Part (%)",
            legend=dict(orientation="h", y=-0.2),
            title_font_size=13,
        )
        st_plotly(fig_trend)

        insight(
            "La progression de l'Asie de l'Est est nette depuis 1992, "
            "en partie grâce aux JO de <strong>Pékin 2008</strong>. "
            "L'Europe reste la région historiquement dominante mais son "
            "poids relatif décline progressivement."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — MÉDAILLES VS PIB PAR HABITANT
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        section_header("💰 Richesse vs performance olympique")

        gdp_df = enriched.dropna(subset=["gdp_per_capita", "region"]).query("medals > 0")

        fig_gdp = px.scatter(
            gdp_df,
            x="gdp_per_capita",
            y="medals_per_million",
            color="region",
            size="medals",
            hover_name="Team",
            hover_data={"gdp_per_capita": ":,.0f", "medals_per_million": ":.3f",
                        "medals": True, "population": True},
            log_x=True,
            trendline="ols",
            trendline_scope="overall",
            title="PIB/hab. vs médailles/million d'hab. — corrélation richesse–performance",
        )
        fig_gdp.update_layout(
            **PLOTLY_THEME, height=480,
            xaxis_title="PIB par habitant (USD, log)",
            yaxis_title="Médailles pour 1 million d'habitants",
            legend=dict(orientation="h", y=-0.2),
            title_font_size=13,
        )
        st_plotly(fig_gdp)

        # Top performers relatifs au PIB — sur-performers
        st.markdown("---")
        section_header("Sur-performers — pays qui dépassent leur niveau économique")

        gdp_df2 = gdp_df.copy()
        # Percentile rank PIB vs medals_per_million
        gdp_df2["gdp_rank_pct"] = gdp_df2["gdp_per_capita"].rank(pct=True)
        gdp_df2["med_rank_pct"] = gdp_df2["medals_per_million"].rank(pct=True)
        gdp_df2["overperformance"] = (gdp_df2["med_rank_pct"] - gdp_df2["gdp_rank_pct"]).round(3)

        over = gdp_df2.sort_values("overperformance", ascending=False).head(15)
        under = gdp_df2.sort_values("overperformance", ascending=True).head(10)

        col_o1, col_o2 = st.columns(2)

        with col_o1:
            fig_over = px.bar(
                over, x="overperformance", y="Team",
                orientation="h",
                color="overperformance",
                color_continuous_scale="Greens",
                text=over["overperformance"].apply(lambda x: f"+{x:.2f}"),
                title="Pays médaillés au-delà de leur richesse",
                hover_data=["gdp_per_capita", "medals_per_million", "region"],
            )
            fig_over.update_traces(textposition="outside")
            fig_over.update_layout(
                **PLOTLY_THEME, height=400,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=12,
            )
            st_plotly(fig_over)

        with col_o2:
            fig_under = px.bar(
                under, x="overperformance", y="Team",
                orientation="h",
                color="overperformance",
                color_continuous_scale="Reds_r",
                text=under["overperformance"].apply(lambda x: f"{x:.2f}"),
                title="Pays riches sous-performant",
                hover_data=["gdp_per_capita", "medals_per_million", "region"],
            )
            fig_under.update_traces(textposition="outside")
            fig_under.update_layout(
                **PLOTLY_THEME, height=400,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=12,
            )
            st_plotly(fig_under)

        insight(
            "Le <strong>score de sur-performance</strong> compare le rang médailles/million "
            "au rang PIB/hab. Un score positif élevé = nation olympiquement efficace "
            "malgré un niveau de vie modeste. Score négatif = richesse non convertie en médailles."
        )
        warning_insight(
            "La corrélation PIB–médailles est réelle mais imparfaite. Des facteurs culturels, "
            "la tradition sportive nationale et les disciplines pratiquées jouent un rôle crucial."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — DONNÉES BRUTES FUSIONNÉES
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        section_header("📊 Données fusionnées CSV × World Bank")

        st.caption(
            "Ce tableau résulte de la jointure entre le dataset JO (Kaggle) "
            "et les métadonnées pays de la World Bank API."
        )

        display_cols = [c for c in [
            "NOC", "Team", "medals", "medals_per_million",
            "population", "gdp_per_capita", "region", "income_level",
        ] if c in enriched.columns]

        sort_col = st.selectbox(
            "Trier par",
            ["medals", "medals_per_million", "population", "gdp_per_capita"],
            key="ms_sort",
        )

        display_df = enriched[display_cols].dropna(subset=["region"]).sort_values(
            sort_col, ascending=False
        ).reset_index(drop=True)
        display_df.index += 1

        st.dataframe(display_df, width="stretch", height=500)

        st.download_button(
            label="Télécharger (CSV)",
            data=display_df.to_csv(index=True).encode("utf-8"),
            file_name="jo_world_bank_enriched.csv",
            mime="text/csv",
        )

        insight(
            "Données téléchargeables pour analyses complémentaires. "
            "La colonne <code>medals_per_million</code> est calculée en divisant le total "
            "historique de médailles (toutes éditions) par la population 2024."
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )

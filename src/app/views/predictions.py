import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.models.predictor import get_active_nocs
from src.models.ratings import (
    compute_sport_dominance,
    compute_athlete_ratings,
    generate_recommendations,
)
from src.app.components.cards import (
    section_header, insight, warning_insight, prediction_card,
    MEDAL_COLORS, PLOTLY_THEME,
)

CHART_H = 420

# ── Cached computations ───────────────────────────────────────────────────


@st.cache_data
def _get_sport_dominance(df: pd.DataFrame) -> pd.DataFrame:
    return compute_sport_dominance(df)


@st.cache_data
def _get_athlete_ratings(df: pd.DataFrame) -> pd.DataFrame:
    return compute_athlete_ratings(df)


@st.cache_data
def _get_recommendations(df: pd.DataFrame) -> dict:
    return generate_recommendations(df)


# ── Helpers ───────────────────────────────────────────────────────────────


def _build_models():
    return {
        "📐 Régression Linéaire": LinearRegression(),
        "📉 Ridge (régularisé)": Ridge(alpha=1.0),
        "🌳 Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "🔁 Polynomiale (deg 2)": Pipeline([
            ("poly", PolynomialFeatures(degree=2, include_bias=False)),
            ("lin", LinearRegression()),
        ]),
    }


def _predict_all_models(df: pd.DataFrame, top_n: int, model_name: str):
    """Entraîne le modèle sélectionné et prédit les médailles pour 2028."""
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()
    medal_counts = (
        medals.groupby(["NOC", "Team", "Year"])
        .size()
        .reset_index(name="Total")
    )
    models = _build_models()
    model = models[model_name]
    active = get_active_nocs(df)

    predictions = []
    for noc, group in medal_counts.groupby("NOC"):
        if noc not in active:
            continue
        group = group.sort_values("Year")
        if len(group) < 3:
            continue
        X = group[["Year"]].values
        y = group["Total"].values
        try:
            model.fit(X, y)
            pred = float(model.predict([[2028]])[0])
            mae = mean_absolute_error(y, model.predict(X))
            team = group["Team"].iloc[-1]
            predictions.append({
                "NOC": noc, "Pays": team,
                "Médailles prédites 2028": max(0, round(pred)),
                "MAE historique": round(mae, 1),
            })
        except Exception:
            continue

    pred_df = (
        pd.DataFrame(predictions)
        .sort_values("Médailles prédites 2028", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    pred_df.index = pred_df.index + 1
    return pred_df


def _country_trend_with_ci(df: pd.DataFrame, team_name: str):
    """Retourne historique + prédiction 2028 + IC 95%."""
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    hist = (
        medals[medals["Team"] == team_name]
        .groupby("Year").size().reset_index(name="Total").sort_values("Year")
    )
    if len(hist) < 3:
        return hist, None, None, None

    X = hist[["Year"]].values
    y = hist["Total"].values
    model = LinearRegression()
    model.fit(X, y)
    pred = max(0.0, float(model.predict([[2028]])[0]))

    residuals = y - model.predict(X)
    std = float(np.std(residuals))
    ci_low = max(0.0, pred - 1.96 * std)
    ci_high = pred + 1.96 * std

    return hist, round(pred), round(ci_low), round(ci_high)


# ── Vue principale ────────────────────────────────────────────────────────


def show(df: pd.DataFrame):
    st.title("🔮 Prédictions JO 2028 — Los Angeles")
    st.markdown(
        "Plusieurs algorithmes de Machine Learning entraînés sur l'**historique "
        "complet des médailles par pays** pour forecaster les résultats 2028. "
        "Comparez les modèles, explorez les côtes par discipline, et lisez les "
        "recommandations pour Los Angeles."
    )

    # ── Config panneau ────────────────────────────────────────────────────
    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        models_dict = _build_models()
        sel_model = st.selectbox("🤖 Algorithme", list(models_dict.keys()))
    with col_cfg2:
        top_n = st.slider("Nombre de pays", 5, 30, 20, key="pred_top_n")

    run = st.button("🚀 Calculer les prédictions", type="primary", use_container_width=True)

    if run:
        with st.spinner("Modèle en cours d'entraînement…"):
            st.session_state["pred_df"] = _predict_all_models(df, top_n, sel_model)
            st.session_state["pred_model"] = sel_model

    pred_df = st.session_state.get("pred_df")
    model_used = st.session_state.get("pred_model", sel_model)

    if pred_df is not None:
        st.success(f"✅ {len(pred_df)} pays prédits avec **{model_used}**")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏆 Classement 2028",
        "📈 Historique pays",
        "⚔️ Comparaison modèles",
        "🌍 Carte prédite",
        "🎯 Côtes & Disciplines",
        "💡 Recommandations",
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — CLASSEMENT
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        if pred_df is None:
            st.info("Cliquez sur **Calculer les prédictions** pour afficher le classement.")
        else:
            section_header(f"🏆 Classement prédit pour Los Angeles 2028 — {model_used}")

            fig = px.bar(
                pred_df, x="Médailles prédites 2028", y="Pays",
                orientation="h",
                color="Médailles prédites 2028",
                color_continuous_scale="RdYlGn",
                text="Médailles prédites 2028",
                labels={"Médailles prédites 2028": "Médailles"},
                title=f"Prédictions JO 2028 — Top {len(pred_df)} pays",
            )
            fig.update_traces(textposition="outside", marker_line_width=0)
            fig.update_layout(
                **PLOTLY_THEME, height=600,
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False,
                title_font_size=13,
            )
            st.plotly_chart(fig, use_container_width=True)

            podium_cols = st.columns(3)
            podium = pred_df.head(3)
            podium_labels = ["🥇", "🥈", "🥉"]
            for i, (col, (_, row)) in enumerate(zip(podium_cols, podium.iterrows())):
                with col:
                    prediction_card(row["Pays"], int(row["Médailles prédites 2028"]), podium_labels[i])

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("📋 Tableau complet des prédictions"):
                st.dataframe(pred_df, use_container_width=True)

            insight(
                f"Le modèle <strong>{model_used}</strong> prédit "
                f"<strong>{pred_df.iloc[0]['Pays']}</strong> en tête avec "
                f"<strong>{int(pred_df.iloc[0]['Médailles prédites 2028'])}</strong> médailles estimées."
            )

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — HISTORIQUE + PROJECTION PAYS
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        if pred_df is None:
            st.info("Cliquez sur **Calculer les prédictions** pour accéder à l'historique par pays.")
        else:
            section_header("📈 Historique & projection pour un pays")

            sel_country = st.selectbox(
                "Choisir un pays", pred_df["Pays"].tolist(), key="pred_country"
            )
            hist, pred_2028, ci_low, ci_high = _country_trend_with_ci(df, sel_country)

            if hist is not None and pred_2028 is not None:
                fig2 = go.Figure()

                last_year = int(hist["Year"].iloc[-1])
                last_val = int(hist["Total"].iloc[-1])
                fig2.add_trace(go.Scatter(
                    x=[last_year, 2028, 2028, last_year],
                    y=[last_val, ci_high, ci_low, last_val],
                    fill="toself",
                    fillcolor="rgba(229,57,53,0.12)",
                    line=dict(color="rgba(0,0,0,0)"),
                    name="IC 95%",
                    showlegend=True,
                ))
                fig2.add_trace(go.Scatter(
                    x=hist["Year"], y=hist["Total"],
                    mode="lines+markers",
                    name="Historique",
                    line=dict(color="#1E88E5", width=2.5),
                    marker=dict(size=7),
                ))
                fig2.add_trace(go.Scatter(
                    x=[last_year, 2028],
                    y=[last_val, pred_2028],
                    mode="lines+markers",
                    name="Projection 2028",
                    line=dict(color="#E53935", dash="dash", width=2),
                    marker=dict(size=10, symbol="star"),
                ))
                fig2.update_layout(
                    **PLOTLY_THEME, height=CHART_H,
                    title=f"Évolution des médailles — {sel_country}",
                    xaxis_title="Année", yaxis_title="Médailles totales",
                    legend=dict(orientation="h"),
                    title_font_size=13,
                )
                st.plotly_chart(fig2, use_container_width=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Prédiction 2028", f"{pred_2028} 🏅")
                c2.metric("IC bas (95%)", str(ci_low))
                c3.metric("IC haut (95%)", str(ci_high))
            else:
                st.warning(f"Pas assez de données historiques pour {sel_country}.")

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — COMPARAISON MODÈLES
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        if pred_df is None:
            st.info("Cliquez sur **Calculer les prédictions** pour comparer les modèles.")
        else:
            section_header("⚔️ Comparaison de tous les modèles sur un pays")

            sel_cmp = st.selectbox(
                "Pays à évaluer", pred_df["Pays"].tolist(), key="cmp_country"
            )

            medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
            hist_cmp = (
                medals[medals["Team"] == sel_cmp]
                .groupby("Year").size().reset_index(name="Total").sort_values("Year")
            )

            if len(hist_cmp) >= 3:
                X = hist_cmp[["Year"]].values
                y = hist_cmp["Total"].values
                models_dict_all = _build_models()

                results = []
                fig_cmp = go.Figure()
                fig_cmp.add_trace(go.Scatter(
                    x=hist_cmp["Year"], y=hist_cmp["Total"],
                    mode="lines+markers", name="Historique",
                    line=dict(color="#37474f", width=3),
                ))
                colors_cmp = ["#E53935", "#1E88E5", "#43A047", "#FB8C00"]
                last_y = int(hist_cmp["Year"].iloc[-1])
                last_v = int(hist_cmp["Total"].iloc[-1])
                for (name_m, m), col_m in zip(models_dict_all.items(), colors_cmp):
                    try:
                        m.fit(X, y)
                        pred_v = max(0.0, float(m.predict([[2028]])[0]))
                        mae = mean_absolute_error(y, m.predict(X))
                        r2 = r2_score(y, m.predict(X))
                        results.append({
                            "Modèle": name_m,
                            "Prédiction 2028": round(pred_v),
                            "MAE": round(mae, 1),
                            "R²": round(r2, 3),
                        })
                        fig_cmp.add_trace(go.Scatter(
                            x=[last_y, 2028], y=[last_v, round(pred_v)],
                            mode="lines+markers",
                            name=name_m,
                            line=dict(color=col_m, dash="dash", width=1.8),
                            marker=dict(size=9),
                        ))
                    except Exception:
                        pass

                fig_cmp.update_layout(
                    **PLOTLY_THEME, height=CHART_H,
                    title=f"Comparaison modèles — {sel_cmp}",
                    xaxis_title="Année", yaxis_title="Médailles",
                    legend=dict(orientation="h", y=-0.15),
                    title_font_size=13,
                )
                st.plotly_chart(fig_cmp, use_container_width=True)
                st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)

                insight(
                    "Un <strong>R² proche de 1</strong> indique un bon ajustement aux données historiques. "
                    "Un <strong>MAE faible</strong> indique une erreur de prédiction réduite par édition."
                )
            else:
                st.warning(f"Pas assez d'historique pour {sel_cmp}.")

    # ════════════════════════════════════════════════════════════════════
    # TAB 4 — CARTE MONDIALE PRÉDITE
    # ════════════════════════════════════════════════════════════════════
    with tab4:
        if pred_df is None:
            st.info("Cliquez sur **Calculer les prédictions** pour afficher la carte.")
        else:
            section_header("🌍 Carte mondiale des prédictions 2028")

            noc_map = (
                df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
                .groupby("Team")["NOC"].first().to_dict()
            )
            pred_map = pred_df.copy()
            pred_map["NOC"] = pred_map["Pays"].map(noc_map)

            fig_map = px.choropleth(
                pred_map.dropna(subset=["NOC"]),
                locations="NOC",
                color="Médailles prédites 2028",
                hover_name="Pays",
                color_continuous_scale="Blues",
                labels={"Médailles prédites 2028": "Médailles prédites"},
                title="Prédiction des médailles pour Les Jeux Olympiques 2028 — Los Angeles",
            )
            fig_map.update_layout(
                **PLOTLY_THEME, height=500,
                geo=dict(showframe=False, showcoastlines=True,
                         coastlinecolor="#e0e0e0", bgcolor="rgba(0,0,0,0)"),
                coloraxis_colorbar=dict(title="Médailles", thickness=12),
                title_font_size=13,
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig_map, use_container_width=True)

            warning_insight(
                "Ces prédictions sont basées sur des tendances historiques et ne prennent pas en compte "
                "les changements de programme sportif, les nouvelles disciplines ou les imprévus géopolitiques."
            )

    # ════════════════════════════════════════════════════════════════════
    # TAB 5 — CÔTES & DISCIPLINES
    # ════════════════════════════════════════════════════════════════════
    with tab5:
        section_header("🎯 Côtes de dominance par pays et discipline (2016–2024)")

        dom_df = _get_sport_dominance(df)

        # Heatmap pays × disciplines
        top_sports = (
            dom_df.groupby("Sport")["medals_recent"].sum()
            .nlargest(15).index.tolist()
        )
        top_teams = (
            dom_df.groupby("Team")["medals_recent"].sum()
            .nlargest(10).index.tolist()
        )
        heatmap_data = (
            dom_df[dom_df["Sport"].isin(top_sports) & dom_df["Team"].isin(top_teams)]
            .pivot_table(index="Team", columns="Sport", values="dominance_pct", fill_value=0)
        )

        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale="Blues",
            aspect="auto",
            labels=dict(color="Dominance (%)"),
            title="Dominance par pays et discipline — % des médailles distribuées (2016–2024)",
        )
        fig_heat.update_layout(**PLOTLY_THEME, height=420, title_font_size=13)
        st.plotly_chart(fig_heat, use_container_width=True)

        insight(
            "Un score de <strong>40%</strong> signifie que ce pays a remporté 40% de toutes les "
            "médailles distribuées dans cette discipline depuis 2016. Plus la cellule est foncée, "
            "plus la nation domine."
        )

        st.markdown("---")

        # Filtre par discipline
        col_sp1, col_sp2 = st.columns([1, 2])
        with col_sp1:
            all_sports = sorted(dom_df["Sport"].unique())
            sel_sport = st.selectbox("Discipline", all_sports, key="cote_sport")

        sport_data = dom_df[dom_df["Sport"] == sel_sport].nlargest(10, "dominance_pct")

        with col_sp2:
            fig_sport = px.bar(
                sport_data, x="dominance_pct", y="Team",
                orientation="h",
                color="dominance_pct",
                color_continuous_scale="RdYlGn",
                text=sport_data["dominance_pct"].apply(lambda x: f"{x}%"),
                title=f"Top pays en {sel_sport} (2016–2024)",
            )
            fig_sport.update_traces(textposition="outside")
            fig_sport.update_layout(
                **PLOTLY_THEME, height=360,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=13,
            )
            st.plotly_chart(fig_sport, use_container_width=True)

        st.markdown("---")

        # Profil radar d'un pays
        section_header("Profil olympique d'un pays")

        all_teams = sorted(dom_df["Team"].unique())
        sel_country_radar = st.selectbox("Pays", all_teams, key="cote_country")
        country_sports = dom_df[dom_df["Team"] == sel_country_radar].nlargest(8, "dominance_pct")

        if not country_sports.empty and len(country_sports) >= 3:
            labels = country_sports["Sport"].tolist()
            values = country_sports["dominance_pct"].tolist()
            # Ferme le polygone
            labels_closed = labels + [labels[0]]
            values_closed = values + [values[0]]

            fig_radar = go.Figure(go.Scatterpolar(
                r=values_closed,
                theta=labels_closed,
                fill="toself",
                fillcolor="rgba(30, 136, 229, 0.25)",
                line=dict(color="#1E88E5", width=2),
                name=sel_country_radar,
            ))
            fig_radar.update_layout(
                **PLOTLY_THEME,
                polar=dict(radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2],
                )),
                height=420,
                title=f"Profil olympique — {sel_country_radar} (% dominance par discipline)",
                showlegend=False,
                title_font_size=13,
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning(f"Pas assez de disciplines avec données pour {sel_country_radar}.")

        st.markdown("---")

        # Côtes des athlètes
        section_header("🏃 Côtes des athlètes actifs (2016–2024)")

        ath_df = _get_athlete_ratings(df)

        if not ath_df.empty:
            col_a1, col_a2 = st.columns([1, 2])
            with col_a1:
                sports_list = ["Tous"] + sorted(ath_df["Sport"].unique())
                sel_ath_sport = st.selectbox("Filtrer par sport", sports_list, key="ath_sport_filter")
                min_medals = st.slider("Médailles minimum", 1, 10, 3, key="ath_min_medals")

            filtered_ath = ath_df[ath_df["nb_medals"] >= min_medals]
            if sel_ath_sport != "Tous":
                filtered_ath = filtered_ath[filtered_ath["Sport"] == sel_ath_sport]

            top_athletes = filtered_ath.head(15)

            with col_a2:
                if not top_athletes.empty:
                    fig_ath = px.bar(
                        top_athletes, x="cote", y="Name",
                        orientation="h",
                        color="cote",
                        color_continuous_scale="Oranges",
                        hover_data=["Team", "Sport", "nb_medals", "nb_editions"],
                        text="cote",
                        title="Top 15 athlètes par côte (score pondéré)",
                    )
                    fig_ath.update_traces(textposition="outside")
                    fig_ath.update_layout(
                        **PLOTLY_THEME, height=420,
                        coloraxis_showscale=False,
                        yaxis={"categoryorder": "total ascending"},
                        title_font_size=13,
                    )
                    st.plotly_chart(fig_ath, use_container_width=True)
                else:
                    st.info("Aucun athlète ne correspond aux filtres sélectionnés.")

            with st.expander("📋 Tableau complet des côtes athlètes"):
                st.dataframe(
                    filtered_ath[
                        ["Name", "Team", "Sport", "nb_medals", "nb_editions", "weighted_score", "cote"]
                    ].head(50),
                    use_container_width=True,
                    hide_index=True,
                )

            insight(
                "La <strong>côte</strong> combine le score pondéré des médailles "
                "(Or=3 pts, Argent=2 pts, Bronze=1 pt) avec la régularité aux JO "
                "(+15% par édition supplémentaire). Un score élevé indique un athlète "
                "dominant sur plusieurs cycles olympiques."
            )

    # ════════════════════════════════════════════════════════════════════
    # TAB 6 — RECOMMANDATIONS
    # ════════════════════════════════════════════════════════════════════
    with tab6:
        section_header("💡 Recommandations stratégiques pour Los Angeles 2028")

        recs = _get_recommendations(df)

        # --- Nations en progression ---
        st.subheader("Nations en forte progression")
        rising = recs["rising_nations"]

        if not rising.empty:
            fig_rising = px.bar(
                rising, x="growth_pct", y="Team",
                orientation="h",
                color="growth_pct",
                color_continuous_scale="Greens",
                text=rising["growth_pct"].apply(lambda x: f"+{x}%"),
                hover_data={"early": True, "recent": True, "growth": True, "growth_pct": False},
                title="Croissance du palmarès entre 2008–2016 et 2016–2024",
            )
            fig_rising.update_traces(textposition="outside")
            fig_rising.update_layout(
                **PLOTLY_THEME, height=360,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=13,
            )
            st.plotly_chart(fig_rising, use_container_width=True)

            insight(
                "Ces nations ont <strong>multiplié leur palmarès</strong> sur les deux derniers "
                "cycles olympiques. Leurs athlètes sont à surveiller de près pour 2028."
            )

        st.markdown("---")

        # --- Sports compétitifs vs dominés ---
        col_r1, col_r2 = st.columns(2)

        with col_r1:
            st.subheader("Sports les plus ouverts")
            comp = recs["competitive_sports"]
            if not comp.empty:
                comp_df = comp.reset_index()
                comp_df.columns = ["Sport", "HHI"]
                comp_df["Compétitivité (%)"] = ((1 - comp_df["HHI"]) * 100).round(1)
                comp_df = comp_df.sort_values("Compétitivité (%)", ascending=True)

                fig_comp = px.bar(
                    comp_df, x="Compétitivité (%)", y="Sport",
                    orientation="h",
                    color="Compétitivité (%)",
                    color_continuous_scale="Teal",
                    text=comp_df["Compétitivité (%)"].apply(lambda x: f"{x}%"),
                    title="Disciplines sans dominance claire — opportunités",
                )
                fig_comp.update_traces(textposition="outside")
                fig_comp.update_layout(
                    **PLOTLY_THEME, height=300,
                    coloraxis_showscale=False,
                    yaxis={"categoryorder": "total ascending"},
                    title_font_size=13,
                )
                st.plotly_chart(fig_comp, use_container_width=True)

                insight(
                    "Score élevé = médailles <strong>réparties entre de nombreux pays</strong>. "
                    "Ce sont les disciplines où les nations émergentes ont le plus à gagner."
                )

        with col_r2:
            st.subheader("Sports les plus dominés")
            dom_rec = recs["dominated_sports"]
            if not dom_rec.empty:
                dom_tbl = dom_rec.reset_index()
                dom_tbl.columns = ["Sport", "HHI"]
                dom_tbl["Dominance (%)"] = (dom_tbl["HHI"] * 100).round(1)
                dom_tbl = dom_tbl.sort_values("Dominance (%)", ascending=True)

                fig_dom = px.bar(
                    dom_tbl, x="Dominance (%)", y="Sport",
                    orientation="h",
                    color="Dominance (%)",
                    color_continuous_scale="Reds",
                    text=dom_tbl["Dominance (%)"].apply(lambda x: f"{x}%"),
                    title="Disciplines monopolisées — peu d'espace pour les outsiders",
                )
                fig_dom.update_traces(textposition="outside")
                fig_dom.update_layout(
                    **PLOTLY_THEME, height=300,
                    coloraxis_showscale=False,
                    yaxis={"categoryorder": "total ascending"},
                    title_font_size=13,
                )
                st.plotly_chart(fig_dom, use_container_width=True)

                warning_insight(
                    "Ces sports sont historiquement monopolisés par un ou deux pays. "
                    "Il est difficile d'y décrocher des médailles sans tradition établie."
                )

        # --- France spotlight ---
        france_sports = recs["france_top_sports"]
        if not france_sports.empty:
            st.markdown("---")
            section_header("🇫🇷 Disciplines clés pour la France")

            fr_df = france_sports.reset_index()
            fr_df.columns = ["Sport", "Médailles (2016–2024)"]

            fig_fr = px.bar(
                fr_df, x="Médailles (2016–2024)", y="Sport",
                orientation="h",
                color="Médailles (2016–2024)",
                color_continuous_scale="Blues",
                text="Médailles (2016–2024)",
                title="Sports où la France performe le mieux (2016–2024)",
            )
            fig_fr.update_traces(textposition="outside")
            fig_fr.update_layout(
                **PLOTLY_THEME, height=320,
                coloraxis_showscale=False,
                yaxis={"categoryorder": "total ascending"},
                title_font_size=13,
            )
            st.plotly_chart(fig_fr, use_container_width=True)

            insight(
                "Pour maximiser son palmarès à Los Angeles, la France devrait s'appuyer "
                "sur ses disciplines de tradition tout en visant les sports compétitifs "
                "identifiés dans la colonne de gauche."
            )

        # --- Synthèse narrative ---
        st.markdown("---")
        st.markdown(
            """
            <div class="insight-block">
            💡 <strong>Synthèse des recommandations pour Los Angeles 2028</strong><br><br>
            1. <strong>Capitaliser sur les sports compétitifs</strong> — les disciplines sans monopole
               offrent le plus d'opportunités, notamment pour les nations en progression.<br>
            2. <strong>Surveiller les nations montantes</strong> — leur croissance rapide pourrait
               redistribuer les médailles dans plusieurs disciplines clés.<br>
            3. <strong>Valoriser les athlètes multi-éditions</strong> — la régularité sur plusieurs
               cycles olympiques est le meilleur indicateur de performance future.<br>
            4. <strong>Anticiper les nouvelles disciplines</strong> — Los Angeles pourrait introduire
               des sports où la répartition des médailles reste encore indéterminée.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )

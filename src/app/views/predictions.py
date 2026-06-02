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
from src.app.components.cards import (
    section_header, insight, warning_insight, prediction_card,
    MEDAL_COLORS, PLOTLY_THEME,
)

CHART_H = 420

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

    # Ne prédire que les nations encore actives (présentes depuis 2016) :
    # sinon des pays disparus (URSS, RDA...) dominent le classement 2028.
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

    # IC bootstrappé simplifié
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
        "Comparez les modèles, explorez par pays, simulez des scénarios."
    )

    # ── Config panneau ────────────────────────────────────────────────────
    col_cfg1, col_cfg2 = st.columns([2, 1])
    with col_cfg1:
        models_dict = _build_models()
        sel_model = st.selectbox("🤖 Algorithme", list(models_dict.keys()))
    with col_cfg2:
        top_n = st.slider("Nombre de pays", 5, 30, 20, key="pred_top_n")

    # ── Bouton lancer ─────────────────────────────────────────────────────
    run = st.button("🚀 Calculer les prédictions", type="primary", width='stretch')

    if "pred_df" not in st.session_state or run:
        if run:
            with st.spinner("Modèle en cours d'entraînement…"):
                st.session_state["pred_df"] = _predict_all_models(df, top_n, sel_model)
                st.session_state["pred_model"] = sel_model
        else:
            st.info("Cliquez sur **Calculer les prédictions** pour afficher les résultats.")
            return

    pred_df = st.session_state["pred_df"]
    model_used = st.session_state.get("pred_model", sel_model)

    st.success(f"✅ {len(pred_df)} pays prédits avec **{model_used}**")

    # ── Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Classement 2028", "📈 Historique pays", "⚔️ Comparaison modèles", "🌍 Carte prédite"
    ])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — CLASSEMENT
    # ════════════════════════════════════════════════════════════════════
    with tab1:
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
        st.plotly_chart(fig, width='stretch')

        # Podium top 3
        podium_cols = st.columns(3)
        podium = pred_df.head(3)
        podium_labels = ["🥇", "🥈", "🥉"]
        for i, (col, (_, row)) in enumerate(zip(podium_cols, podium.iterrows())):
            with col:
                prediction_card(row["Pays"], int(row["Médailles prédites 2028"]), podium_labels[i])

        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋 Tableau complet des prédictions"):
            st.dataframe(pred_df, width='stretch')

        insight(
            f"Le modèle <strong>{model_used}</strong> prédit "
            f"<strong>{pred_df.iloc[0]['Pays']}</strong> en tête avec "
            f"<strong>{int(pred_df.iloc[0]['Médailles prédites 2028'])}</strong> médailles estimées."
        )

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — HISTORIQUE + PROJECTION PAYS
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        section_header("📈 Historique & projection pour un pays")

        sel_country = st.selectbox(
            "Choisir un pays", pred_df["Pays"].tolist(), key="pred_country"
        )
        hist, pred_2028, ci_low, ci_high = _country_trend_with_ci(df, sel_country)

        if hist is not None and pred_2028 is not None:
            fig2 = go.Figure()

            # Bande IC
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

            # Historique
            fig2.add_trace(go.Scatter(
                x=hist["Year"], y=hist["Total"],
                mode="lines+markers",
                name="Historique",
                line=dict(color="#1E88E5", width=2.5),
                marker=dict(size=7),
            ))

            # Projection
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
            st.plotly_chart(fig2, width='stretch')

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
            # Historique
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
                        "Modèle": name_m, "Prédiction 2028": round(pred_v),
                        "MAE": round(mae, 1), "R²": round(r2, 3),
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
            st.plotly_chart(fig_cmp, width='stretch')

            st.dataframe(pd.DataFrame(results), width='stretch', hide_index=True)

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
        section_header("🌍 Carte mondiale des prédictions 2028")

        # Enrichir pred_df avec le code NOC original
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
        st.plotly_chart(fig_map, width='stretch')

        warning_insight(
            "Ces prédictions sont basées sur des tendances historiques et ne prennent pas en compte "
            "les changements de programme sportif, les nouvelles disciplines ou les imprévus géopolitiques."
        )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )


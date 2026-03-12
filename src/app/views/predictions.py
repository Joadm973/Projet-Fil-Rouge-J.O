import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.models.predictor import predict_medals_2028, get_country_trend


def show(df):
    st.title("🔮 Prédictions JO 2028 — Los Angeles")
    st.markdown(
        """
        Modèle de **régression linéaire** entraîné sur l'historique des médailles par pays.
        Pour chaque pays, on prédit le total de médailles attendu pour les JO 2028.
        """
    )
    st.divider()

    col1, col2 = st.columns([1, 2])
    with col1:
        top_n = st.slider("Nombre de pays à afficher", 5, 30, 20)
    with col2:
        st.info(
            "📐 Algorithme : Régression Linéaire (scikit-learn) — un modèle par pays sur toutes les éditions disponibles."
        )

    if st.button("🚀 Lancer les prédictions", type="primary", width='stretch'):
        with st.spinner("Calcul en cours…"):
            pred_df = predict_medals_2028(df, top_n=top_n)

        st.success(f"✅ Prédictions calculées pour {len(pred_df)} pays !")
        st.divider()

        st.subheader(f"🏆 Top {top_n} pays prédits pour 2028")
        fig = px.bar(
            pred_df,
            x="Médailles prédites 2028",
            y="Pays",
            orientation="h",
            color="Médailles prédites 2028",
            color_continuous_scale="Reds",
            labels={"Médailles prédites 2028": "Médailles prédites"},
            text="Médailles prédites 2028",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=600, yaxis={"categoryorder": "total ascending"},
                          coloraxis_showscale=False)
        st.plotly_chart(fig, width='stretch')

        st.subheader("📋 Tableau des prédictions")
        st.dataframe(pred_df, width='stretch')

        st.divider()
        st.subheader("📈 Historique + Projection pour un pays")
        selected = st.selectbox("Choisir un pays", pred_df["Pays"].tolist())
        hist, pred_2028 = get_country_trend(df, selected)

        if hist is not None and pred_2028 is not None:
            fig2 = go.Figure()
            fig2.add_trace(
                go.Scatter(
                    x=hist["Year"],
                    y=hist["Total"],
                    mode="lines+markers",
                    name="Historique",
                    line=dict(color="#1E88E5"),
                )
            )
            last_year = int(hist["Year"].iloc[-1])
            last_val = int(hist["Total"].iloc[-1])
            fig2.add_trace(
                go.Scatter(
                    x=[last_year, 2028],
                    y=[last_val, pred_2028],
                    mode="lines+markers",
                    name="Prédiction 2028",
                    line=dict(color="#E53935", dash="dash"),
                    marker=dict(size=10),
                )
            )
            fig2.update_layout(
                title=f"Évolution des médailles — {selected}",
                xaxis_title="Année",
                yaxis_title="Médailles totales",
                height=420,
            )
            st.plotly_chart(fig2, width='stretch')
            st.metric(f"Médailles prédites pour {selected} en 2028", pred_2028)

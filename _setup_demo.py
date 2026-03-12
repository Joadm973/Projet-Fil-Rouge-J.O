"""
Script temporaire pour peupler les fichiers sources vides du projet.
Exécuter une seule fois depuis la racine du projet.
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

files = {}

# ─────────────────────────────────────────
# src/data/data_loader.py
# ─────────────────────────────────────────
files["src/data/data_loader.py"] = '''\
import pandas as pd
from pathlib import Path
import sys

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import RAW_OLYMPICS_FILE


def load_raw_data() -> pd.DataFrame:
    """Charge le dataset brut des JO depuis le fichier CSV."""
    return pd.read_csv(RAW_OLYMPICS_FILE)
'''

# ─────────────────────────────────────────
# src/data/data_cleaner.py
# ─────────────────────────────────────────
files["src/data/data_cleaner.py"] = '''\
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et prépare le dataset pour l\'analyse."""
    df = df.copy()
    # Uniquement les JO d\'été
    df = df[df["Season"] == "Summer"]
    df = df.drop_duplicates()
    # Flag médaille binaire
    df["Has_Medal"] = df["Medal"].isin(["Gold", "Silver", "Bronze"]).astype(int)
    return df.reset_index(drop=True)


def get_medals_df(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne uniquement les lignes avec une médaille."""
    return df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()
'''

# ─────────────────────────────────────────
# src/analysis/exploratory.py
# ─────────────────────────────────────────
files["src/analysis/exploratory.py"] = '''\
import pandas as pd


def medals_by_country(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return (
        medals.groupby(["Team", "NOC", "Medal"])
        .size()
        .reset_index(name="Count")
    )


def medals_by_year(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return medals.groupby(["Year", "Medal"]).size().reset_index(name="Count")


def top_athletes(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return (
        medals.groupby(["Name", "Team", "Sport"])
        .size()
        .nlargest(n)
        .reset_index(name="Médailles")
    )


def participation_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Year").agg(
        Athlètes=("Name", "nunique"),
        Pays=("NOC", "nunique"),
        Sports=("Sport", "nunique"),
    ).reset_index()
'''

# ─────────────────────────────────────────
# src/models/predictor.py
# ─────────────────────────────────────────
files["src/models/predictor.py"] = '''\
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_medals_2028(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Entraîne une régression linéaire par pays sur l\'historique des médailles
    et prédit le total pour JO 2028.
    """
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()
    medal_counts = (
        medals.groupby(["NOC", "Team", "Year"])
        .size()
        .reset_index(name="Total")
    )

    predictions = []
    for noc, group in medal_counts.groupby("NOC"):
        group = group.sort_values("Year")
        if len(group) < 2:
            continue
        X = group[["Year"]].values
        y = group["Total"].values
        model = LinearRegression()
        model.fit(X, y)
        pred = float(model.predict([[2028]])[0])
        team = group["Team"].iloc[-1]
        predictions.append(
            {
                "NOC": noc,
                "Pays": team,
                "Médailles prédites 2028": max(0, round(pred)),
            }
        )

    pred_df = (
        pd.DataFrame(predictions)
        .sort_values("Médailles prédites 2028", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    pred_df.index = pred_df.index + 1
    return pred_df


def get_country_trend(df: pd.DataFrame, team_name: str):
    """Retourne l\'historique + la prédiction 2028 pour un pays donné."""
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    hist = (
        medals[medals["Team"] == team_name]
        .groupby("Year")
        .size()
        .reset_index(name="Total")
        .sort_values("Year")
    )
    if len(hist) < 2:
        return hist, None

    X = hist[["Year"]].values
    y = hist["Total"].values
    model = LinearRegression()
    model.fit(X, y)
    pred_2028 = max(0, float(model.predict([[2028]])[0]))
    return hist, round(pred_2028)
'''

# ─────────────────────────────────────────
# src/app/pages/home.py
# ─────────────────────────────────────────
files["src/app/pages/home.py"] = '''\
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
    c2.metric("🏃 Athlètes", f"{df[\'Name\'].nunique():,}")
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
        st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig2, use_container_width=True)

    # ── Évolution participation ────────────────────────────────────────────
    st.subheader("📈 Évolution de la participation aux JO d\'été")
    part = participation_over_time(df)
    fig3 = px.line(
        part,
        x="Year",
        y=["Athlètes", "Pays", "Sports"],
        markers=True,
        labels={"value": "Nombre", "Year": "Année", "variable": ""},
    )
    fig3.update_layout(height=360)
    st.plotly_chart(fig3, use_container_width=True)
'''

# ─────────────────────────────────────────
# src/app/pages/exploration.py
# ─────────────────────────────────────────
files["src/app/pages/exploration.py"] = '''\
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
            "Fourchette d\'années",
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
    st.plotly_chart(fig, use_container_width=True)

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
        st.plotly_chart(fig2, use_container_width=True)

    # ── Évolution Or — Top 5 pays ─────────────────────────────────────────
    with col_r:
        st.subheader("📆 Évolution médailles d\'or — Top 5")
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
            labels={"Or": "Médailles d\'or", "Year": "Année"},
        )
        fig3.update_layout(height=420)
        st.plotly_chart(fig3, use_container_width=True)

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
    st.plotly_chart(fig_map, use_container_width=True)
'''

# ─────────────────────────────────────────
# src/app/pages/athletes.py
# ─────────────────────────────────────────
files["src/app/pages/athletes.py"] = '''\
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
    st.plotly_chart(fig, use_container_width=True)

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
    st.plotly_chart(fig2, use_container_width=True)

    # ── Tableau ───────────────────────────────────────────────────────────
    st.subheader("📋 Tableau des performances")
    st.dataframe(
        top.rename(columns={"Name": "Athlète", "Team": "Pays"}).reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )
'''

# ─────────────────────────────────────────
# src/app/pages/predictions.py
# ─────────────────────────────────────────
files["src/app/pages/predictions.py"] = '''\
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
        Modèle de **régression linéaire** entraîné sur l\'historique des médailles par pays.
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

    if st.button("🚀 Lancer les prédictions", type="primary", use_container_width=True):
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
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Tableau des prédictions")
        st.dataframe(pred_df, use_container_width=True)

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
            st.plotly_chart(fig2, use_container_width=True)
            st.metric(f"Médailles prédites pour {selected} en 2028", pred_2028)
'''

# ─────────────────────────────────────────
# src/app/app.py
# ─────────────────────────────────────────
files["src/app/app.py"] = '''\
import streamlit as st
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from config import APP_CONFIG
from src.data.data_loader import load_raw_data
from src.data.data_cleaner import clean_data
from src.app.pages import home, exploration, athletes, predictions

st.set_page_config(**APP_CONFIG)


@st.cache_data
def get_data():
    df = load_raw_data()
    return clean_data(df)


df = get_data()

# ── Sidebar navigation ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏅 YPerf")
    st.markdown("*Analyse des Performances Olympiques*")
    st.divider()
    page = st.radio(
        "Navigation",
        options=["🏠 Accueil", "🔍 Exploration", "🏃 Athlètes", "🔮 Prédictions 2028"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"📁 {len(df):,} lignes | {df[\'Year\'].min()}–{df[\'Year\'].max()}")
    st.caption("Ynov Bachelor 3 — Data & IA — 2026")

# ── Page routing ──────────────────────────────────────────────────────────
if page == "🏠 Accueil":
    home.show(df)
elif page == "🔍 Exploration":
    exploration.show(df)
elif page == "🏃 Athlètes":
    athletes.show(df)
elif page == "🔮 Prédictions 2028":
    predictions.show(df)
'''

# ─────────────────────────────────────────
# Write all files
# ─────────────────────────────────────────
for rel_path, content in files.items():
    abs_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ {rel_path}")

print("\n🎉 Tous les fichiers ont été générés avec succès !")

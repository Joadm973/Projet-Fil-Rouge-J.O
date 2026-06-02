import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.app.components.cards import (
    section_header, insight, MEDAL_COLORS, PLOTLY_THEME
)

CHART_H = 440


def show(df: pd.DataFrame):
    st.title("🏃 Tableau de bord Athlètes")
    st.markdown("Recherchez, comparez et explorez les profils des athlètes olympiques.")

    medals_df = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

    # ── Filtres sidebar ───────────────────────────────────────────────────
    with st.sidebar:
        st.subheader("⚙️ Filtres athlètes")
        sports_list = ["Tous"] + sorted(df["Sport"].unique().tolist())
        sel_sport = st.selectbox("Sport", sports_list, key="ath_sport")
        countries_list = ["Tous"] + sorted(df["Team"].unique().tolist())
        sel_country = st.selectbox("Pays", countries_list, key="ath_country")
        medal_filter = st.multiselect(
            "Médailles", ["Gold", "Silver", "Bronze"],
            default=["Gold", "Silver", "Bronze"], key="ath_medals",
        )
        year_range = st.slider(
            "Période", int(df["Year"].min()), int(df["Year"].max()),
            (int(df["Year"].min()), int(df["Year"].max())), key="ath_years"
        )

    # Appliquer les filtres
    filt = medals_df[medals_df["Medal"].isin(medal_filter)].copy()
    filt = filt[(filt["Year"] >= year_range[0]) & (filt["Year"] <= year_range[1])]
    if sel_sport != "Tous":
        filt = filt[filt["Sport"] == sel_sport]
    if sel_country != "Tous":
        filt = filt[filt["Team"] == sel_country]

    # ── Barre de recherche ────────────────────────────────────────────────
    search = st.text_input("🔎 Rechercher un athlète par nom", placeholder="Ex: Phelps, Bolt, Biles...")

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["🥇 Classement", "📊 Comparaison", "🔎 Fiche athlète"])

    # ════════════════════════════════════════════════════════════════════
    # TAB 1 — CLASSEMENT
    # ════════════════════════════════════════════════════════════════════
    with tab1:
        section_header("🥇 Top athlètes les plus médaillés")

        top = (
            filt.groupby(["Name", "Team", "Sport"])
            .size()
            .nlargest(25)
            .reset_index(name="Médailles")
        )

        # Filtrer par recherche si actif
        if search.strip():
            top = top[top["Name"].str.contains(search.strip(), case=False, na=False)]

        if top.empty:
            st.warning("Aucun athlète ne correspond à ces critères.")
        else:
            fig = px.bar(
                top, x="Médailles", y="Name", orientation="h",
                color="Sport",
                hover_data={"Team": True, "Sport": True},
                labels={"Name": "Athlète"},
                title=f"Top {len(top)} athlètes — {year_range[0]}–{year_range[1]}",
            )
            fig.update_layout(
                **PLOTLY_THEME, height=600,
                yaxis={"categoryorder": "total ascending"},
                legend_title_text="Sport", title_font_size=13,
            )
            st.plotly_chart(fig, width='stretch')

        # Détail or/argent/bronze pour le top 10
        section_header("📊 Détail des médailles — Top 10")
        top10_names = top["Name"].head(10).tolist()
        detail = (
            filt[filt["Name"].isin(top10_names)]
            .groupby(["Name", "Medal"])
            .size()
            .reset_index(name="Count")
        )
        if not detail.empty:
            fig2 = px.bar(
                detail, x="Name", y="Count", color="Medal",
                barmode="group",
                color_discrete_map=MEDAL_COLORS,
                labels={"Count": "Médailles", "Name": "Athlète"},
                title="Décomposition Or / Argent / Bronze",
            )
            fig2.update_layout(
                **PLOTLY_THEME, height=380, xaxis_tickangle=-30,
                legend_title_text="", title_font_size=13,
            )
            st.plotly_chart(fig2, width='stretch')

    # ════════════════════════════════════════════════════════════════════
    # TAB 2 — COMPARAISON RADAR
    # ════════════════════════════════════════════════════════════════════
    with tab2:
        section_header("📡 Radar de comparaison entre athlètes")

        eligible = (
            filt.groupby("Name").size().nlargest(50).index.tolist()
        )
        default_radar = eligible[:3] if len(eligible) >= 3 else eligible

        sel_athletes = st.multiselect(
            "Sélectionner 2 à 5 athlètes à comparer",
            eligible, default=default_radar, key="radar_athletes",
        )

        if len(sel_athletes) >= 2:
            # Préparer les données radar
            radar_data = []
            for name in sel_athletes:
                ath = filt[filt["Name"] == name]
                gold = int((ath["Medal"] == "Gold").sum())
                silver = int((ath["Medal"] == "Silver").sum())
                bronze = int((ath["Medal"] == "Bronze").sum())
                total = gold + silver + bronze
                sports_n = int(ath["Sport"].nunique())
                years_n = int(ath["Year"].nunique())
                radar_data.append({
                    "Athlète": name,
                    "Or": gold, "Argent": silver, "Bronze": bronze,
                    "Total": total, "Sports": sports_n, "Éditions": years_n,
                })

            categories = ["Or", "Argent", "Bronze", "Total", "Sports", "Éditions"]
            fig_radar = go.Figure()
            colors = px.colors.qualitative.Plotly

            for i, row in enumerate(radar_data):
                values = [row[c] for c in categories] + [row[categories[0]]]
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories + [categories[0]],
                    fill="toself",
                    fillcolor=f"rgba{tuple(list(int(colors[i % len(colors)].lstrip('#')[j:j+2], 16) for j in (0, 2, 4)) + [0.2])}",
                    line=dict(color=colors[i % len(colors)], width=2),
                    name=row["Athlète"],
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                showlegend=True,
                height=500,
                title="Radar de comparaison des performances",
                title_font_size=13,
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_radar, width='stretch')

            # Tableau comparatif
            radar_df = pd.DataFrame(radar_data).set_index("Athlète")
            st.dataframe(radar_df, width='stretch')

        else:
            st.info("Sélectionnez au moins 2 athlètes pour afficher le radar.")

        # Distribution médailles par genre
        section_header("⚤ Répartition des médailles par genre")
        gender_medals = (
            filt.groupby(["Sex", "Medal"]).size().reset_index(name="Count")
        )
        gender_medals["Sex"] = gender_medals["Sex"].map({"M": "Hommes", "F": "Femmes"})
        fig_gm = px.bar(
            gender_medals, x="Sex", y="Count", color="Medal",
            barmode="group",
            color_discrete_map=MEDAL_COLORS,
            labels={"Count": "Médailles", "Sex": "Genre"},
            title="Médailles par genre",
        )
        fig_gm.update_layout(**PLOTLY_THEME, height=360, legend_title_text="",
                              title_font_size=13)
        st.plotly_chart(fig_gm, width='stretch')

    # ════════════════════════════════════════════════════════════════════
    # TAB 3 — FICHE ATHLÈTE
    # ════════════════════════════════════════════════════════════════════
    with tab3:
        section_header("🔎 Fiche détaillée d'un athlète")

        # Sélection par nom (recherche ou liste)
        search_name = search.strip() if search.strip() else ""
        if search_name:
            candidates = df[df["Name"].str.contains(search_name, case=False, na=False)]["Name"].unique()
        else:
            candidates = filt.groupby("Name").size().nlargest(100).index.tolist()

        if len(candidates) == 0:
            st.warning("Aucun athlète trouvé. Modifiez les filtres ou la recherche.")
            st.stop()

        sel_ath = st.selectbox("Athlète", sorted(candidates), key="fiche_athlete")

        ath_all = df[df["Name"] == sel_ath]
        ath_medals = ath_all[ath_all["Medal"].isin(["Gold", "Silver", "Bronze"])]

        # KPIs de l'athlète
        gold_c = int((ath_medals["Medal"] == "Gold").sum())
        silver_c = int((ath_medals["Medal"] == "Silver").sum())
        bronze_c = int((ath_medals["Medal"] == "Bronze").sum())
        total_c = gold_c + silver_c + bronze_c

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🥇 Or", gold_c)
        c2.metric("🥈 Argent", silver_c)
        c3.metric("🥉 Bronze", bronze_c)
        c4.metric("🏅 Total", total_c)
        c5.metric("⭐ Éditions", int(ath_all["Year"].nunique()))

        st.markdown(f"**Pays :** {ath_all['Team'].iloc[0]} &nbsp;|&nbsp; **Sport(s) :** {', '.join(ath_all['Sport'].unique())}")

        # Timeline
        if len(ath_all) > 0:
            ath_timeline = (
                ath_all.groupby(["Year", "Medal"]).size().reset_index(name="Count")
            )
            ath_timeline["Medal"] = ath_timeline["Medal"].replace({"No medal": "Participation"})
            fig_tl = px.bar(
                ath_timeline, x="Year", y="Count", color="Medal",
                barmode="stack",
                color_discrete_map={**MEDAL_COLORS, "Participation": "#BDBDBD"},
                labels={"Count": "Entrées", "Year": "Année"},
                title=f"Carrière de {sel_ath} aux Jeux Olympiques",
            )
            fig_tl.update_layout(
                **PLOTLY_THEME, height=360, legend_title_text="",
                title_font_size=13,
            )
            st.plotly_chart(fig_tl, width='stretch')

        # Tableau complet de la carrière
        with st.expander("📋 Voir le détail complet de la carrière"):
            cols_show = [c for c in ["Year", "Sport", "Event", "Medal", "Team"] if c in ath_all.columns]
            st.dataframe(
                ath_all[cols_show].sort_values("Year").reset_index(drop=True),
                width='stretch',
            )

    # ── Footer ────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="footer">YPerf · Projet fil rouge Bachelor 3 · Ynov Informatique · 2026</div>',
        unsafe_allow_html=True,
    )


"""Système de notation (côtes) pour les athlètes et pays par discipline."""
import pandas as pd

MEDAL_WEIGHTS = {"Gold": 3, "Silver": 2, "Bronze": 1}
MEDAL_VALUES = ["Gold", "Silver", "Bronze"]


def compute_sport_dominance(df: pd.DataFrame, recent_start: int = 2016) -> pd.DataFrame:
    """Calcule le score de dominance (%) par pays et par sport sur les éditions récentes.

    Returns DataFrame: NOC, Team, Sport, medals_recent, sport_total, dominance_pct
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)].copy()
    recent = medals[medals["Year"] >= recent_start]

    if recent.empty:
        return pd.DataFrame(
            columns=["NOC", "Team", "Sport", "medals_recent", "sport_total", "dominance_pct"]
        )

    country_sport = (
        recent.groupby(["NOC", "Team", "Sport"])
        .size()
        .reset_index(name="medals_recent")
    )
    sport_totals = recent.groupby("Sport").size().reset_index(name="sport_total")

    merged = country_sport.merge(sport_totals, on="Sport")
    merged["dominance_pct"] = (merged["medals_recent"] / merged["sport_total"] * 100).round(1)

    return (
        merged
        .sort_values(["Sport", "dominance_pct"], ascending=[True, False])
        .reset_index(drop=True)
    )


def compute_athlete_ratings(df: pd.DataFrame, recent_start: int = 2016) -> pd.DataFrame:
    """Calcule un score composite (côte) pour chaque athlète médaillé actif.

    Côte = score_pondéré × (1 + 0.15 × nb_éditions)
    Or=3 pts, Argent=2 pts, Bronze=1 pt. Bonus par édition supplémentaire.

    Returns DataFrame: Name, Team, Sport, nb_medals, nb_editions, weighted_score, cote
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)].copy()
    medals["weight"] = medals["Medal"].map(MEDAL_WEIGHTS)

    active_names = set(df.loc[df["Year"] >= recent_start, "Name"])
    athlete_medals = medals[medals["Name"].isin(active_names)]

    if athlete_medals.empty:
        return pd.DataFrame()

    stats = (
        athlete_medals.groupby(["Name", "Team"])
        .agg(
            weighted_score=("weight", "sum"),
            nb_medals=("Medal", "count"),
            nb_editions=("Year", "nunique"),
            Sport=("Sport", lambda x: x.mode().iloc[0]),
        )
        .reset_index()
    )

    stats["cote"] = (stats["weighted_score"] * (1 + 0.15 * stats["nb_editions"])).round(2)

    return stats.sort_values("cote", ascending=False).reset_index(drop=True)


def generate_recommendations(df: pd.DataFrame) -> dict:
    """Génère des recommandations narratives pour les JO 2028.

    Returns dict:
        rising_nations   : DataFrame (Team, early, recent, growth, growth_pct)
        competitive_sports: Series   (Sport → HHI, lower = plus compétitif)
        dominated_sports : Series   (Sport → HHI, higher = plus dominé)
        france_top_sports: Series   (Sport → nb_medals)
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)].copy()

    # --- 1. Nations en progression (2008–2016 vs 2016–2024) ---
    early = medals[(medals["Year"] >= 2008) & (medals["Year"] < 2016)]
    recent = medals[medals["Year"] >= 2016]

    early_counts = early.groupby("Team").size().rename("early")
    recent_counts = recent.groupby("Team").size().rename("recent")

    combined = (
        pd.concat([early_counts, recent_counts], axis=1)
        .fillna(0)
        .reset_index()
        .rename(columns={"index": "Team"})
    )
    combined["growth"] = combined["recent"] - combined["early"]
    combined["growth_pct"] = (
        (combined["recent"] - combined["early"]) / (combined["early"] + 1) * 100
    ).round(1)

    active_teams = set(df.loc[df["Year"] >= 2016, "Team"])
    rising = (
        combined[
            combined["Team"].isin(active_teams)
            & (combined["recent"] >= 5)
            & (combined["growth"] > 0)
        ]
        .sort_values("growth_pct", ascending=False)
        .head(8)
        .reset_index(drop=True)
    )

    # --- 2. Compétitivité par sport (indice Herfindahl–Hirschman) ---
    sport_hhi: dict[str, float] = {}
    for sport, grp in recent.groupby("Sport"):
        if len(grp) < 10:
            continue
        total = len(grp)
        country_shares = grp.groupby("NOC").size() / total
        sport_hhi[sport] = round(float((country_shares**2).sum()), 3)

    hhi_series = pd.Series(sport_hhi)
    competitive_sports = hhi_series.sort_values().head(6)
    dominated_sports = hhi_series.sort_values(ascending=False).head(6)

    # --- 3. Disciplines clés pour la France ---
    france_medals = recent[recent["NOC"] == "FRA"]
    france_top_sports = (
        france_medals.groupby("Sport").size().sort_values(ascending=False).head(6)
        if not france_medals.empty
        else pd.Series(dtype=int)
    )

    return {
        "rising_nations": rising,
        "competitive_sports": competitive_sports,
        "dominated_sports": dominated_sports,
        "france_top_sports": france_top_sports,
    }

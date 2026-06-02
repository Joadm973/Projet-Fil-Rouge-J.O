"""Modèle de prédiction des médailles pour les JO 2028.

Une régression linéaire est entraînée **par pays** sur l'historique du nombre
de médailles par édition, puis extrapolée à 2028.

⚠️ Seules les nations encore actives (présentes à au moins une édition depuis
``RECENT_YEARS_THRESHOLD``) sont prédites : sans ce filtre, des pays disparus
comme l'URSS ou la RDA — dont la série historique est longue et croissante —
remontent en tête d'un classement 2028, ce qui n'a aucun sens.
"""
import pandas as pd
from sklearn.linear_model import LinearRegression

# Édition de référence : un pays est considéré « actif » s'il a participé
# à au moins une édition depuis cette année.
RECENT_YEARS_THRESHOLD = 2016
TARGET_YEAR = 2028
MEDAL_VALUES = ["Gold", "Silver", "Bronze"]


def get_active_nocs(df: pd.DataFrame, since: int = RECENT_YEARS_THRESHOLD) -> set:
    """Retourne l'ensemble des NOC ayant participé depuis l'année `since`.

    Sert à exclure les nations disparues (URSS, RDA, Tchécoslovaquie...) des
    projections 2028.
    """
    return set(df.loc[df["Year"] >= since, "NOC"].unique())


def _medal_counts_by_noc(df: pd.DataFrame) -> pd.DataFrame:
    """Nombre de médailles par pays et par édition."""
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    return (
        medals.groupby(["NOC", "Team", "Year"])
        .size()
        .reset_index(name="Total")
    )


def predict_medals_2028(
    df: pd.DataFrame, top_n: int = 20, only_active: bool = True
) -> pd.DataFrame:
    """Entraîne une régression linéaire par pays et prédit le total 2028.

    Args:
        df: dataset nettoyé.
        top_n: nombre de pays à conserver dans le classement.
        only_active: si True, ne prédit que les nations actives depuis 2016.
    """
    medal_counts = _medal_counts_by_noc(df)
    active = get_active_nocs(df) if only_active else set(medal_counts["NOC"])

    predictions = []
    for noc, group in medal_counts.groupby("NOC"):
        if noc not in active:
            continue
        group = group.sort_values("Year")
        if len(group) < 2:
            continue
        X = group[["Year"]].values
        y = group["Total"].values
        model = LinearRegression()
        model.fit(X, y)
        pred = float(model.predict([[TARGET_YEAR]])[0])
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
    """Retourne l'historique + la prédiction 2028 pour un pays donné."""
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
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
    pred_2028 = max(0, float(model.predict([[TARGET_YEAR]])[0]))
    return hist, round(pred_2028)

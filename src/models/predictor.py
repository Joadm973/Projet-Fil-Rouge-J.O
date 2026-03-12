import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def predict_medals_2028(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    Entraîne une régression linéaire par pays sur l'historique des médailles
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
    """Retourne l'historique + la prédiction 2028 pour un pays donné."""
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

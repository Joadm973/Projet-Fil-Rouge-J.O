"""Évaluation et comparaison de modèles de régression pour la prédiction des médailles.

Fournit les métriques (MAE, RMSE, R²), une comparaison multi-modèles sur
l'historique d'un pays et une validation croisée temporelle.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit

MEDAL_VALUES = ["Gold", "Silver", "Bronze"]
TARGET_YEAR = 2028


def regression_metrics(y_true, y_pred) -> dict:
    """Calcule MAE, RMSE et R² entre valeurs réelles et prédites."""
    return {
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": float(r2_score(y_true, y_pred)),
    }


def _country_history(df: pd.DataFrame, team_name: str) -> pd.DataFrame:
    """Série temporelle (Year, Total médailles) pour un pays."""
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    return (
        medals[medals["Team"] == team_name]
        .groupby("Year")
        .size()
        .reset_index(name="Total")
        .sort_values("Year")
    )


def evaluate_models_on_country(
    df: pd.DataFrame, team_name: str, models: dict
) -> pd.DataFrame:
    """Entraîne plusieurs modèles sur l'historique d'un pays et compare leurs métriques.

    Args:
        models: dict {nom: estimateur sklearn}.

    Returns:
        DataFrame trié par R² décroissant avec MAE, RMSE, R² et la prédiction 2028.
    """
    hist = _country_history(df, team_name)
    if len(hist) < 3:
        return pd.DataFrame()

    X = hist[["Year"]].values
    y = hist["Total"].values

    rows = []
    for name, model in models.items():
        model.fit(X, y)
        metrics = regression_metrics(y, model.predict(X))
        metrics["Modèle"] = name
        metrics["Prédiction 2028"] = max(0, round(float(model.predict([[TARGET_YEAR]])[0])))
        rows.append(metrics)

    return (
        pd.DataFrame(rows)[["Modèle", "MAE", "RMSE", "R2", "Prédiction 2028"]]
        .sort_values("R2", ascending=False)
        .reset_index(drop=True)
    )


def cross_val_mae(X, y, model, n_splits: int = 3) -> float:
    """MAE moyen en validation croisée temporelle (TimeSeriesSplit).

    Retourne NaN si la série est trop courte pour le nombre de splits demandé.
    """
    if len(y) <= n_splits:
        return float("nan")
    tscv = TimeSeriesSplit(n_splits=n_splits)
    maes = []
    for train_idx, test_idx in tscv.split(X):
        model.fit(X[train_idx], y[train_idx])
        maes.append(mean_absolute_error(y[test_idx], model.predict(X[test_idx])))
    return float(np.mean(maes))

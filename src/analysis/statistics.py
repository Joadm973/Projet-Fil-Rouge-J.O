"""Indicateurs statistiques descriptifs et inférentiels sur les données JO.

Ce module regroupe les outils « Maths pour la DataScience » du projet :
audit qualité, statistiques univariées, score pondéré, concentration (Gini)
et tests inférentiels (χ², corrélation de Pearson).
"""
import numpy as np
import pandas as pd
from scipy import stats

MEDAL_VALUES = ["Gold", "Silver", "Bronze"]
MEDAL_WEIGHTS = {"Gold": 3, "Silver": 2, "Bronze": 1}


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """Audit qualité : type, nb et % de valeurs manquantes, valeurs uniques par colonne."""
    return pd.DataFrame(
        {
            "dtype": df.dtypes.astype(str),
            "n_missing": df.isna().sum(),
            "pct_missing": (df.isna().mean() * 100).round(2),
            "n_unique": df.nunique(),
        }
    )


def descriptive_stats(df: pd.DataFrame, column: str) -> dict:
    """Statistiques descriptives univariées d'une colonne numérique."""
    serie = pd.to_numeric(df[column], errors="coerce").dropna()
    return {
        "count": int(serie.count()),
        "mean": float(serie.mean()),
        "median": float(serie.median()),
        "std": float(serie.std()),
        "min": float(serie.min()),
        "max": float(serie.max()),
        "skewness": float(serie.skew()),
        "kurtosis": float(serie.kurt()),
    }


def weighted_medal_score(df: pd.DataFrame) -> pd.DataFrame:
    """Score pondéré par pays (Or=3, Argent=2, Bronze=1), trié décroissant."""
    medals = df[df["Medal"].isin(MEDAL_VALUES)].copy()
    medals["points"] = medals["Medal"].map(MEDAL_WEIGHTS)
    return (
        medals.groupby(["NOC", "Team"])["points"]
        .sum()
        .reset_index(name="Score")
        .sort_values("Score", ascending=False)
        .reset_index(drop=True)
    )


def medal_concentration_gini(df: pd.DataFrame) -> float:
    """Indice de Gini de la concentration des médailles entre pays.

    0 = répartition parfaitement égalitaire, 1 = monopole d'un seul pays.
    """
    counts = df[df["Medal"].isin(MEDAL_VALUES)].groupby("NOC").size().values
    if len(counts) == 0:
        return float("nan")
    values = np.sort(counts.astype(float))
    n = len(values)
    cum = np.cumsum(values)
    return float(
        (2 * np.sum(np.arange(1, n + 1) * values) - (n + 1) * cum[-1]) / (n * cum[-1])
    )


def chi2_sex_medal(df: pd.DataFrame) -> dict:
    """Test du χ² d'indépendance entre le genre et le fait de remporter une médaille.

    H0 : la probabilité de médaille est indépendante du genre.
    """
    table = pd.crosstab(df["Sex"], df["Medal"].isin(MEDAL_VALUES))
    chi2, p_value, dof, _ = stats.chi2_contingency(table)
    return {
        "chi2": float(chi2),
        "p_value": float(p_value),
        "dof": int(dof),
        "significant_5pct": bool(p_value < 0.05),
        "table": table,
    }


def corr_participation_medals(df: pd.DataFrame) -> dict:
    """Corrélation de Pearson entre nombre d'athlètes envoyés et médailles gagnées.

    Calculée au niveau (pays, édition). Quantifie l'« effet de masse ».
    """
    grp = (
        df.groupby(["NOC", "Year"])
        .agg(
            athletes=("Name", "nunique"),
            medals=("Medal", lambda s: s.isin(MEDAL_VALUES).sum()),
        )
        .reset_index()
    )
    r_value, p_value = stats.pearsonr(grp["athletes"], grp["medals"])
    return {
        "pearson_r": float(r_value),
        "p_value": float(p_value),
        "n_observations": int(len(grp)),
    }


def gender_parity_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Part des athlètes femmes (en %) par édition."""
    parity = df.groupby(["Year", "Sex"])["Name"].nunique().unstack(fill_value=0)
    total = parity.sum(axis=1).replace(0, np.nan)
    parity["pct_femmes"] = (parity.get("F", 0) / total * 100).round(1)
    return parity.reset_index()

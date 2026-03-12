import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et prépare le dataset pour l'analyse."""
    df = df.copy()
    # Uniquement les JO d'été
    df = df[df["Season"] == "Summer"]
    df = df.drop_duplicates()
    # Flag médaille binaire
    df["Has_Medal"] = df["Medal"].isin(["Gold", "Silver", "Bronze"]).astype(int)
    return df.reset_index(drop=True)


def get_medals_df(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne uniquement les lignes avec une médaille."""
    return df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

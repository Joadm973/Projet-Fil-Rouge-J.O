"""Module de nettoyage et de préparation des données pour l'analyse."""
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et prépare le dataset pour l'analyse."""
    df = df.copy()
    # Uniquement les JO d'été
    df = df[df["Season"] == "Summer"]
    df = df.drop_duplicates()
    # Fusionner Allemagne de l'Est (GDR) et de l'Ouest (FRG) avec l'Allemagne unifiée (GER)
    germany_nocs = {"GDR", "FRG"}
    df.loc[df["NOC"].isin(germany_nocs), "NOC"] = "GER"
    df.loc[
        df["NOC"] == "GER",
        "Team",
    ] = df.loc[df["NOC"] == "GER", "Team"].str.replace(
        r"^(East|West)\s+Germany", "Germany", regex=True
    )
    # Flag médaille binaire
    df["Has_Medal"] = df["Medal"].isin(["Gold", "Silver", "Bronze"]).astype(int)
    return df.reset_index(drop=True)


def get_medals_df(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne uniquement les lignes avec une médaille."""
    return df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

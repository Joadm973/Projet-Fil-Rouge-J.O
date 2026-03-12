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
    df.loc[df["NOC"] == "GER", "Team"] = df.loc[
        df["NOC"] == "GER", "Team"
    ].str.replace(r"^(East|West)\s+Germany", "Germany", regex=True)
    # Fusionner ROC (Russie sous sanctions) avec la Russie (RUS)
    df.loc[df["NOC"] == "ROC", "NOC"] = "RUS"
    df.loc[df["NOC"] == "RUS", "Team"] = df.loc[
        df["NOC"] == "RUS", "Team"
    ].str.replace(r"^ROC$", "Russia", regex=True)
    # Fusionner Serbie-et-Monténégro (SCG) avec la Serbie (SRB)
    df.loc[df["NOC"] == "SCG", "NOC"] = "SRB"
    df.loc[df["NOC"] == "SRB", "Team"] = df.loc[
        df["NOC"] == "SRB", "Team"
    ].str.replace(r"^Serbia and Montenegro$", "Serbia", regex=True)
    # Fusionner Bohème (BOH) avec la République tchèque (CZE)
    df.loc[df["NOC"] == "BOH", "NOC"] = "CZE"
    df.loc[df["NOC"] == "CZE", "Team"] = df.loc[
        df["NOC"] == "CZE", "Team"
    ].str.replace(r"^Bohemia.*$", "Czech Republic", regex=True)
    # Flag médaille binaire
    df["Has_Medal"] = df["Medal"].isin(["Gold", "Silver", "Bronze"]).astype(int)
    return df.reset_index(drop=True)


def get_medals_df(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne uniquement les lignes avec une médaille."""
    return df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

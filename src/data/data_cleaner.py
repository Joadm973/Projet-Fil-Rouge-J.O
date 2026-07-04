"""Module de nettoyage et de préparation des données pour l'analyse."""
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et prépare le dataset pour l'analyse."""
    df = df.copy()
    # Uniquement les JO d'été
    df = df[df["Season"] == "Summer"]
    df = df.drop_duplicates()
    
    # Correction des noms d'athlètes corrompus
    name_fixes = {
        "Michael Ii": "Michael Phelps",
        "Larysa (diriy-)": "Larysa Latynina",
        "Vra (-odloilov)": "Věra Čáslavská",
        "Aladr (-gerei)": "Aladár Gerevich",
        "Jennifer (-cumpelik)": "Jenny Thompson",
        "Dara -minas)": "Dara Torres",
        "Natalie (-hall)": "Natalie Coughlin",
        "gnes (klein)": "Ágnes Keleti",
        "Lyudmila (-borzova)": "Lyudmila Turischeva",
        "Nadia (-conner)": "Nadia Comăneci",
        "Kornelia -grummt)": "Kornelia Ender",
        "Margit -szalay)": "Margit Korondi",
        "Petria (-jones)": "Petria Thomas",
        "Sofiya (poduzdova-)": "Sofiya Muratova",
        "Viljo (koukkari-)": "Ville Ritola",
        "Albert (thorvaldsen-)": "Albert Helgerud",
        "Amanda (-brown)": "Amanda Beard",
        "Dana (-grant)": "Dana Vollmer",
        "Karin (-bttner)": "Karin Janz",
        "Kirsty (-seward)": "Kirsty Coventry",
        "Shannon -falconetti)": "Shannon Miller",
        "Simona (-tabr)": "Simona Amânar",
        "Amy (-rouen)": "Amy Van Dyken",
        "Anders (johansson-)": "Anders Holmertz",
        "Andrea (-pinske)": "Andrea Pollack",
        "Angelina -sims)": "Angelina Martino",
        "Kimberly (-harryman)": "Kim Rhode",
        "Nellya (-achasov)": "Nelli Kim",
        "Olga (todenbier-)": "Olga Tass",
        "Olga -voynich)": "Olga Korbut",
        "Renate (meiner-)": "Renate Stecher",
        "Viorica (-harper)": "Daniela Silivaș",
        "Antje (-meeuw)": "Antje Buschschulte"
    }
    df["Name"] = df["Name"].replace(name_fixes)
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

"""Module de nettoyage et de préparation des données pour l'analyse."""
import re

import pandas as pd

# Noms tronqués irrécupérables du dataset source : un prénom + suffixe générique
# ("William Jr.", "John Jr.", "Carl Ii"…) regroupe en réalité plusieurs athlètes
# distincts sous le même libellé. Impossible à réattribuer -> à exclure des
# classements individuels (les médailles restent comptées au niveau pays/sport).
AMBIGUOUS_NAME_PATTERN = re.compile(r"^\S+\s+(?:Jr|Sr|Ii|Iii|Iv)\.?$", re.IGNORECASE)


def is_ambiguous_athlete_name(names: pd.Series) -> pd.Series:
    """Masque booléen : True si le nom fusionne plusieurs athlètes distincts."""
    return names.str.match(AMBIGUOUS_NAME_PATTERN, na=False)


# Token de nom de famille écrit en capitales (≥2 majuscules consécutives),
# ex. "McKEON", "O'CALLAGHAN" — format « NOM Prénom » des éditions 2020+.
_SHOUTING_TOKEN = re.compile(r"[A-Z]{2,}")


def _reorder_reversed_name(name: str) -> str:
    """Convertit « McKEON Emma » en « Emma Mckeon » (format des éditions <2020).

    Les tokens contenant ≥2 majuscules consécutives sont le nom de famille ;
    ils sont recapitalisés et déplacés en fin. Les noms sans token en capitales
    (ou entièrement en capitales, ordre indécidable) sont laissés tels quels.
    """
    tokens = str(name).split()
    caps_idx = [i for i, t in enumerate(tokens) if _SHOUTING_TOKEN.search(t)]
    if len(tokens) < 2 or not caps_idx or len(caps_idx) == len(tokens):
        return name
    given = [t for i, t in enumerate(tokens) if i not in caps_idx]
    surname = [tokens[i].capitalize() for i in caps_idx]
    return " ".join(given + surname)


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
    # Harmoniser le format « NOM Prénom » des éditions 2020+ (ex. "McKEON Emma")
    # vers le format historique « Prénom Nom » ("Emma Mckeon"). Sans cela, la
    # carrière d'un athlète présent avant et après 2020 est scindée en deux
    # identités distinctes (faux "breakouts", côtes sous-évaluées).
    recent = df["Year"] >= 2020
    df.loc[recent, "Name"] = df.loc[recent, "Name"].map(_reorder_reversed_name)
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
    # Standardiser les noms d'équipe : un NOC = un libellé unique (le plus fréquent).
    # Le dataset contient des noms de clubs ("Vesper Boat Club", 1904) et des
    # suffixes d'embarcations ("United States-1") qui dupliquent les pays dans
    # tous les agrégats par équipe (cartes, classements, régressions).
    canonical_team = df.groupby("NOC")["Team"].agg(lambda s: s.value_counts().idxmax())
    df["Team"] = df["NOC"].map(canonical_team)
    # Flag médaille binaire
    df["Has_Medal"] = df["Medal"].isin(["Gold", "Silver", "Bronze"]).astype(int)
    return df.reset_index(drop=True)


def get_medals_df(df: pd.DataFrame) -> pd.DataFrame:
    """Retourne uniquement les lignes avec une médaille."""
    return df[df["Medal"].isin(["Gold", "Silver", "Bronze"])].copy()

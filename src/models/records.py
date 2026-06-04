"""Timeline des records et premières olympiques par édition."""
import pandas as pd

MEDAL_VALUES = ["Gold", "Silver", "Bronze"]


def get_olympic_editions(df: pd.DataFrame) -> list[int]:
    """Retourne la liste triée des années olympiques disponibles."""
    return sorted(df["Year"].unique().tolist())


def get_edition_summary(df: pd.DataFrame, year: int) -> dict:
    """Résumé des records et premières pour une édition olympique donnée.

    Returns dict:
        year, city, total_medals, total_countries,
        top_countries  : DataFrame (Pays, NOC, Médailles)
        top_athletes   : DataFrame (Athlète, Pays, Sport, Médailles)
        new_sports     : list[str]  — disciplines à leur 1ère édition
        debut_countries: list[str]  — pays remportant leur 1ère médaille
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    edition = medals[medals["Year"] == year]
    previous = medals[medals["Year"] < year]

    city_rows = df[df["Year"] == year]["City"]
    city = city_rows.iloc[0] if not city_rows.empty else str(year)

    top_countries = (
        edition.groupby(["Team", "NOC"])
        .size()
        .reset_index(name="Médailles")
        .rename(columns={"Team": "Pays"})
        .nlargest(10, "Médailles")
        .reset_index(drop=True)
    )
    top_countries.index += 1

    top_athletes = (
        edition.groupby(["Name", "Team", "Sport"])
        .size()
        .reset_index(name="Médailles")
        .rename(columns={"Name": "Athlète", "Team": "Pays"})
        .nlargest(10, "Médailles")
        .reset_index(drop=True)
    )
    top_athletes.index += 1

    prev_sports = set(previous["Sport"].unique()) if not previous.empty else set()
    new_sports = sorted(set(edition["Sport"].unique()) - prev_sports)

    prev_nocs = set(previous["NOC"].unique()) if not previous.empty else set()
    debut_nocs = set(edition["NOC"].unique()) - prev_nocs
    noc_to_team = df.groupby("NOC")["Team"].first().to_dict()
    debut_countries = sorted(noc_to_team.get(n, n) for n in debut_nocs)

    return {
        "year": year,
        "city": city,
        "total_medals": len(edition),
        "total_countries": edition["NOC"].nunique(),
        "top_countries": top_countries,
        "top_athletes": top_athletes,
        "new_sports": new_sports,
        "debut_countries": debut_countries,
    }


def get_all_time_records(df: pd.DataFrame) -> dict:
    """Records absolus toutes éditions confondues.

    Returns dict:
        best_country_performances : DataFrame — top 10 performances nationales
        best_athlete_performances : DataFrame — top 10 performances individuelles
        countries_per_year        : DataFrame — nb pays médaillés par édition
        sports_per_year           : DataFrame — nb disciplines par édition
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)]

    country_ed = (
        medals.groupby(["Team", "NOC", "Year", "City"])
        .size()
        .reset_index(name="Médailles")
        .rename(columns={"Team": "Pays"})
    )
    best_country = (
        country_ed.nlargest(10, "Médailles")
        .reset_index(drop=True)
    )
    best_country.index += 1

    athlete_ed = (
        medals.groupby(["Name", "Team", "Sport", "Year"])
        .size()
        .reset_index(name="Médailles")
        .rename(columns={"Name": "Athlète", "Team": "Pays"})
    )
    best_athletes = (
        athlete_ed.nlargest(10, "Médailles")
        .reset_index(drop=True)
    )
    best_athletes.index += 1

    countries_per_year = (
        medals.groupby("Year")["NOC"]
        .nunique()
        .reset_index(name="Pays médaillés")
    )

    sports_per_year = (
        medals.groupby("Year")["Sport"]
        .nunique()
        .reset_index(name="Disciplines")
    )

    return {
        "best_country_performances": best_country,
        "best_athlete_performances": best_athletes,
        "countries_per_year": countries_per_year,
        "sports_per_year": sports_per_year,
    }


def get_first_medals_timeline(df: pd.DataFrame) -> pd.DataFrame:
    """Compte cumulatif des pays ayant remporté leur 1ère médaille olympique.

    Returns DataFrame: first_year, new_countries, cumul_pays
    """
    medals = df[df["Medal"].isin(MEDAL_VALUES)]
    first_year = medals.groupby("NOC")["Year"].min().reset_index(name="first_year")

    by_year = (
        first_year.groupby("first_year")
        .size()
        .reset_index(name="new_countries")
        .sort_values("first_year")
    )
    by_year["cumul_pays"] = by_year["new_countries"].cumsum()
    return by_year

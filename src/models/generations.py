"""Détection des nouvelles générations olympiques.

"Nouvelle génération" = athlète dont la 1ère participation olympique (estivale)
a eu lieu en 2016 ou après, avec au moins une médaille.
"""
import pandas as pd

MEDAL_VALUES = ["Gold", "Silver", "Bronze"]
NEW_GEN_FROM = 2016
RECENT_FROM = 2020


def _medals(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["Medal"].isin(MEDAL_VALUES)].copy()


def detect_new_gen_athletes(df: pd.DataFrame, debut_from: int = NEW_GEN_FROM) -> pd.DataFrame:
    """Athlètes dont la 1ère apparition olympique est >= debut_from.

    Returns DataFrame: Name, Team, Sport, debut_year, nb_editions,
                       nb_medals, gold, silver, bronze, editions_list
    """
    m = _medals(df)

    debut = df.groupby("Name")["Year"].min().reset_index(name="debut_year")
    new_gen_names = debut[debut["debut_year"] >= debut_from]["Name"]
    m_new = m[m["Name"].isin(new_gen_names)]

    medal_counts = (
        m_new.groupby(["Name", "Team", "Sport"])
        .agg(
            nb_medals=("Medal", "count"),
            gold=("Medal", lambda x: (x == "Gold").sum()),
            silver=("Medal", lambda x: (x == "Silver").sum()),
            bronze=("Medal", lambda x: (x == "Bronze").sum()),
            nb_editions=("Year", "nunique"),
            editions_list=("Year", lambda x: sorted(x.unique().tolist())),
        )
        .reset_index()
    )
    medal_counts = medal_counts.merge(
        debut[debut["Name"].isin(new_gen_names)], on="Name"
    )

    medal_counts["score"] = (
        medal_counts["gold"] * 3
        + medal_counts["silver"] * 2
        + medal_counts["bronze"]
    )

    return medal_counts.sort_values("score", ascending=False).reset_index(drop=True)


def detect_breakout_athletes(df: pd.DataFrame) -> pd.DataFrame:
    """Athlètes sans médaille avant RECENT_FROM, avec médaille en RECENT_FROM+.

    Returns DataFrame: Name, Team, Sport, first_medal_year, medals_recent, score
    """
    m = _medals(df)

    before = m[m["Year"] < RECENT_FROM].groupby("Name").size().rename("medals_before")
    after = m[m["Year"] >= RECENT_FROM].groupby("Name").agg(
        medals_recent=("Medal", "count"),
        gold=("Medal", lambda x: (x == "Gold").sum()),
        silver=("Medal", lambda x: (x == "Silver").sum()),
        bronze=("Medal", lambda x: (x == "Bronze").sum()),
        first_medal_year=("Year", "min"),
        Sport=("Sport", "first"),
        Team=("Team", "first"),
    ).reset_index()

    pure_breakout = after[~after["Name"].isin(before.index)].copy()
    pure_breakout["score"] = (
        pure_breakout["gold"] * 3
        + pure_breakout["silver"] * 2
        + pure_breakout["bronze"]
    )
    return pure_breakout.sort_values("score", ascending=False).reset_index(drop=True)


def detect_generation_shift(
    df: pd.DataFrame,
    old_years: tuple[int, int] = (2008, 2016),
    new_years: tuple[int, int] = (2020, 2024),
) -> pd.DataFrame:
    """Mesure le renouvellement des athlètes dominants par sport entre deux périodes.

    Taux de renouvellement = 1 − (athlètes communs / max(top_old, top_new))
    Retourne les sports triés par renouvellement décroissant.

    Returns DataFrame: Sport, top_old_count, top_new_count, overlap, renewal_rate
    """
    m = _medals(df)
    old = m[(m["Year"] >= old_years[0]) & (m["Year"] <= old_years[1])]
    new = m[(m["Year"] >= new_years[0]) & (m["Year"] <= new_years[1])]

    rows = []
    for sport in m["Sport"].unique():
        old_top = set(
            old[old["Sport"] == sport]
            .groupby("Name").size().nlargest(10).index
        )
        new_top = set(
            new[new["Sport"] == sport]
            .groupby("Name").size().nlargest(10).index
        )
        if not old_top and not new_top:
            continue
        overlap = len(old_top & new_top)
        denom = max(len(old_top), len(new_top))
        renewal = round(1 - overlap / denom, 3) if denom else 0.0
        rows.append({
            "Sport": sport,
            "top_old_count": len(old_top),
            "top_new_count": len(new_top),
            "overlap": overlap,
            "renewal_rate": renewal,
        })

    return (
        pd.DataFrame(rows)
        .sort_values("renewal_rate", ascending=False)
        .reset_index(drop=True)
    )


def detect_new_medaling_nations(df: pd.DataFrame, from_year: int = NEW_GEN_FROM) -> pd.DataFrame:
    """Pays remportant leur 1ère médaille en from_year ou après.

    Returns DataFrame: Team, NOC, first_medal_year, medals_total, Sports
    """
    m = _medals(df)
    first_year = m.groupby("NOC")["Year"].min().reset_index(name="first_medal_year")
    new_nations_noc = first_year[first_year["first_medal_year"] >= from_year]["NOC"]

    m_new = m[m["NOC"].isin(new_nations_noc)]
    stats = (
        m_new.groupby(["NOC"])
        .agg(
            Team=("Team", "first"),
            first_medal_year=("Year", "min"),
            medals_total=("Medal", "count"),
            Sports=("Sport", lambda x: ", ".join(sorted(x.unique()))),
        )
        .reset_index()
    )
    return stats.sort_values(["first_medal_year", "medals_total"], ascending=[True, False]).reset_index(drop=True)

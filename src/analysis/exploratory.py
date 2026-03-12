import pandas as pd


def medals_by_country(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return (
        medals.groupby(["Team", "NOC", "Medal"])
        .size()
        .reset_index(name="Count")
    )


def medals_by_year(df: pd.DataFrame) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return medals.groupby(["Year", "Medal"]).size().reset_index(name="Count")


def top_athletes(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    medals = df[df["Medal"].isin(["Gold", "Silver", "Bronze"])]
    return (
        medals.groupby(["Name", "Team", "Sport"])
        .size()
        .nlargest(n)
        .reset_index(name="Médailles")
    )


def participation_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("Year").agg(
        Athlètes=("Name", "nunique"),
        Pays=("NOC", "nunique"),
        Sports=("Sport", "nunique"),
    ).reset_index()

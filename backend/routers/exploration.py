import numpy as np
from fastapi import APIRouter, Query
from typing import Optional
from backend.deps import get_df

router = APIRouter()
MEDALS = ["Gold", "Silver", "Bronze"]


def _filter(year_min: int, year_max: int, gender: str):
    df = get_df()
    df = df[(df["Year"] >= year_min) & (df["Year"] <= year_max)]
    if gender != "all":
        df = df[df["Sex"] == gender.upper()]
    return df


@router.get("/meta")
def meta():
    df = get_df()
    return {"year_min": int(df["Year"].min()), "year_max": int(df["Year"].max())}


@router.get("/top-countries")
def top_countries(
    year_min: int = Query(1896), year_max: int = Query(2024),
    gender: str = Query("all"), top_n: int = Query(15),
):
    df = _filter(year_min, year_max, gender)
    medals = df[df["Medal"].isin(MEDALS)]
    top_teams = medals.groupby("Team").size().nlargest(top_n).index.tolist()
    r = (
        medals[medals["Team"].isin(top_teams)]
        .groupby(["NOC", "Team", "Medal"])
        .size().reset_index(name="count")
    )
    return r.replace({np.nan: None}).to_dict(orient="records")


@router.get("/top-sports")
def top_sports(
    year_min: int = Query(1896), year_max: int = Query(2024),
    gender: str = Query("all"), top_n: int = Query(20),
):
    df = _filter(year_min, year_max, gender)
    medals = df[df["Medal"].isin(MEDALS)]
    top_sport_names = medals.groupby("Sport").size().nlargest(top_n).index.tolist()
    r = medals[medals["Sport"].isin(top_sport_names)].groupby(["Sport", "Sex"]).size().reset_index(name="count")
    r["Sex"] = r["Sex"].map({"M": "Hommes", "F": "Femmes"})
    return r.replace({np.nan: None}).to_dict(orient="records")


@router.get("/trends")
def trends(
    year_min: int = Query(1896), year_max: int = Query(2024),
    gender: str = Query("all"),
):
    df = _filter(year_min, year_max, gender)
    medals = df[df["Medal"].isin(MEDALS)]
    gold_by_year = medals[medals["Medal"] == "Gold"].groupby("Year").size().reset_index(name="gold")
    parity = df.groupby(["Year", "Sex"])["Name"].nunique().reset_index()
    parity["Sex"] = parity["Sex"].map({"M": "Hommes", "F": "Femmes"})
    return {
        "gold_by_year": gold_by_year.replace({np.nan: None}).to_dict(orient="records"),
        "parity": parity.replace({np.nan: None}).to_dict(orient="records"),
    }


@router.get("/heatmap")
def heatmap(
    year_min: int = Query(1896), year_max: int = Query(2024),
    top_n: int = Query(15),
):
    df = get_df()
    medals = df[df["Medal"] == "Gold"]
    medals = medals[(medals["Year"] >= year_min) & (medals["Year"] <= year_max)]
    top_countries = medals.groupby("Team").size().nlargest(top_n).index.tolist()
    r = (
        medals[medals["Team"].isin(top_countries)]
        .groupby(["Team", "Year"]).size().reset_index(name="gold")
    )
    return r.replace({np.nan: None}).to_dict(orient="records")


@router.get("/choropleth")
def choropleth(
    year_min: int = Query(1896), year_max: int = Query(2024),
    gender: str = Query("all"),
):
    df = _filter(year_min, year_max, gender)
    medals = df[df["Medal"].isin(MEDALS)]
    r = medals.groupby(["NOC", "Team"]).size().reset_index(name="total")
    return r.replace({np.nan: None}).to_dict(orient="records")

import numpy as np
from fastapi import APIRouter, Query
from backend.deps import get_df
from src.data.data_cleaner import is_ambiguous_athlete_name

router = APIRouter()
MEDALS = ["Gold", "Silver", "Bronze"]


@router.get("/top")
def top_athletes(
    sport: str = Query("all"),
    country: str = Query("all"),
    medals: str = Query("Gold,Silver,Bronze"),
    year_min: int = Query(1896),
    year_max: int = Query(2024),
    top_n: int = Query(25),
):
    df = get_df()
    medal_list = medals.split(",")
    filt = df[df["Medal"].isin(medal_list)]
    # Exclut les noms fusionnant plusieurs athlètes ("William Jr.") du palmarès.
    filt = filt[~is_ambiguous_athlete_name(filt["Name"])]
    filt = filt[(filt["Year"] >= year_min) & (filt["Year"] <= year_max)]
    if sport != "all":
        filt = filt[filt["Sport"] == sport]
    if country != "all":
        noc = df.loc[df["Team"] == country, "NOC"]
        filt = filt[filt["NOC"].isin(noc)]
    top = (
        filt.groupby(["Name", "Team", "Sport"])
        .size().nlargest(top_n).reset_index(name="total")
    )
    return top.replace({np.nan: None}).to_dict(orient="records")


@router.get("/search")
def search_athletes(q: str = Query("", min_length=0)):
    q = q.strip()
    if len(q) < 2:
        return []
    df = get_df()
    m = df[df["Name"].str.contains(q, case=False, na=False, regex=False)]
    m = m[~is_ambiguous_athlete_name(m["Name"])]
    medals = m[m["Medal"].isin(MEDALS)]
    totals = medals.groupby(["Name", "Team"]).size().reset_index(name="total")
    results = totals.sort_values("total", ascending=False).head(50)
    return results.replace({np.nan: None}).to_dict(orient="records")


@router.get("/detail")
def athlete_detail(
    name: str = Query(...),
    year_min: int = Query(1896),
    year_max: int = Query(2024),
    medals: str = Query("Gold,Silver,Bronze"),
):
    df = get_df()
    medal_list = medals.split(",")
    filt = df[(df["Medal"].isin(medal_list)) & (df["Name"] == name)]
    filt = filt[(filt["Year"] >= year_min) & (filt["Year"] <= year_max)]
    by_medal = filt.groupby(["Name", "Medal"]).size().reset_index(name="count")
    by_year = filt.groupby("Year").size().reset_index(name="medals")
    return {
        "by_medal": by_medal.replace({np.nan: None}).to_dict(orient="records"),
        "by_year": by_year.replace({np.nan: None}).to_dict(orient="records"),
        "sports": filt["Sport"].unique().tolist(),
        "editions": sorted(filt["Year"].unique().tolist()),
    }


@router.get("/gender-medals")
def gender_medals(
    year_min: int = Query(1896),
    year_max: int = Query(2024),
    medals: str = Query("Gold,Silver,Bronze"),
):
    df = get_df()
    medal_list = medals.split(",")
    filt = df[(df["Medal"].isin(medal_list)) & (df["Year"] >= year_min) & (df["Year"] <= year_max)]
    r = filt.groupby(["Sex", "Medal"]).size().reset_index(name="count")
    r["Sex"] = r["Sex"].map({"M": "Hommes", "F": "Femmes"})
    return r.replace({np.nan: None}).to_dict(orient="records")


@router.get("/timeline")
def athlete_timeline(
    name: str = Query(...),
):
    df = get_df()
    filt = df[(df["Name"] == name) & df["Medal"].isin(MEDALS)]
    r = filt.groupby(["Year", "Sport", "Event", "Medal"]).size().reset_index(name="n")
    return r.replace({np.nan: None}).to_dict(orient="records")


@router.get("/filters-meta")
def filters_meta():
    df = get_df()
    canonical_team = df.groupby("NOC")["Team"].agg(lambda s: s.value_counts().idxmax())
    return {
        "sports": sorted(df["Sport"].unique().tolist()),
        "countries": sorted(canonical_team.unique().tolist()),
    }

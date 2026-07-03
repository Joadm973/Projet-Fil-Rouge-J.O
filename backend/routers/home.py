from fastapi import APIRouter
from backend.deps import get_df
from src.analysis.exploratory import medals_by_year, participation_over_time

router = APIRouter()

MEDALS = ["Gold", "Silver", "Bronze"]


@router.get("/kpis")
def kpis():
    df = get_df()
    medals_df = df[df["Medal"].isin(MEDALS)]
    gold_leaders = medals_df[medals_df["Medal"] == "Gold"].groupby("Team").size()
    top_country = gold_leaders.idxmax() if len(gold_leaders) else "—"
    return {
        "editions": int(df["Year"].nunique()),
        "athletes": int(df["Name"].nunique()),
        "countries": int(df["NOC"].nunique()),
        "sports": int(df["Sport"].nunique()),
        "gold_medals": int((medals_df["Medal"] == "Gold").sum()),
        "top_country": top_country,
        "last_year": int(df["Year"].max()),
        "last_year_countries": int(df[df["Year"] == df["Year"].max()]["NOC"].nunique()),
    }


@router.get("/medals-by-year")
def medals_by_year_endpoint():
    df = get_df()
    mby = medals_by_year(df)
    return mby.to_dict(orient="records")


@router.get("/gender-participation")
def gender_participation():
    df = get_df()
    gp = df.groupby(["Year", "Sex"])["Name"].nunique().reset_index()
    gp["Sex"] = gp["Sex"].map({"M": "Hommes", "F": "Femmes"})
    gp.columns = ["year", "sex", "count"]
    return gp.to_dict(orient="records")


@router.get("/medals-by-country")
def medals_by_country():
    df = get_df()
    medals_df = df[df["Medal"].isin(MEDALS)]
    r = medals_df.groupby(["NOC", "Team"]).size().reset_index(name="total")
    return r.to_dict(orient="records")


@router.get("/participation")
def participation():
    df = get_df()
    part = participation_over_time(df)
    return part.to_dict(orient="records")


@router.get("/medals-by-sport")
def medals_by_sport():
    df = get_df()
    medals_df = df[df["Medal"].isin(MEDALS)]
    r = medals_df.groupby("Sport").size().reset_index(name="medals")
    return r.to_dict(orient="records")

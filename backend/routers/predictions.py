from fastapi import APIRouter, Query
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error
from backend.deps import get_df
from src.models.predictor import get_active_nocs
from src.models.ratings import compute_sport_dominance, compute_athlete_ratings, generate_recommendations
from src.models.records import get_edition_summary, get_all_time_records, get_first_medals_timeline, get_olympic_editions

router = APIRouter()
MEDALS = ["Gold", "Silver", "Bronze"]

MODELS = {
    "linear": lambda: LinearRegression(),
    "ridge": lambda: Ridge(alpha=1.0),
    "gradient_boosting": lambda: GradientBoostingRegressor(n_estimators=100, random_state=42),
    "polynomial": lambda: Pipeline([
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("lin", LinearRegression()),
    ]),
}


@router.get("/predict")
def predict(
    model: str = Query("linear"),
    top_n: int = Query(20),
):
    df = get_df()
    medals = df[df["Medal"].isin(MEDALS)]
    medal_counts = medals.groupby(["NOC", "Team", "Year"]).size().reset_index(name="Total")
    m = MODELS.get(model, MODELS["linear"])()
    active = get_active_nocs(df)
    results = []
    for noc, group in medal_counts.groupby("NOC"):
        if noc not in active:
            continue
        group = group.sort_values("Year")
        if len(group) < 3:
            continue
        X = group[["Year"]].values
        y = group["Total"].values
        try:
            m.fit(X, y)
            pred = float(m.predict([[2028]])[0])
            mae = mean_absolute_error(y, m.predict(X))
            results.append({
                "noc": noc,
                "country": group["Team"].iloc[-1],
                "predicted": max(0, round(pred)),
                "mae": round(mae, 1),
            })
        except Exception:
            continue
    results.sort(key=lambda x: x["predicted"], reverse=True)
    return results[:top_n]


@router.get("/country-trend")
def country_trend(team: str = Query(...)):
    df = get_df()
    medals = df[df["Medal"].isin(MEDALS)]
    hist = (
        medals[medals["Team"] == team]
        .groupby("Year").size().reset_index(name="total")
        .sort_values("Year")
    )
    if len(hist) < 3:
        return {"history": hist.replace({np.nan: None}).to_dict(orient="records"), "pred2028": None}
    X = hist[["Year"]].values
    y = hist["Total"].values if "Total" in hist.columns else hist["total"].values
    m = LinearRegression()
    m.fit(X, y)
    pred = max(0.0, float(m.predict([[2028]])[0]))
    residuals = y - m.predict(X)
    std = float(np.std(residuals))
    return {
        "history": hist.replace({np.nan: None}).to_dict(orient="records"),
        "pred2028": round(pred),
        "ci_low": max(0, round(pred - 1.96 * std)),
        "ci_high": round(pred + 1.96 * std),
    }


@router.get("/dominance")
def dominance():
    df = get_df()
    dom = compute_sport_dominance(df)
    return dom.replace({np.nan: None}).to_dict(orient="records")


@router.get("/athlete-ratings")
def athlete_ratings(top_n: int = Query(30)):
    df = get_df()
    r = compute_athlete_ratings(df)
    return r.head(top_n).replace({np.nan: None}).to_dict(orient="records")


@router.get("/recommendations")
def recommendations():
    df = get_df()
    recs = generate_recommendations(df)
    return {
        "rising_nations": recs["rising_nations"].head(10).replace({np.nan: None}).to_dict(orient="records"),
        "competitive_sports": recs["competitive_sports"].head(8).tolist(),
        "dominated_sports": recs["dominated_sports"].head(8).tolist(),
        "france_top_sports": recs["france_top_sports"].head(8).reset_index(name="medals_recent").replace({np.nan: None}).to_dict(orient="records"),
    }


@router.get("/editions")
def editions():
    df = get_df()
    return get_olympic_editions(df)


@router.get("/edition-summary")
def edition_summary(year: int = Query(2024)):
    df = get_df()
    s = get_edition_summary(df, year)
    return {
        "year": s["year"],
        "city": s["city"],
        "total_medals": s["total_medals"],
        "total_countries": s["total_countries"],
        "top_countries": s["top_countries"].reset_index().replace({np.nan: None}).to_dict(orient="records"),
        "new_sports": s["new_sports"],
        "debut_countries": s["debut_countries"],
    }


@router.get("/timeline-diversity")
def timeline_diversity():
    df = get_df()
    alltime = get_all_time_records(df)
    tl = get_first_medals_timeline(df)
    return {
        "countries_per_year": alltime["countries_per_year"].replace({np.nan: None}).to_dict(orient="records"),
        "sports_per_year": alltime["sports_per_year"].replace({np.nan: None}).to_dict(orient="records"),
        "first_medals_timeline": tl.replace({np.nan: None}).to_dict(orient="records"),
    }

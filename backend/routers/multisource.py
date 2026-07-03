from fastapi import APIRouter, Query
from backend.deps import get_df
from src.data.api_fetcher import fetch_country_metadata, enrich_medals_with_country_data
import functools
import pandas as pd

router = APIRouter()
MEDALS = ["Gold", "Silver", "Bronze"]


@functools.lru_cache(maxsize=1)
def _meta() -> pd.DataFrame:
    return fetch_country_metadata()


def _enriched() -> pd.DataFrame:
    df = get_df()
    medals = df[df["Medal"].isin(MEDALS)]
    agg = medals.groupby(["NOC", "Team"]).size().reset_index(name="medals")
    return enrich_medals_with_country_data(agg, _meta())


@router.get("/overview")
def overview():
    enriched = _enriched()
    matched = int(enriched["population"].notna().sum())
    return {"total_countries": len(enriched), "matched": matched}


@router.get("/per-capita")
def per_capita(min_medals: int = Query(10), min_pop: int = Query(500000), top_n: int = Query(20)):
    enriched = _enriched()
    r = (
        enriched
        .dropna(subset=["medals_per_million", "population"])
        .query(f"population > {min_pop} and medals >= {min_medals}")
        .sort_values("medals_per_million", ascending=False)
        .head(top_n)
    )
    return r[["NOC", "Team", "medals", "medals_per_million", "population", "region"]].to_dict(orient="records")


@router.get("/scatter")
def scatter():
    enriched = _enriched()
    r = enriched.dropna(subset=["population", "region"]).query("medals > 0")
    return r[["NOC", "Team", "medals", "medals_per_million", "population", "region"]].to_dict(orient="records")


@router.get("/by-region")
def by_region():
    enriched = _enriched()
    r = (
        enriched.dropna(subset=["region"])
        .groupby("region")
        .agg(medals=("medals", "sum"), nb_countries=("NOC", "count"), total_pop=("population", "sum"))
        .reset_index()
        .sort_values("medals", ascending=False)
    )
    r["medals_per_million"] = (r["medals"] / r["total_pop"] * 1_000_000).round(3)
    return r.to_dict(orient="records")


@router.get("/region-trend")
def region_trend():
    df = get_df()
    medals = df[df["Medal"].isin(MEDALS)]
    agg = medals.groupby(["NOC", "Team", "Year"]).size().reset_index(name="medals")
    meta = _meta()
    keep = [c for c in ["NOC", "region"] if c in meta.columns]
    merged = agg.merge(meta[keep], on="NOC", how="left")
    trend = (
        merged.dropna(subset=["region"])
        .query("Year >= 1992")
        .groupby(["Year", "region"])["medals"].sum()
        .reset_index()
    )
    total_by_year = trend.groupby("Year")["medals"].transform("sum")
    trend["share_pct"] = (trend["medals"] / total_by_year * 100).round(1)
    return trend.to_dict(orient="records")


@router.get("/gdp-scatter")
def gdp_scatter():
    enriched = _enriched()
    r = enriched.dropna(subset=["gdp_per_capita", "region"]).query("medals > 0").copy()
    r["gdp_rank_pct"] = r["gdp_per_capita"].rank(pct=True).round(3)
    r["med_rank_pct"] = r["medals_per_million"].rank(pct=True).round(3)
    r["overperformance"] = (r["med_rank_pct"] - r["gdp_rank_pct"]).round(3)
    cols = ["NOC", "Team", "medals", "medals_per_million", "population", "gdp_per_capita", "region", "overperformance"]
    return r[cols].to_dict(orient="records")


@router.get("/table")
def table():
    enriched = _enriched()
    cols = [c for c in ["NOC", "Team", "medals", "medals_per_million", "population", "gdp_per_capita", "region", "income_level"] if c in enriched.columns]
    r = enriched[cols].dropna(subset=["region"]).sort_values("medals", ascending=False)
    return r.to_dict(orient="records")

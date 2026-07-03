from fastapi import APIRouter, Query
from backend.deps import get_df
from src.models.generations import (
    detect_new_gen_athletes,
    detect_breakout_athletes,
    detect_generation_shift,
    detect_new_medaling_nations,
)

router = APIRouter()


@router.get("/new-gen")
def new_gen(top_n: int = Query(50)):
    df = get_df()
    r = detect_new_gen_athletes(df)
    return r.head(top_n).to_dict(orient="records")


@router.get("/breakouts")
def breakouts(top_n: int = Query(50)):
    df = get_df()
    r = detect_breakout_athletes(df)
    return r.head(top_n).to_dict(orient="records")


@router.get("/generation-shift")
def generation_shift():
    df = get_df()
    r = detect_generation_shift(df)
    return r.to_dict(orient="records")


@router.get("/new-nations")
def new_nations():
    df = get_df()
    r = detect_new_medaling_nations(df)
    return r.to_dict(orient="records")

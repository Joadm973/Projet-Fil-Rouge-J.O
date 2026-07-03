"""Shared data dependency — loaded once, cached."""
import functools
import pandas as pd
from src.data.data_loader import load_raw_data
from src.data.data_cleaner import clean_data


@functools.lru_cache(maxsize=1)
def get_df() -> pd.DataFrame:
    return clean_data(load_raw_data())

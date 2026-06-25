"""Acquisition de données depuis des sources externes (API).

Sources :
  - World Bank API v2 : métadonnées pays (région, niveau de revenu)
  - World Bank API v2 : population (indicateur SP.POP.TOTL)
  - World Bank API v2 : PIB par habitant (indicateur NY.GDP.PCAP.CD)

Cache local : data/processed/countries_api.json
API docs : https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
"""
import json
import logging
import urllib.request
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_CACHE_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "countries_api.json"

_WB_BASE = "https://api.worldbank.org/v2"
_WB_COUNTRIES_URL = f"{_WB_BASE}/country?format=json&per_page=300"
_WB_POP_URL = (
    f"{_WB_BASE}/country/all/indicator/SP.POP.TOTL"
    "?format=json&mrv=1&per_page=300"
)
_WB_GDP_URL = (
    f"{_WB_BASE}/country/all/indicator/NY.GDP.PCAP.CD"
    "?format=json&mrv=1&per_page=300"
)

# NOC (Olympic codes) → ISO 3166-1 alpha-3 (World Bank id / cca3)
# Only entries where NOC ≠ ISO3 are listed; identical codes fall through.
NOC_TO_ISO3: dict[str, str | None] = {
    "NED": "NLD",
    "GER": "DEU",
    "SUI": "CHE",
    "DEN": "DNK",
    "CHI": "CHL",
    "CRO": "HRV",
    "PHI": "PHL",
    "MAS": "MYS",
    "SIN": "SGP",
    "INA": "IDN",
    "ZIM": "ZWE",
    "TAN": "TZA",
    "GRE": "GRC",
    "BUL": "BGR",
    "LAT": "LVA",
    "POR": "PRT",
    "URU": "URY",
    "PAR": "PRY",
    "HAI": "HTI",
    "BAH": "BHS",
    "TRI": "TTO",
    "RSA": "ZAF",
    "NGR": "NGA",
    "ALG": "DZA",
    "IRI": "IRN",
    "UAE": "ARE",
    "KSA": "SAU",
    "MGL": "MNG",
    "TPE": "TWN",
    "NEP": "NPL",
    "SRI": "LKA",
    "BAN": "BGD",
    "VIE": "VNM",
    "CAM": "KHM",
    "MYA": "MMR",
    "LIB": "LBN",
    "KUW": "KWT",
    "JOR": "JOR",
    "GUA": "GTM",
    "HON": "HND",
    "ESA": "SLV",
    "BOT": "BWA",
    "ZAM": "ZMB",
    "MOZ": "MOZ",
    "MAD": "MDG",
    "MRI": "MUS",
    "MAL": "MDV",
    "NIG": "NER",
    "SUD": "SDN",
    "FIJ": "FJI",
    "PNG": "PNG",
    "SAM": "WSM",
    "TON": "TON",
    "CZE": "CZE",
    "SVK": "SVK",
    "SLO": "SVN",
    "MKD": "MKD",
    "BIH": "BIH",
    "SRB": "SRB",
    "MNE": "MNE",
    "ALB": "ALB",
    "AZE": "AZE",
    "GEO": "GEO",
    "ARM": "ARM",
    "KAZ": "KAZ",
    "UZB": "UZB",
    "KGZ": "KGZ",
    "TJK": "TJK",
    "MDA": "MDA",
    "BLR": "BLR",
    "UKR": "UKR",
    "EST": "EST",
    "LTU": "LTU",
    "LBA": "LBY",
    "MTN": "MRT",
    "SOM": "SOM",
    "SEY": "SYC",
    "RWA": "RWA",
    "BDI": "BDI",
    "UGA": "UGA",
    "MWI": "MWI",
    "MLI": "MLI",
    "GEQ": "GNQ",
    "CPV": "CPV",
    "SLE": "SLE",
    "LBR": "LBR",
    "DJI": "DJI",
    "ERI": "ERI",
    "CMR": "CMR",
    "GHA": "GHA",
    "SEN": "SEN",
    "BEN": "BEN",
    "TOG": "TGO",
    "BUR": "BFA",
    "CIV": "CIV",
    "GUI": "GIN",
    "GAB": "GAB",
    "URS": None,   # defunct Soviet Union
    "IOA": None,   # Independent Olympic Athletes
    "EOR": None,   # Refugee Olympic Team
    "ROC": "RUS",  # merged to Russia in cleaner
}


def _fetch_json(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": "YPerf/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def _load_cache() -> dict | None:
    if _CACHE_PATH.exists():
        try:
            return json.loads(_CACHE_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _save_cache(data: dict) -> None:
    _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CACHE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _fetch_all() -> dict:
    """Appelle les 3 endpoints World Bank et retourne un dict structuré."""
    logger.info("Fetching World Bank data (countries, population, GDP)…")

    # 1. Countries metadata
    countries_raw = _fetch_json(_WB_COUNTRIES_URL)[1]
    countries: dict[str, dict] = {}
    for c in countries_raw:
        iso3 = c.get("id", "")
        if not iso3 or len(iso3) != 3:
            continue
        countries[iso3] = {
            "iso3": iso3,
            "country_name": c.get("name", ""),
            "region": c.get("region", {}).get("value", ""),
            "income_level": c.get("incomeLevel", {}).get("value", ""),
            "capital": c.get("capitalCity", ""),
        }

    # 2. Population
    pop_raw = _fetch_json(_WB_POP_URL)[1]
    for row in pop_raw:
        iso3 = row.get("countryiso3code", "")
        val = row.get("value")
        if iso3 in countries and val is not None:
            countries[iso3]["population"] = int(val)

    # 3. GDP per capita (USD)
    gdp_raw = _fetch_json(_WB_GDP_URL)[1]
    for row in gdp_raw:
        iso3 = row.get("countryiso3code", "")
        val = row.get("value")
        if iso3 in countries and val is not None:
            countries[iso3]["gdp_per_capita"] = round(float(val), 2)

    return countries


def fetch_country_metadata(force_refresh: bool = False) -> pd.DataFrame:
    """Retourne un DataFrame enrichi avec les métadonnées pays (World Bank).

    Colonnes: NOC, iso3, country_name, region, income_level, population, gdp_per_capita
    Cache dans data/processed/countries_api.json.
    """
    raw: dict | None = None
    if not force_refresh:
        raw = _load_cache()

    if raw is None:
        try:
            raw = _fetch_all()
            _save_cache(raw)
        except Exception as exc:
            logger.warning("World Bank API fetch failed: %s — using cache or empty.", exc)
            raw = _load_cache() or {}

    # Build NOC → row using NOC_TO_ISO3 mapping
    rows = []
    for noc, iso3_override in NOC_TO_ISO3.items():
        iso3 = iso3_override
        if iso3 is None:
            continue
        meta = raw.get(iso3)
        if meta:
            rows.append({"NOC": noc, **meta})

    # Also add NOCs that directly match ISO3 codes (not in override dict)
    override_nocs = set(NOC_TO_ISO3.keys())
    for iso3, meta in raw.items():
        if iso3 not in override_nocs:
            rows.append({"NOC": iso3, **meta})

    df = pd.DataFrame(rows).drop_duplicates(subset=["NOC"])
    # Ensure numeric types
    for col in ("population", "gdp_per_capita"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.reset_index(drop=True)


def enrich_medals_with_country_data(
    medals_df: pd.DataFrame,
    country_meta: pd.DataFrame,
) -> pd.DataFrame:
    """Fusionne un DataFrame de médailles (agrégé par NOC) avec les métadonnées.

    medals_df doit contenir: NOC, Team, medals
    Ajoute: population, region, income_level, gdp_per_capita, medals_per_million
    """
    keep = [c for c in ["NOC", "country_name", "population", "region",
                         "income_level", "gdp_per_capita"] if c in country_meta.columns]
    merged = medals_df.merge(country_meta[keep], on="NOC", how="left")

    if "population" in merged.columns:
        merged["medals_per_million"] = (
            (merged["medals"] / merged["population"] * 1_000_000)
            .where(merged["population"] > 0)
            .round(4)
        )
    return merged

"""
Configuration du projet JO 2028 - YPerf
"""

from pathlib import Path

# =============================================================================
# CHEMINS DU PROJET
# =============================================================================

# Répertoire racine du projet
ROOT_DIR = Path(__file__).parent

# Répertoires de données
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Répertoires sources
SRC_DIR = ROOT_DIR / "src"
NOTEBOOKS_DIR = ROOT_DIR / "notebooks"
ASSETS_DIR = ROOT_DIR / "assets"
DOCS_DIR = ROOT_DIR / "docs"

# =============================================================================
# FICHIERS DE DONNÉES
# =============================================================================

# Données brutes
RAW_OLYMPICS_FILE = RAW_DATA_DIR / "olympics_dataset.csv"

# Données traitées
CLEANED_DATA_FILE = PROCESSED_DATA_DIR / "olympics_cleaned.csv"
MEDALS_BY_COUNTRY_FILE = PROCESSED_DATA_DIR / "medals_by_country.csv"
MEDALS_BY_SPORT_FILE = PROCESSED_DATA_DIR / "medals_by_sport.csv"
ATHLETES_STATS_FILE = PROCESSED_DATA_DIR / "athletes_stats.csv"
PREDICTIONS_FILE = PROCESSED_DATA_DIR / "predictions_2028.csv"

# =============================================================================
# COLONNES DU DATASET
# =============================================================================

COLUMNS = {
    "player_id": "Identifiant unique de l'athlète",
    "Name": "Nom de l'athlète",
    "Sex": "Genre (M/F)",
    "Team": "Équipe/Pays",
    "NOC": "Code pays (3 lettres)",
    "Year": "Année des JO",
    "Season": "Saison (Summer/Winter)",
    "City": "Ville hôte",
    "Sport": "Sport",
    "Event": "Épreuve",
    "Medal": "Médaille (Gold/Silver/Bronze/No medal)"
}

# =============================================================================
# PARAMÈTRES D'ANALYSE
# =============================================================================

# Années des JO d'été récents (pour l'analyse)
SUMMER_OLYMPICS_YEARS = [1992, 1996, 2000, 2004, 2008, 2012, 2016, 2020, 2024]

# Année cible pour les prédictions
TARGET_YEAR = 2028

# Types de médailles
MEDAL_TYPES = ["Gold", "Silver", "Bronze"]
MEDAL_WEIGHTS = {"Gold": 3, "Silver": 2, "Bronze": 1}

# =============================================================================
# PARAMÈTRES STREAMLIT
# =============================================================================

APP_CONFIG = {
    "page_title": "YPerf - Analyse JO 2028",
    "page_icon": "🏅",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Thème de couleurs
COLORS = {
    "gold": "#FFD700",
    "silver": "#C0C0C0",
    "bronze": "#CD7F32",
    "primary": "#1E88E5",
    "secondary": "#FFC107",
    "background": "#FAFAFA"
}

# =============================================================================
# PARAMÈTRES MACHINE LEARNING
# =============================================================================

ML_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "cv_folds": 5
}

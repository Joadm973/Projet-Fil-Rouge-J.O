"""Fixtures partagées pour la suite de tests YPerf."""
import sys
from pathlib import Path

import pandas as pd
import pytest

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

_COLUMNS = [
    "player_id", "Name", "Sex", "Team", "NOC", "Year",
    "Season", "City", "Sport", "Event", "Medal",
]

_ROWS = [
    # États-Unis — actifs, plusieurs éditions médaillées
    (1, "Athlete A", "M", "United States", "USA", 2012, "Summer", "London", "Swimming", "100m", "Gold"),
    (2, "Athlete B", "F", "United States", "USA", 2016, "Summer", "Rio", "Swimming", "100m", "Silver"),
    (3, "Athlete C", "M", "United States", "USA", 2020, "Summer", "Tokyo", "Swimming", "100m", "Bronze"),
    (4, "Athlete D", "M", "United States", "USA", 2024, "Summer", "Paris", "Swimming", "100m", "Gold"),
    # URSS — nation disparue, uniquement des éditions anciennes
    (5, "Athlete E", "M", "Soviet Union", "URS", 1980, "Summer", "Moscow", "Athletics", "100m", "Gold"),
    (6, "Athlete F", "M", "Soviet Union", "URS", 1988, "Summer", "Seoul", "Athletics", "100m", "Gold"),
    # NOC historiques à fusionner
    (7, "Athlete G", "M", "East Germany", "GDR", 1976, "Summer", "Montreal", "Rowing", "Eight", "Gold"),
    (8, "Athlete H", "M", "West Germany", "FRG", 1972, "Summer", "Munich", "Rowing", "Eight", "Silver"),
    (9, "Athlete I", "M", "ROC", "ROC", 2020, "Summer", "Tokyo", "Fencing", "Epee", "Gold"),
    (10, "Athlete J", "M", "Serbia and Montenegro", "SCG", 2004, "Summer", "Athens", "Water Polo", "Team", "Silver"),
    (11, "Athlete K", "M", "Bohemia", "BOH", 1900, "Summer", "Paris", "Tennis", "Singles", "Bronze"),
    # France — non-médaillé + édition d'hiver (doit être filtrée) + médailles récentes
    (12, "Athlete L", "F", "France", "FRA", 2016, "Summer", "Rio", "Judo", "-57kg", "No medal"),
    (13, "Athlete M", "M", "France", "FRA", 2018, "Winter", "PyeongChang", "Skiing", "Slalom", "Gold"),
    (14, "Athlete N", "F", "France", "FRA", 2012, "Summer", "London", "Judo", "-57kg", "Gold"),
    (15, "Athlete O", "F", "France", "FRA", 2020, "Summer", "Tokyo", "Judo", "-57kg", "Gold"),
    (16, "Athlete P", "F", "France", "FRA", 2024, "Summer", "Paris", "Judo", "-57kg", "Silver"),
    # Effectifs variés par (pays, édition) -> corrélation participation/médailles définie
    (17, "Athlete Q", "M", "United States", "USA", 2012, "Summer", "London", "Athletics", "200m", "Silver"),
    (18, "Athlete R", "F", "United States", "USA", 2024, "Summer", "Paris", "Gymnastics", "All-Around", "Gold"),
    (19, "Athlete S", "F", "France", "FRA", 2024, "Summer", "Paris", "Swimming", "200m", "Bronze"),
    # Variantes de nom d'équipe pour un même NOC (clubs 1904, embarcations "-1")
    (20, "Athlete T", "M", "Vesper Boat Club", "USA", 1904, "Summer", "St. Louis", "Rowing", "Eight", "Gold"),
    (21, "Athlete U", "M", "United States-1", "USA", 2012, "Summer", "London", "Tennis", "Doubles", "Bronze"),
]


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Mini-dataset synthétique couvrant tous les cas du nettoyage et du modèle.

    Contient volontairement : un doublon, une ligne d'hiver, des NOC historiques
    (GDR/FRG/ROC/SCG/BOH), une nation disparue (URS), des pays actifs et des
    variantes de nom d'équipe ("Vesper Boat Club", "United States-1").
    """
    df = pd.DataFrame(_ROWS, columns=_COLUMNS)
    # Ajoute un doublon exact (1re ligne) pour tester la déduplication.
    return pd.concat([df, df.iloc[[0]]], ignore_index=True)

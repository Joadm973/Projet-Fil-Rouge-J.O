"""Tests du nettoyage et de la préparation des données."""
from src.data.data_cleaner import clean_data, get_medals_df

MEDALS = ["Gold", "Silver", "Bronze"]


def test_only_summer_kept(sample_df):
    """clean_data ne conserve que les JO d'été."""
    out = clean_data(sample_df)
    assert (out["Season"] == "Summer").all()


def test_duplicates_removed(sample_df):
    """Le doublon injecté doit disparaître après nettoyage."""
    out = clean_data(sample_df)
    assert not out.duplicated().any()


def test_has_medal_flag_consistent(sample_df):
    """Has_Medal vaut 1 si et seulement si une médaille a été remportée."""
    out = clean_data(sample_df)
    assert set(out["Has_Medal"].unique()) <= {0, 1}
    assert (out.loc[out["Medal"].isin(MEDALS), "Has_Medal"] == 1).all()
    assert (out.loc[~out["Medal"].isin(MEDALS), "Has_Medal"] == 0).all()


def test_historical_nocs_merged(sample_df):
    """Les NOC historiques sont fusionnés vers leur équivalent moderne."""
    out = clean_data(sample_df)
    nocs = set(out["NOC"].unique())
    for old in ["GDR", "FRG", "ROC", "SCG", "BOH"]:
        assert old not in nocs, f"{old} aurait dû être fusionné"
    assert {"GER", "RUS", "SRB", "CZE"} <= nocs


def test_merged_team_renamed(sample_df):
    """Le nom d'équipe est harmonisé après fusion (ROC -> Russia)."""
    out = clean_data(sample_df)
    assert (out.loc[out["NOC"] == "RUS", "Team"] == "Russia").all()


def test_get_medals_df_only_medals(sample_df):
    """get_medals_df ne renvoie que des lignes médaillées."""
    medals = get_medals_df(clean_data(sample_df))
    assert medals["Medal"].isin(MEDALS).all()


def test_team_names_canonicalized(sample_df):
    """Chaque NOC n'a plus qu'un seul libellé d'équipe après nettoyage."""
    out = clean_data(sample_df)
    assert (out.groupby("NOC")["Team"].nunique() == 1).all()
    # Les clubs et suffixes d'embarcation sont ramenés au nom du pays.
    assert (out.loc[out["NOC"] == "USA", "Team"] == "United States").all()


def test_reversed_names_reordered(sample_df):
    """Les noms « NOM Prénom » des éditions 2020+ sont remis au format historique."""
    import pandas as pd

    extra = pd.DataFrame(
        [
            (40, "Emma Mckeon", "F", "Australia", "AUS", 2016, "Summer", "Rio", "Swimming", "100m", "Gold"),
            (41, "McKEON Emma", "F", "Australia", "AUS", 2020, "Summer", "Tokyo", "Swimming", "100m", "Gold"),
            # Nom entièrement en capitales : ordre indécidable, laissé tel quel.
            (42, "PREETI", "F", "India", "IND", 2024, "Summer", "Paris", "Boxing", "-54kg", "Bronze"),
        ],
        columns=sample_df.columns,
    )
    out = clean_data(pd.concat([sample_df, extra], ignore_index=True))
    names = set(out["Name"])
    assert "McKEON Emma" not in names
    assert "PREETI" in names
    # La carrière est réunifiée sous une seule identité.
    assert (out["Name"] == "Emma Mckeon").sum() == 2

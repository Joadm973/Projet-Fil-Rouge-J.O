"""Tests des indicateurs statistiques."""
from src.analysis import statistics as stx
from src.data.data_cleaner import clean_data


def test_gini_within_bounds(sample_df):
    """L'indice de Gini est borné dans [0, 1]."""
    gini = stx.medal_concentration_gini(clean_data(sample_df))
    assert 0.0 <= gini <= 1.0


def test_data_quality_report_columns(sample_df):
    """Le rapport qualité expose les colonnes attendues."""
    report = stx.data_quality_report(sample_df)
    assert {"dtype", "n_missing", "pct_missing", "n_unique"}.issubset(report.columns)


def test_weighted_score_positive(sample_df):
    """Tout pays médaillé a un score pondéré strictement positif."""
    score = stx.weighted_medal_score(clean_data(sample_df))
    assert (score["Score"] > 0).all()


def test_chi2_returns_expected_keys(sample_df):
    """Le test du χ² renvoie statistique, p-value et degrés de liberté."""
    res = stx.chi2_sex_medal(clean_data(sample_df))
    assert {"chi2", "p_value", "dof", "significant_5pct"}.issubset(res.keys())


def test_corr_participation_medals_range(sample_df):
    """Le coefficient de Pearson est borné dans [-1, 1]."""
    res = stx.corr_participation_medals(clean_data(sample_df))
    assert -1.0 <= res["pearson_r"] <= 1.0

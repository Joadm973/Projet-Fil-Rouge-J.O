"""Tests du modèle de prédiction et de l'évaluateur."""
from sklearn.linear_model import LinearRegression

from src.data.data_cleaner import clean_data
from src.models import evaluator as ev
from src.models.predictor import get_active_nocs, predict_medals_2028


def test_active_nocs_excludes_defunct(sample_df):
    """L'URSS (dernière participation 1988) n'est pas une nation active."""
    active = get_active_nocs(clean_data(sample_df))
    assert "URS" not in active
    assert "USA" in active


def test_predictions_exclude_defunct(sample_df):
    """Le classement 2028 ne doit contenir aucune nation disparue."""
    pred = predict_medals_2028(clean_data(sample_df))
    assert "URS" not in pred["NOC"].values
    assert "USA" in pred["NOC"].values


def test_predictions_non_negative(sample_df):
    """Aucune prédiction de médailles ne peut être négative."""
    pred = predict_medals_2028(clean_data(sample_df))
    assert (pred["Médailles prédites 2028"] >= 0).all()


def test_predict_columns(sample_df):
    """La structure de sortie est stable."""
    pred = predict_medals_2028(clean_data(sample_df))
    assert list(pred.columns) == ["NOC", "Pays", "Médailles prédites 2028"]


def test_regression_metrics_perfect_fit():
    """Une prédiction parfaite donne MAE=0 et R²=1."""
    y_true = [1, 2, 3, 4]
    metrics = ev.regression_metrics(y_true, y_true)
    assert metrics["MAE"] == 0
    assert metrics["R2"] == 1.0


def test_evaluate_models_on_country(sample_df):
    """L'évaluation multi-modèles renvoie les bonnes colonnes."""
    res = ev.evaluate_models_on_country(
        clean_data(sample_df), "United States", {"Linéaire": LinearRegression()}
    )
    assert not res.empty
    assert {"Modèle", "MAE", "RMSE", "R2", "Prédiction 2028"}.issubset(res.columns)

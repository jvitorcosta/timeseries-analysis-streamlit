import numpy as np
import pandas as pd
import pytest

from forecast_eval.core.benchmark import (
    add_hybrid,
    common_rows,
    error_cell_style,
    error_table,
    model_summaries,
)

MODELS = {"main": "forecast", "b": "b"}


@pytest.fixture
def scored() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "series": ["a"] * 4,
            "date": pd.date_range("2022-01-01", periods=4),
            "group": ["g"] * 4,
            "actual": [100.0] * 4,
            "forecast": [90.0] * 4,
            "b": [99.0, np.nan, np.nan, np.nan],
        }
    )


def test_models_are_scored_on_the_same_rows(scored: pd.DataFrame) -> None:
    summaries = model_summaries(scored, MODELS)
    assert summaries["main"].days == summaries["b"].days == 1
    assert summaries["main"].mape == pytest.approx(10.0)
    assert summaries["b"].mape == pytest.approx(1.0)


def test_common_rows_keep_only_complete_days(scored: pd.DataFrame) -> None:
    assert len(common_rows(scored, list(MODELS.values()))) == 1


def test_identical_forecasts_get_identical_scores(scored: pd.DataFrame) -> None:
    scored["b"] = [95.0, -1.0, 95.0, 95.0]
    scored["forecast"] = scored["b"]
    summaries = model_summaries(scored, MODELS)
    assert summaries["main"] == summaries["b"]


def test_hybrid_uses_each_series_chosen_model() -> None:
    frame = pd.DataFrame(
        {"series": ["a", "b"], "forecast": [1.0, 2.0], "x": [3.0, 4.0], "y": [5.0, 6.0]}
    )
    hybrid = add_hybrid(frame, {"a": "x", "b": "y"})
    assert hybrid["Hybrid"].tolist() == [3.0, 6.0]
    assert "Hybrid" not in frame.columns


def test_error_table_shows_signed_percentage_error(scored: pd.DataFrame) -> None:
    table = error_table(scored, MODELS, ["date", "series"])
    assert table["main error %"].tolist() == [10.0] * 4
    assert np.isnan(table["b error %"].iloc[1])


@pytest.mark.parametrize(
    ("value", "colour"),
    [
        (6.0, "lightcoral"),
        (-6.0, "khaki"),
        (5.0, "lightgreen"),
        (float("nan"), "lightgray"),
    ],
)
def test_error_cell_style(value: float, colour: str) -> None:
    assert colour in error_cell_style(value, tolerance=5)

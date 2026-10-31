import math
from datetime import date

import numpy as np
import pandas as pd
import pytest

from forecast_eval.core.aggregate import (
    filter_period,
    group_daily_totals,
    mape_by,
    rmse_by,
    summarize,
    tolerance_share_by,
)


def test_summarize_counts_days_and_zero_actuals(frame: pd.DataFrame) -> None:
    summary = summarize(frame[frame["series"] == "b"])
    assert summary.days == 3
    assert summary.zero_actual_days == 1
    assert summary.scored_days == 2
    assert summary.mape == pytest.approx(25.0)


def test_summarize_tolerance_uses_the_forecast_denominator(frame: pd.DataFrame) -> None:
    a = summarize(frame[frame["series"] == "a"])
    assert a.days_above(5) == 2
    assert a.share_above(5) == pytest.approx(200 / 3)
    assert a.days_above(20) == 0


def test_a_zero_forecast_that_misses_counts_as_above_tolerance() -> None:
    day = pd.DataFrame({"actual": [100.0], "forecast": [0.0]})
    assert summarize(day).days_above(5) == 1


def test_empty_summary_is_nan_not_a_crash() -> None:
    empty = pd.DataFrame({"actual": [], "forecast": []}, dtype=float)
    assert math.isnan(summarize(empty).share_above(5))


def test_tolerance_share_by_series(frame: pd.DataFrame) -> None:
    shares = tolerance_share_by(frame, "series", 5).set_index("series")["value"]
    assert shares["a"] == pytest.approx(200 / 3)
    assert shares["b"] == pytest.approx(200 / 3)


def test_mape_by_ignores_text_columns(frame: pd.DataFrame) -> None:
    values = mape_by(frame, "series").set_index("series")["value"]
    assert values["a"] == pytest.approx(20 / 3)
    assert values["b"] == pytest.approx(25.0)


def test_rmse_by_is_per_group_and_changes_with_the_rows(frame: pd.DataFrame) -> None:
    values = rmse_by(frame, "series").set_index("series")["value"]
    assert values["a"] == pytest.approx(math.sqrt(200 / 3))
    assert values["a"] != values["b"]


def test_group_totals_let_opposite_errors_net_out() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-01-01"] * 2),
            "group": ["g", "g"],
            "series": ["a", "b"],
            "actual": [100.0, 100.0],
            "forecast": [110.0, 90.0],
        }
    )
    totals = group_daily_totals(frame, ["forecast"])
    assert totals["actual"].tolist() == [200.0]
    assert totals["ape"].tolist() == [0.0]
    assert totals["deviation_pct"].tolist() == [0.0]


def test_group_totals_skip_rows_a_model_is_missing() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-01-01", "2022-01-01", "2022-01-02", "2022-01-02"]),
            "group": ["g"] * 4,
            "series": ["a", "b", "a", "b"],
            "actual": [100.0] * 4,
            "forecast": [100.0] * 4,
            "b": [100.0, np.nan, 100.0, 100.0],
        }
    )
    totals = group_daily_totals(frame, ["forecast", "b"])
    assert totals["actual"].tolist() == [100.0, 200.0]
    assert totals["b"].tolist() == [100.0, 200.0]


def test_filter_period_includes_both_ends(frame: pd.DataFrame) -> None:
    kept = filter_period(frame, date(2022, 3, 2), date(2022, 3, 3))
    assert sorted(kept["date"].dt.day.unique().tolist()) == [2, 3]

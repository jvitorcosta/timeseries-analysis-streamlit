import numpy as np
import pandas as pd
import pytest

from forecast_eval.core.residuals import correlogram, decompose
from forecast_eval.errors import InsufficientDataError


def daily(values: np.ndarray, start: str = "2022-01-01") -> pd.Series:
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="D"))


def weekly_pulse(days: int) -> pd.Series:
    rng = np.random.default_rng(1)
    return daily(np.where(np.arange(days) % 7 == 0, 10.0, 0.0) + rng.normal(0, 0.1, days))


def test_correlogram_reports_lags_from_one() -> None:
    result = correlogram(weekly_pulse(200))
    assert result.lags[0] == 1
    assert result.lags[-1] == 45
    assert len(result.values) == len(result.half_width) == len(result.lags)


def test_lags_are_days_even_with_missing_days() -> None:
    series = weekly_pulse(300)
    gappy = series[np.arange(len(series)) % 10 != 3]
    result = correlogram(gappy)
    assert result.values[6] > 0.8 > result.values[5]
    assert result.missing_days == len(series) - len(gappy)


def test_short_windows_cap_the_lags_for_pacf() -> None:
    result = correlogram(weekly_pulse(60), partial=True)
    assert result.lags[-1] == 29


def test_pacf_matches_the_ar1_coefficient() -> None:
    rng = np.random.default_rng(3)
    values = np.zeros(4000)
    for i in range(1, values.size):
        values[i] = 0.7 * values[i - 1] + rng.normal()
    result = correlogram(daily(values), partial=True)
    assert result.values[0] == pytest.approx(0.7, abs=0.05)
    assert abs(result.values[1]) < 0.1


def test_too_few_days_raises() -> None:
    with pytest.raises(InsufficientDataError):
        correlogram(daily(np.arange(3.0)))


def test_constant_series_raises() -> None:
    with pytest.raises(InsufficientDataError):
        correlogram(daily(np.ones(50)))


def test_decompose_reports_interpolated_days() -> None:
    series = weekly_pulse(60).drop(pd.Timestamp("2022-01-20"))
    result = decompose(series, period=7)
    assert result.interpolated_days == 1
    assert len(result.observed) == 60


def test_decompose_period_is_configurable() -> None:
    annual = daily(300 * np.sin(2 * np.pi * np.arange(1100) / 365))
    assert np.ptp(decompose(annual, period=7).seasonal) < 10
    assert np.ptp(decompose(annual, period=365).seasonal) > 400


def test_decompose_needs_two_full_periods() -> None:
    with pytest.raises(InsufficientDataError, match="14"):
        decompose(daily(np.arange(13.0)), period=7)

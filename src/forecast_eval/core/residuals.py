"""Seasonal decomposition and autocorrelation of one daily series."""

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import acf, levinson_durbin

from forecast_eval.config.settings import MAX_LAGS, Z_95
from forecast_eval.errors import InsufficientDataError

MIN_DAYS_FOR_CORRELATION = 8


@dataclass(frozen=True)
class Decomposition:
    observed: pd.Series
    trend: pd.Series
    seasonal: pd.Series
    residual: pd.Series
    period: int
    interpolated_days: int


@dataclass(frozen=True)
class Correlogram:
    lags: npt.NDArray[np.int64]
    values: npt.NDArray[np.float64]
    half_width: npt.NDArray[np.float64]
    missing_days: int


def _daily(series: pd.Series) -> pd.Series:
    return series.sort_index().asfreq("D")


def decompose(series: pd.Series, period: int = 7) -> Decomposition:
    """Additive classical decomposition. Missing days are filled by linear interpolation."""
    daily = _daily(series)
    if len(daily) < 2 * period:
        raise InsufficientDataError(f"Decomposition needs at least {2 * period} days.")
    filled = daily.interpolate(method="linear")
    result = seasonal_decompose(filled, model="additive", period=period)
    return Decomposition(
        observed=filled,
        trend=result.trend,
        seasonal=result.seasonal,
        residual=result.resid,
        period=period,
        interpolated_days=int(daily.isna().sum()),
    )


def correlogram(series: pd.Series, *, partial: bool = False) -> Correlogram:
    """ACF or PACF by calendar day, so lag 7 means seven days even with gaps."""
    daily = _daily(series)
    observed = int(daily.notna().sum())
    nlags = min(MAX_LAGS, len(daily) // 2 - 1)
    if observed < MIN_DAYS_FOR_CORRELATION or daily.std() == 0:
        raise InsufficientDataError(
            f"Autocorrelation needs at least {MIN_DAYS_FOR_CORRELATION} days that vary."
        )
    values, interval = acf(
        daily.to_numpy(), nlags=nlags, alpha=0.05, missing="conservative", result_object=False
    )
    half_width = interval[1:, 1] - values[1:]
    lags = np.arange(1, nlags + 1)
    missing_days = len(daily) - observed
    if not partial:
        return Correlogram(lags, values[1:], half_width, missing_days)
    partials = levinson_durbin(values, nlags=nlags, isacov=True)[2][1:]
    return Correlogram(lags, partials, np.full(nlags, Z_95 / np.sqrt(observed)), missing_days)

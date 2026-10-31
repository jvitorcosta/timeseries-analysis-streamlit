"""Forecast error metrics.

Everything takes actuals first, then forecasts. The error is always actual - forecast,
so a positive error is an under-forecast. Percentage errors divide by the actual and are
undefined (NaN) on a zero actual. `deviation_from_forecast_pct` is the one metric that
divides by the forecast: it measures tolerance against what was forecast.
"""

import numpy as np
import numpy.typing as npt

type Values = npt.ArrayLike
type FloatArray = npt.NDArray[np.float64]


def _as_float(values: Values) -> FloatArray:
    return np.asarray(values, dtype=np.float64)


def forecast_error(actual: Values, forecast: Values) -> FloatArray:
    return _as_float(actual) - _as_float(forecast)


def percentage_error(actual: Values, forecast: Values) -> FloatArray:
    """100 * (actual - forecast) / actual, NaN where the actual is zero."""
    y = _as_float(actual)
    error = forecast_error(y, forecast)
    return np.divide(100 * error, y, out=np.full_like(error, np.nan), where=y != 0)


def absolute_percentage_error(actual: Values, forecast: Values) -> FloatArray:
    return np.abs(percentage_error(actual, forecast))


def deviation_from_forecast_pct(actual: Values, forecast: Values) -> FloatArray:
    """100 * |actual - forecast| / |forecast|.

    A zero forecast that misses is an infinite deviation, and one that's right is zero, so
    every day with both values is defined and counts towards a tolerance share.
    """
    f = _as_float(forecast)
    gap = np.abs(forecast_error(actual, f))
    deviation = np.full_like(gap, np.inf)
    deviation[gap == 0] = 0.0
    deviation[np.isnan(gap)] = np.nan
    defined = f != 0
    deviation[defined] = 100 * gap[defined] / np.abs(f[defined])
    return deviation


def _nanmean(values: FloatArray) -> float:
    kept = values[~np.isnan(values)]
    return float(kept.mean()) if kept.size else float("nan")


def mape(actual: Values, forecast: Values) -> float:
    """Mean absolute percentage error over the days with a non-zero actual."""
    return _nanmean(absolute_percentage_error(actual, forecast))


def mpe(actual: Values, forecast: Values) -> float:
    """Mean percentage error. Positive means the forecast runs low."""
    return _nanmean(percentage_error(actual, forecast))


def rmse(actual: Values, forecast: Values) -> float:
    return float(np.sqrt(_nanmean(forecast_error(actual, forecast) ** 2)))


def standardized_residuals(errors: Values) -> FloatArray:
    """(e - mean) / sample std, all NaN when fewer than 3 values or no spread."""
    e = _as_float(errors)
    kept = e[~np.isnan(e)]
    if kept.size < 3 or kept.std(ddof=1) == 0:
        return np.full_like(e, np.nan)
    return (e - kept.mean()) / kept.std(ddof=1)

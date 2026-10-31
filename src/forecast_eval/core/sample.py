"""A seeded, fully synthetic dataset that exercises every view."""

import numpy as np
import pandas as pd

from forecast_eval.core.calendar import holidays_between
from forecast_eval.core.schema import ColumnMap

SEED = 2022
START = "2022-01-01"
DAYS = 730
OUTAGE_EVERY = 97
SERIES = {
    "site_a": ("north", 1500.0, 1.0, 0.00),
    "site_b": ("north", 820.0, 1.6, 0.03),
    "site_c": ("north", 310.0, 2.2, -0.02),
    "site_d": ("south", 2400.0, 0.8, 0.01),
    "site_e": ("south", 640.0, 1.8, -0.04),
    "site_f": ("south", 95.0, 3.0, 0.05),
}
SAMPLE_MAP = ColumnMap(
    series="series_id",
    date="date",
    actual="actual",
    forecast="forecast",
    group="zone",
    benchmarks=("seasonal_naive", "moving_average"),
)


def _one_series(
    name: str, zone: str, level: float, noise: float, bias: float, rng: np.random.Generator
) -> pd.DataFrame:
    dates = pd.date_range(START, periods=DAYS, freq="D")
    days = np.arange(DAYS)
    weekly = 1 + 0.12 * np.isin(dates.day_of_week, [0, 1, 2, 3, 4]) - 0.06
    yearly = 1 + 0.18 * np.cos(2 * np.pi * (days - 200) / 365)
    holidays = holidays_between(dates[0].date(), dates[-1].date())["date"]
    dip = np.where(dates.isin(holidays), 0.72, 1.0)
    signal = level * (1 + 0.0002 * days) * weekly * yearly
    actual = signal * dip * (1 + rng.normal(0, 0.02 * noise, DAYS))
    actual[days % OUTAGE_EVERY == OUTAGE_EVERY - 1] = 0.0
    # The forecast knows the seasonality but not the holidays, so they show up as misses.
    forecast = signal * (1 + bias) * (1 + rng.normal(0, 0.015 * noise, DAYS))
    series = pd.Series(actual)
    return pd.DataFrame(
        {
            "series_id": name,
            "date": dates.strftime("%Y-%m-%d"),
            "actual": actual.round(2),
            "forecast": forecast.round(2),
            "seasonal_naive": series.shift(7).round(2),
            "moving_average": series.rolling(28).mean().shift(1).round(2),
            "zone": zone,
        }
    )


def generate_sample() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    parts = [
        _one_series(name, zone, level, noise, bias, rng)
        for name, (zone, level, noise, bias) in SERIES.items()
    ]
    return pd.concat(parts, ignore_index=True)

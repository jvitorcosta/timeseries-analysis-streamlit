"""Summaries by series, group and period."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from forecast_eval.config.settings import TOLERANCES
from forecast_eval.core import metrics
from forecast_eval.core.preprocess import add_errors
from forecast_eval.core.schema import ACTUAL, DATE, DEVIATION, FORECAST, GROUP

VALUE = "value"


@dataclass(frozen=True)
class Summary:
    days: int
    zero_actual_days: int
    mape: float
    mpe: float
    rmse: float
    above: tuple[tuple[float, int], ...]

    @property
    def scored_days(self) -> int:
        """Days with a defined percentage error."""
        return self.days - self.zero_actual_days

    def days_above(self, tolerance: float) -> int:
        return dict(self.above)[tolerance]

    def share_above(self, tolerance: float) -> float:
        """Percentage of days above the tolerance, NaN with no days."""
        return 100 * self.days_above(tolerance) / self.days if self.days else float("nan")


def summarize(
    frame: pd.DataFrame, model: str = FORECAST, tolerances: Sequence[float] = TOLERANCES
) -> Summary:
    actual, forecast = frame[ACTUAL].to_numpy(), frame[model].to_numpy()
    deviation = metrics.deviation_from_forecast_pct(actual, forecast)
    return Summary(
        days=len(frame),
        zero_actual_days=int((actual == 0).sum()),
        mape=metrics.mape(actual, forecast),
        mpe=metrics.mpe(actual, forecast),
        rmse=metrics.rmse(actual, forecast),
        above=tuple((t, int((deviation > t).sum())) for t in tolerances),
    )


def _by(frame: pd.DataFrame, key: str, statistic: Callable[[pd.DataFrame], float]) -> pd.DataFrame:
    rows = [(name, statistic(part)) for name, part in frame.groupby(key, observed=True)]
    return pd.DataFrame(rows, columns=[key, VALUE])


def tolerance_share_by(frame: pd.DataFrame, key: str, tolerance: float) -> pd.DataFrame:
    """Percentage of rows per `key` with a deviation from forecast above the tolerance."""
    return _by(frame, key, lambda part: 100 * float(np.mean(part[DEVIATION] > tolerance)))


def mape_by(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    return _by(frame, key, lambda part: metrics.mape(part[ACTUAL], part[FORECAST]))


def rmse_by(frame: pd.DataFrame, key: str) -> pd.DataFrame:
    return _by(frame, key, lambda part: metrics.rmse(part[ACTUAL], part[FORECAST]))


def group_daily_totals(frame: pd.DataFrame, models: Sequence[str] = (FORECAST,)) -> pd.DataFrame:
    """Daily totals per group, over rows where every model has a forecast.

    Errors of opposite sign net out across a group's series, so this measures the group
    total, not its typical series. Error columns describe the first model.
    """
    columns = [ACTUAL, *models]
    complete = frame.dropna(subset=columns)
    totals = complete.groupby([DATE, GROUP], as_index=False, observed=True)[columns].sum()
    return add_errors(totals.reset_index(drop=True), models[0])


def filter_period(frame: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    days = frame[DATE].dt.date
    kept: pd.DataFrame = frame.loc[(days >= start) & (days <= end)].copy()
    return kept

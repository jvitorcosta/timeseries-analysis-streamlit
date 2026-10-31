"""Turn an uploaded table into the canonical frame every view works from."""

from dataclasses import dataclass

import numpy as np
import pandas as pd

from forecast_eval.core.metrics import (
    absolute_percentage_error,
    deviation_from_forecast_pct,
    forecast_error,
    percentage_error,
)
from forecast_eval.core.schema import (
    ACTUAL,
    APE,
    DATE,
    DEVIATION,
    ERROR,
    FORECAST,
    GROUP,
    PERCENTAGE_ERROR,
    SERIES,
    ColumnMap,
)
from forecast_eval.errors import ColumnMappingError

NO_GROUP = "(no group)"
ONE_GROUP = "all"


@dataclass(frozen=True)
class Prepared:
    frame: pd.DataFrame
    dropped_rows: int


def add_errors(frame: pd.DataFrame, model: str = FORECAST) -> pd.DataFrame:
    """A copy with error columns for `model`, which is scored exactly as given."""
    actual, forecast = frame[ACTUAL], frame[model]
    return frame.assign(
        **{
            ERROR: forecast_error(actual, forecast),
            PERCENTAGE_ERROR: percentage_error(actual, forecast),
            APE: absolute_percentage_error(actual, forecast),
            DEVIATION: deviation_from_forecast_pct(actual, forecast),
        }
    )


def _to_numeric(column: pd.Series, name: str) -> pd.Series:
    try:
        return pd.to_numeric(column).astype(float).replace([np.inf, -np.inf], np.nan)
    except (ValueError, TypeError) as err:
        raise ColumnMappingError(f"Column '{name}' must be numeric.") from err


def _to_dates(column: pd.Series, name: str) -> pd.Series:
    try:
        return pd.to_datetime(column, format="ISO8601").dt.normalize()
    except (ValueError, TypeError, AttributeError) as err:
        raise ColumnMappingError(f"Column '{name}' must hold ISO dates (YYYY-MM-DD).") from err


def prepare(raw: pd.DataFrame, mapping: ColumnMap) -> Prepared:
    mapping.validate(raw.columns.tolist())
    group = raw[mapping.group].astype("string").fillna(NO_GROUP) if mapping.group else ONE_GROUP
    frame = pd.DataFrame(
        {
            SERIES: raw[mapping.series],
            DATE: _to_dates(raw[mapping.date], mapping.date),
            ACTUAL: _to_numeric(raw[mapping.actual], mapping.actual),
            FORECAST: _to_numeric(raw[mapping.forecast], mapping.forecast),
            GROUP: group,
        }
    )
    for name, column in mapping.models.items():
        if column != FORECAST:
            frame[column] = _to_numeric(raw[name], name)

    complete = frame.dropna(subset=[SERIES, DATE, ACTUAL, FORECAST]).copy()
    if complete.empty:
        raise ColumnMappingError("No rows have a series, date, actual and forecast.")
    complete[SERIES] = complete[SERIES].astype(str)
    complete[GROUP] = complete[GROUP].astype(str)
    if complete.duplicated([SERIES, DATE]).any():
        raise ColumnMappingError("The file must have one row per series per day.")

    ordered = complete.sort_values([DATE, SERIES], ignore_index=True)
    return Prepared(add_errors(ordered), dropped_rows=len(frame) - len(complete))

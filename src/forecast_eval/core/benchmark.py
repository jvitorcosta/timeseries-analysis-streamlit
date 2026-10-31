"""Compare forecasts on equal terms: same rows, same metrics."""

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd

from forecast_eval.core.aggregate import Summary, summarize
from forecast_eval.core.metrics import percentage_error
from forecast_eval.core.schema import ACTUAL, HYBRID, SERIES


def common_rows(frame: pd.DataFrame, columns: Sequence[str]) -> pd.DataFrame:
    """Rows where every compared model has a forecast."""
    return frame.dropna(subset=list(columns))


def model_summaries(frame: pd.DataFrame, models: Mapping[str, str]) -> dict[str, Summary]:
    """Summary per model, all computed on the same rows."""
    rows = common_rows(frame, list(models.values()))
    return {name: summarize(rows, column) for name, column in models.items()}


def add_hybrid(frame: pd.DataFrame, choice: Mapping[str, str]) -> pd.DataFrame:
    """A copy with a Hybrid forecast that takes each series from its chosen column."""
    hybrid = pd.Series(np.nan, index=frame.index, dtype=float)
    for series, column in choice.items():
        mask = frame[SERIES] == series
        hybrid[mask] = frame.loc[mask, column]
    return frame.assign(**{HYBRID: hybrid})


def error_table(
    frame: pd.DataFrame, models: Mapping[str, str], keys: Sequence[str]
) -> pd.DataFrame:
    """Keys, actual, forecasts and each model's signed percentage error."""
    errors = {
        f"{name} error %": percentage_error(frame[ACTUAL], frame[column])
        for name, column in models.items()
    }
    forecasts = {name: frame[column] for name, column in models.items()}
    return frame[[*keys, ACTUAL]].assign(**errors, **forecasts)


def error_cell_style(value: float, tolerance: float) -> str:
    """Red for an under-forecast, yellow for an over-forecast, grey when undefined."""
    if np.isnan(value):
        colour = "lightgray"
    elif value > tolerance:
        colour = "lightcoral"
    elif value < -tolerance:
        colour = "khaki"
    else:
        colour = "lightgreen"
    return f"background-color: {colour}; color: black"

"""Several forecasts on one chart."""

from collections.abc import Mapping

import pandas as pd
import plotly.graph_objects as go

from forecast_eval.charts import theme
from forecast_eval.charts.series import tolerance_lines
from forecast_eval.core.metrics import percentage_error
from forecast_eval.core.schema import ACTUAL, DATE


def model_lines(frame: pd.DataFrame, models: Mapping[str, str]) -> go.Figure:
    fig = go.Figure()
    for colour, (name, column) in zip(theme.model_colours(), models.items(), strict=False):
        fig.add_scatter(x=frame[DATE], y=frame[column], name=name, line_color=colour)
    fig.add_scatter(
        x=frame[DATE], y=frame[ACTUAL], name="Actual", line={"color": theme.ACTUAL, "dash": "dash"}
    )
    return theme.style(fig, "Forecasts vs actual", "", "Value")


def model_errors(frame: pd.DataFrame, models: Mapping[str, str], tolerance: float) -> go.Figure:
    fig = go.Figure()
    for colour, (name, column) in zip(theme.model_colours(), models.items(), strict=False):
        fig.add_scatter(
            x=frame[DATE],
            y=percentage_error(frame[ACTUAL], frame[column]),
            mode="markers",
            name=name,
            marker_color=colour,
        )
    tolerance_lines(fig, tolerance)
    return theme.style(fig, "Daily percentage error", "", "100 * (actual - forecast) / actual")

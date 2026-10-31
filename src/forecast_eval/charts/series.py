"""Time-based charts for one series."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from forecast_eval.charts import theme
from forecast_eval.config.settings import Z_95
from forecast_eval.core.residuals import Correlogram, Decomposition
from forecast_eval.core.schema import ACTUAL, DATE, ERROR, FORECAST, PERCENTAGE_ERROR

_RANGE_BUTTONS = [
    {"count": 1, "label": "1m", "step": "month", "stepmode": "backward"},
    {"count": 3, "label": "3m", "step": "month", "stepmode": "backward"},
    {"count": 6, "label": "6m", "step": "month", "stepmode": "backward"},
    {"count": 1, "label": "1y", "step": "year", "stepmode": "backward"},
    {"step": "all"},
]


def tolerance_lines(fig: go.Figure, tolerance: float) -> None:
    for level in (tolerance, -tolerance):
        fig.add_hline(y=level, line_dash="dash", line_color=theme.TOLERANCE, line_width=1)


def actual_vs_forecast(frame: pd.DataFrame, model: str) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=frame[DATE], y=frame[ACTUAL], name="Actual", line_color=theme.ACTUAL)
    fig.add_scatter(x=frame[DATE], y=frame[FORECAST], name=model, line_color=theme.FORECAST)
    fig.add_scatter(x=frame[DATE], y=frame[ERROR], name="Error", line_color=theme.ERROR)
    fig.update_xaxes(rangeslider_visible=True, rangeselector={"buttons": _RANGE_BUTTONS})
    return theme.style(fig, "Actual vs forecast", "", "Value")


def error_series(frame: pd.DataFrame, column: str, name: str, *, band: bool = False) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=frame[DATE], y=frame[column], name=name, line_color=theme.MAPE)
    if band:
        fig.add_hrect(y0=-Z_95, y1=Z_95, fillcolor=theme.FORECAST, opacity=0.12, line_width=0)
    fig.add_hline(y=0, line_color=theme.ACTUAL, line_width=1)
    return theme.style(fig, name, "", f"{name} (actual - forecast)")


def percentage_error_scatter(frame: pd.DataFrame, tolerance: float) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(
        x=frame[DATE],
        y=frame[PERCENTAGE_ERROR],
        mode="markers",
        name="Percentage error",
        marker_color=theme.MAPE,
    )
    tolerance_lines(fig, tolerance)
    return theme.style(fig, "Daily percentage error", "", "100 * (actual - forecast) / actual")


def decomposition_chart(result: Decomposition, title: str) -> go.Figure:
    panels = {
        "Observed": result.observed,
        "Trend": result.trend,
        "Seasonal": result.seasonal,
        "Residual": result.residual,
    }
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=list(panels)
    )
    for row, (name, values) in enumerate(panels.items(), start=1):
        fig.add_scatter(x=values.index, y=values, name=name, row=row, col=1)
    fig.update_layout(title_text=title, showlegend=False, height=2 * theme.HEIGHT)
    return fig


def correlogram_chart(result: Correlogram, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(
        x=result.lags,
        y=result.half_width,
        name="upper",
        mode="lines",
        line_color="rgba(0,0,0,0)",
        hoverinfo="skip",
    )
    fig.add_scatter(
        x=result.lags,
        y=-result.half_width,
        name="lower",
        mode="lines",
        line_color="rgba(0,0,0,0)",
        fill="tonexty",
        fillcolor="rgba(32,146,230,0.25)",
        hoverinfo="skip",
    )
    stems_x = np.repeat(result.lags.astype(float), 3)
    stems_y = np.column_stack(
        (np.zeros_like(result.values), result.values, np.full_like(result.values, np.nan))
    ).ravel()
    stems_x[2::3] = np.nan
    fig.add_scatter(x=stems_x, y=stems_y, name="stem", mode="lines", line_color=theme.ERROR)
    fig.add_scatter(
        x=result.lags, y=result.values, name=title, mode="markers", marker_color=theme.MAPE
    )
    fig.update_layout(showlegend=False)
    return theme.style(fig, title, "Lag (days)", "Correlation")

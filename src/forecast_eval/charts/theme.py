"""Shared look of every chart."""

from itertools import cycle
from typing import Any

import plotly.graph_objects as go

ACTUAL = "#222222"
FORECAST = "#ea526f"
ERROR = "#8d8d8d"
MAPE = "#6e44ff"
RMSE = "#1fa9ac"
TOLERANCE = "#c42b2b"
MODELS = ("#d84797", "#06a77d", "#5158bb", "#de9e36", "#419797", "#c31f1f", "#6bab25")
HEIGHT = 420


def model_colours() -> Any:
    return cycle(MODELS)


def style(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    fig.update_layout(
        title_text=title,
        height=HEIGHT,
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode="x unified",
        legend_title_text="",
    )
    return fig

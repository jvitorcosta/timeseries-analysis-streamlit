"""Bars per series or group."""

import pandas as pd
import plotly.graph_objects as go

from forecast_eval.charts.theme import style
from forecast_eval.core.aggregate import VALUE


def bar_chart(
    frame: pd.DataFrame, key: str, title: str, y_title: str, colour: str, *, axis_title: str
) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=frame[key],
            y=frame[VALUE],
            marker_color=colour,
            texttemplate="%{y:.1f}",
            textposition="outside",
        )
    )
    fig.update_yaxes(rangemode="tozero")
    return style(fig, title, axis_title, y_title)

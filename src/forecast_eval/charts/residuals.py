"""Distributions of errors."""

import numpy as np
import numpy.typing as npt
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import gaussian_kde

from forecast_eval.charts.theme import ACTUAL, MAPE, TOLERANCE, style

KDE_POINTS = 200


def density(values: npt.NDArray[np.float64], name: str, title: str) -> go.Figure:
    """Histogram with a kernel density line when the data can support one."""
    finite = values[np.isfinite(values)]
    fig = go.Figure(
        go.Histogram(x=finite, histnorm="probability density", marker_color=MAPE, opacity=0.35)
    )
    fig.update_traces(name=name)
    if finite.size > 2 and np.ptp(finite) > 0:
        grid = np.linspace(finite.min(), finite.max(), KDE_POINTS)
        fig.add_scatter(x=grid, y=gaussian_kde(finite)(grid), line_color=ACTUAL, name="Density")
    fig.add_vline(x=0, line_width=1, line_dash="dash", line_color=TOLERANCE)
    return style(fig, title, name, "Density")


def box_by(frame: pd.DataFrame, x: str, y: str, title: str, y_title: str = "") -> go.Figure:
    fig = go.Figure(go.Box(x=frame[x], y=frame[y], boxmean=True, marker_color=MAPE))
    fig.update_traces(quartilemethod="exclusive")
    fig.update_xaxes(tickangle=-45)
    return style(fig, title, "", y_title)

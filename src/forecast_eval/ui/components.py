"""Widgets shared by the pages."""

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pandas.io.formats.style import Styler

from forecast_eval.config.settings import TOLERANCES
from forecast_eval.core.aggregate import Summary
from forecast_eval.core.schema import DATE

DEVIATION_NOTE = (
    "Days above tolerance use the deviation from forecast, which divides by the forecast: "
    "100 * |actual - forecast| / |forecast|."
)
MAPE_NOTE = "MAPE and MPE use the percentage error, which divides by the actual."
ERROR_NOTE = "Error is actual - forecast, so a positive error is an under-forecast."


def percent(value: float) -> str:
    return "n/a" if math.isnan(value) else f"{value:.2f}%"


def number(value: float) -> str:
    return "n/a" if math.isnan(value) else f"{value:,.2f}"


def chart(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, key=key)


def table(data: pd.DataFrame | Styler) -> None:
    dates = {DATE: st.column_config.DateColumn("date", format="YYYY-MM-DD")}
    st.dataframe(data, hide_index=True, column_config=dates)


def summary_metrics(summary: Summary, *, label: str | None = None) -> None:
    """One row of metrics. `label` names the model when several are compared."""
    leading = [label] if label else []
    columns = st.columns(len(leading) + 3 + len(TOLERANCES))
    cells = iter(columns)
    if label:
        next(cells).markdown(f"**{label}**")
    next(cells).metric("MAPE", percent(summary.mape))
    next(cells).metric("MPE", percent(summary.mpe))
    next(cells).metric("RMSE", number(summary.rmse))
    for tolerance in TOLERANCES:
        next(cells).metric(
            f"Days above {tolerance:g}%",
            percent(summary.share_above(tolerance)),
            delta=f"{summary.days_above(tolerance)} days",
            delta_color="off",
            delta_arrow="off",
        )


def zero_actual_note(summary: Summary) -> None:
    if summary.zero_actual_days:
        st.caption(
            f"{summary.zero_actual_days} of {summary.days} days have a zero actual, "
            "so they are left out of MAPE and MPE."
        )

"""Metrics page: where the forecast misses, per series and per group total."""

from collections.abc import Callable

import pandas as pd
import streamlit as st

from forecast_eval.charts import theme
from forecast_eval.charts.metrics import bar_chart
from forecast_eval.config.settings import TOLERANCES
from forecast_eval.core.aggregate import (
    group_daily_totals,
    mape_by,
    rmse_by,
    summarize,
    tolerance_share_by,
)
from forecast_eval.core.schema import GROUP, SERIES
from forecast_eval.ui.components import (
    DEVIATION_NOTE,
    ERROR_NOTE,
    MAPE_NOTE,
    chart,
    summary_metrics,
    zero_actual_note,
)

GROUP_NOTE = (
    "Group charts score the daily total of each group, so opposite errors in its series "
    "can net out. Series charts score each series on its own."
)


def _pair(
    frame: pd.DataFrame,
    totals: pd.DataFrame,
    statistic: Callable[[pd.DataFrame, str], pd.DataFrame],
    name: str,
    y_title: str,
    colour: str,
) -> None:
    chart(
        bar_chart(
            statistic(frame, SERIES),
            SERIES,
            f"{name} per series",
            y_title,
            colour,
            axis_title="Series",
        ),
        key=f"{name}_series",
    )
    chart(
        bar_chart(
            statistic(totals, GROUP),
            GROUP,
            f"{name} of group total",
            y_title,
            colour,
            axis_title="Group",
        ),
        key=f"{name}_group",
    )


def render(frame: pd.DataFrame, models: dict[str, str]) -> None:
    summary = summarize(frame)
    st.subheader(f"{next(iter(models))}: all series")
    summary_metrics(summary)
    zero_actual_note(summary)
    st.caption(f"{DEVIATION_NOTE} {MAPE_NOTE} {ERROR_NOTE}")
    st.caption(GROUP_NOTE)

    totals = group_daily_totals(frame)
    statistic = st.radio(
        "Statistic", ["Days above tolerance", "MAPE", "RMSE"], horizontal=True, key="statistic"
    )
    if statistic == "MAPE":
        _pair(frame, totals, mape_by, "MAPE", "MAPE (%)", theme.MAPE)
    elif statistic == "RMSE":
        _pair(frame, totals, rmse_by, "RMSE", "RMSE", theme.RMSE)
    else:
        tolerance = st.selectbox(
            "Tolerance (%)", TOLERANCES, format_func=lambda t: f"{t:g}%", key="tolerance"
        )
        _pair(
            frame,
            totals,
            lambda data, key: tolerance_share_by(data, key, tolerance),
            f"Days above {tolerance:g}%",
            "Share of days (%)",
            theme.FORECAST,
        )

"""Benchmark page: compare forecasts on the same rows."""

from collections.abc import Hashable
from functools import partial

import pandas as pd
import streamlit as st

from forecast_eval.charts.benchmark import model_errors, model_lines
from forecast_eval.config.settings import MAIN_TOLERANCE
from forecast_eval.core.aggregate import group_daily_totals
from forecast_eval.core.benchmark import (
    add_hybrid,
    common_rows,
    error_cell_style,
    error_table,
    model_summaries,
)
from forecast_eval.core.schema import DATE, GROUP, HYBRID, SERIES
from forecast_eval.ui.components import (
    ERROR_NOTE,
    chart,
    summary_metrics,
    table,
    zero_actual_note,
)

_MAX_STYLED_CELLS = 200_000


def _with_hybrid(
    frame: pd.DataFrame, models: dict[str, str]
) -> tuple[pd.DataFrame, dict[str, str]]:
    names = list(models)
    choice = {}
    with st.expander("Forecast per series"):
        for series in sorted(frame[SERIES].unique()):
            picked = st.selectbox(str(series), names, index=1, key=f"hybrid_{series}")
            choice[series] = models[picked]
    st.caption(
        "The hybrid is scored on the same data you pick it from, so it isn't evidence "
        "that the combination would do as well on new data."
    )
    return add_hybrid(frame, choice), {**models, HYBRID: HYBRID}


def _compare(rows: pd.DataFrame, models: dict[str, str], key: str) -> None:
    """Metric rows and charts for one set of rows that all models share."""
    summaries = model_summaries(rows, models)
    for name, summary in summaries.items():
        summary_metrics(summary, label=name)
    zero_actual_note(next(iter(summaries.values())))
    chart(model_lines(rows, models), key=f"{key}_lines")
    chart(model_errors(rows, models, MAIN_TOLERANCE), key=f"{key}_errors")


def _table(frame: pd.DataFrame, models: dict[str, str], keys: list[str]) -> None:
    rows = error_table(frame, models, keys)
    if rows.size > _MAX_STYLED_CELLS:
        table(rows)
        return
    errors: list[Hashable] = [c for c in rows.columns if c.endswith(" error %")]
    style = partial(error_cell_style, tolerance=MAIN_TOLERANCE)
    table(rows.style.map(style, subset=errors))


def render(frame: pd.DataFrame, models: dict[str, str]) -> None:
    if len(models) < 2:
        st.info("Map at least one benchmark forecast to compare models.")
        return
    if st.checkbox("Add a hybrid forecast", key="hybrid"):
        frame, models = _with_hybrid(frame, models)
    columns = list(models.values())

    groups = sorted(frame[GROUP].unique())
    group = st.selectbox("Group", groups, key="benchmark_group")
    in_group = frame[frame[GROUP] == group]
    shared = common_rows(in_group, columns)
    st.caption(
        f"Scored on the {len(shared)} of {len(in_group)} rows where every model has a forecast. "
        f"{ERROR_NOTE}"
    )
    if shared.empty:
        st.info("No rows in this window have a forecast from every model.")
        return

    with st.expander("Group total", expanded=True):
        st.caption("Daily totals of the group, so opposite errors in its series can net out.")
        _compare(group_daily_totals(shared, columns), models, "group")

    with st.expander("One series"):
        series = st.selectbox("Series", sorted(shared[SERIES].unique()), key="benchmark_series")
        _compare(shared[shared[SERIES] == series], models, "series")

    if st.checkbox("Show daily error tables", key="tables"):
        st.caption(
            f"Percentage error divides by the actual. Red is above +{MAIN_TOLERANCE:g}%, "
            f"yellow is below -{MAIN_TOLERANCE:g}%, grey is undefined."
        )
        _table(common_rows(frame, columns), models, [DATE, SERIES, GROUP])
        _table(group_daily_totals(frame, columns), models, [DATE, GROUP])

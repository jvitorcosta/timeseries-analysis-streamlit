"""Residuals page: one series in depth, then holidays across all series."""

import numpy as np
import pandas as pd
import streamlit as st

from forecast_eval.charts import theme
from forecast_eval.charts.metrics import bar_chart
from forecast_eval.charts.residuals import box_by, density
from forecast_eval.charts.series import (
    actual_vs_forecast,
    correlogram_chart,
    decomposition_chart,
    error_series,
    percentage_error_scatter,
)
from forecast_eval.config.settings import MAIN_TOLERANCE, SEASONAL_PERIODS
from forecast_eval.core.aggregate import rmse_by, summarize
from forecast_eval.core.calendar import (
    HOLIDAY,
    MONTH,
    WEEKDAY,
    add_calendar_parts,
    label_holidays,
)
from forecast_eval.core.metrics import standardized_residuals
from forecast_eval.core.residuals import correlogram, decompose
from forecast_eval.core.schema import (
    ACTUAL,
    APE,
    DATE,
    ERROR,
    FORECAST,
    GROUP,
    PERCENTAGE_ERROR,
    SERIES,
)
from forecast_eval.errors import InsufficientDataError
from forecast_eval.ui.components import ERROR_NOTE, chart, summary_metrics, zero_actual_note

STANDARDIZED = "standardized"
_WORST_DAYS = 20


def _decomposition(series: pd.DataFrame, name: str) -> None:
    column = st.selectbox(
        "Column", [ACTUAL, FORECAST, ERROR], key="decompose_column", format_func=str.capitalize
    )
    period = st.selectbox("Seasonal period (days)", SEASONAL_PERIODS, key="decompose_period")
    try:
        result = decompose(series.set_index(DATE)[column], period)
    except InsufficientDataError as err:
        st.info(str(err))
        return
    chart(decomposition_chart(result, f"Additive decomposition: {name}"), key="decomposition")
    st.caption(
        f"Seasonal period: {result.period} days, so longer cycles land in the trend. "
        f"Interpolated days: {result.interpolated_days}."
    )


def _error_series(series: pd.DataFrame) -> None:
    if st.checkbox("Standardized residuals", key="standardize"):
        z = series.assign(**{STANDARDIZED: standardized_residuals(series[ERROR])})
        if z[STANDARDIZED].isna().all():
            st.info("Standardized residuals need at least 3 days with different errors.")
            return
        st.caption("(error - mean) / standard deviation. The band marks +/-1.96.")
        chart(error_series(z, STANDARDIZED, "Standardized residual", band=True), key="z_series")
    else:
        chart(error_series(series, ERROR, "Error"), key="error_series")
    chart(percentage_error_scatter(series, MAIN_TOLERANCE), key="percentage_scatter")


def _by_calendar(parts: pd.DataFrame, column: str, label: str) -> None:
    chart(box_by(parts, MONTH, column, f"{label} by month", label), key=f"{column}_month")
    chart(box_by(parts, WEEKDAY, column, f"{label} by weekday", label), key=f"{column}_weekday")


def _autocorrelation(series: pd.DataFrame) -> None:
    partial = st.checkbox("Partial autocorrelation", key="partial")
    errors = series.set_index(DATE)[ERROR]
    name = "Partial autocorrelation" if partial else "Autocorrelation"
    for suffix, values, key in (
        ("errors", errors, "acf_error"),
        ("squared errors", errors**2, "acf_squared"),
    ):
        try:
            result = correlogram(values, partial=partial)
        except InsufficientDataError as err:
            st.info(str(err))
            return
        chart(correlogram_chart(result, f"{name} of {suffix}"), key=key)
    st.caption(f"Lags are calendar days. Missing days in the window: {result.missing_days}.")


def _mape_section(series: pd.DataFrame, parts: pd.DataFrame) -> None:
    st.subheader("MAPE by month and weekday")
    with st.expander("Percentage errors"):
        worst = series.nlargest(_WORST_DAYS, APE)[[DATE, ACTUAL, FORECAST, APE]]
        st.dataframe(worst, hide_index=True)
        chart(
            density(
                series[PERCENTAGE_ERROR].to_numpy(),
                "Percentage error",
                "Distribution of percentage error",
            ),
            key="percentage_density",
        )
        _by_calendar(parts, APE, "APE (%)")


def _rmse_section(parts: pd.DataFrame) -> None:
    st.subheader("RMSE by month and weekday")
    with st.expander("RMSE of the selected series and period"):
        for key, title in ((MONTH, "month"), (WEEKDAY, "weekday")):
            chart(
                bar_chart(
                    rmse_by(parts, key),
                    key,
                    f"RMSE by {title}",
                    "RMSE",
                    theme.RMSE,
                    axis_title=title.capitalize(),
                ),
                key=f"rmse_{key}",
            )


def _holidays(frame: pd.DataFrame) -> None:
    st.subheader("Holidays")
    labelled = label_holidays(frame)
    holidays = labelled[labelled[HOLIDAY].notna()]
    if holidays.empty:
        st.info("No holidays in this window.")
        return
    with st.expander("Error on holidays, all series"):
        st.caption(
            "Brazilian national holidays plus São Paulo state and city dates, for every series. "
            "(optional) marks days that aren't public holidays."
        )
        chart(box_by(holidays, HOLIDAY, APE, "APE on holidays", "APE (%)"), key="holidays")
        st.dataframe(holidays[[SERIES, DATE, HOLIDAY, APE]], hide_index=True)


def render(frame: pd.DataFrame, models: dict[str, str]) -> None:
    selected = st.selectbox("Series", sorted(frame[SERIES].unique()), key="series")
    series = frame[frame[SERIES] == selected]
    summary = summarize(series)
    st.subheader(f"{selected} ({series[GROUP].iloc[0]})")
    summary_metrics(summary)
    st.caption(f"{summary.days} days evaluated. {ERROR_NOTE}")
    zero_actual_note(summary)
    chart(actual_vs_forecast(series, next(iter(models))), key="actual_vs_forecast")

    with st.expander("Classical decomposition"):
        _decomposition(series, selected)

    parts = add_calendar_parts(series)
    st.subheader("Residuals")
    with st.expander("Over time"):
        _error_series(series)
    with st.expander("Distribution"):
        chart(density(np.asarray(series[ERROR]), "Error", "Distribution of error"), key="density")
        _by_calendar(parts, ERROR, "Error")
    with st.expander("Autocorrelation"):
        _autocorrelation(series)

    _mape_section(series, parts)
    _rmse_section(parts)
    _holidays(frame)

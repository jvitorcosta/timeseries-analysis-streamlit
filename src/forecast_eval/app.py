"""The Streamlit app."""

import streamlit as st

from forecast_eval.errors import ColumnMappingError
from forecast_eval.ui import benchmark, overview, residuals
from forecast_eval.ui.period import choose_period
from forecast_eval.ui.sidebar import Dataset, choose_dataset

PAGES = {"Metrics": overview.render, "Residuals": residuals.render, "Benchmark": benchmark.render}


def _dataset() -> Dataset | None:
    try:
        return choose_dataset()
    except ColumnMappingError as err:
        st.error(str(err))
        return None


def main() -> None:
    st.set_page_config(page_title="Forecast error analysis", page_icon="📈", layout="wide")
    st.title("Forecast error analysis")
    page = st.sidebar.radio("Page", list(PAGES), key="page")
    dataset = _dataset()
    if dataset is None:
        return
    if dataset.dropped_rows:
        st.caption(f"{dataset.dropped_rows} rows without an actual or forecast were left out.")
    frame = choose_period(dataset.frame)
    PAGES[page](frame, dataset.models)

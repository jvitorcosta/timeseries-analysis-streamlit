"""Choose the data: the bundled sample, or an uploaded CSV with a column mapping."""

from dataclasses import dataclass
from importlib import resources
from io import BytesIO

import pandas as pd
import streamlit as st

from forecast_eval.config.settings import CACHE_TTL_SECONDS
from forecast_eval.core.preprocess import prepare
from forecast_eval.core.sample import SAMPLE_MAP
from forecast_eval.core.schema import ACTUAL, DATE, FORECAST, GROUP, SERIES, ColumnMap, guess_column
from forecast_eval.errors import ColumnMappingError

SAMPLE = "Sample data"
UPLOAD = "Upload a CSV"
NO_COLUMN = "(none)"
_MAX_CACHED_UPLOADS = 4


@dataclass(frozen=True)
class Dataset:
    frame: pd.DataFrame
    models: dict[str, str]
    dropped_rows: int


@st.cache_data
def _sample_csv() -> bytes:
    path = resources.files("forecast_eval") / "resources" / "sample_forecasts.csv"
    return path.read_bytes()


@st.cache_data(ttl=CACHE_TTL_SECONDS, max_entries=_MAX_CACHED_UPLOADS)
def _read_csv(content: bytes) -> pd.DataFrame:
    try:
        return pd.read_csv(BytesIO(content))
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as err:
        raise ColumnMappingError("This file can't be read as a CSV.") from err


@st.cache_data(ttl=CACHE_TTL_SECONDS, max_entries=_MAX_CACHED_UPLOADS)
def _load(content: bytes, mapping: ColumnMap) -> Dataset:
    prepared = prepare(_read_csv(content), mapping)
    return Dataset(prepared.frame, mapping.models, prepared.dropped_rows)


def _pick(label: str, role: str, columns: list[str]) -> str | None:
    guess = guess_column(columns, role)
    index = columns.index(guess) if guess else None
    return st.selectbox(label, columns, index=index, key=f"map_{role}", placeholder="Choose")


def _mapping(columns: list[str]) -> ColumnMap | None:
    series = _pick("Series id", SERIES, columns)
    day = _pick("Date", DATE, columns)
    actual = _pick("Actual", ACTUAL, columns)
    forecast = _pick("Forecast to evaluate", FORECAST, columns)
    group = st.selectbox(
        "Group (optional)",
        [NO_COLUMN, *columns],
        index=columns.index(guess) + 1 if (guess := guess_column(columns, GROUP)) else 0,
        key="map_group",
    )
    benchmarks = st.multiselect("Benchmark forecasts", columns, key="map_benchmarks")
    if series is None or day is None or actual is None or forecast is None:
        return None
    return ColumnMap(
        series=series,
        date=day,
        actual=actual,
        forecast=forecast,
        group=None if group == NO_COLUMN else group,
        benchmarks=tuple(benchmarks),
    )


def choose_dataset() -> Dataset | None:
    """The dataset to analyse, or None while an upload is incomplete."""
    source = st.sidebar.radio("Data source", [SAMPLE, UPLOAD], key="source")
    if source == SAMPLE:
        st.sidebar.download_button(
            "Download the sample CSV",
            _sample_csv(),
            file_name="sample_forecasts.csv",
            mime="text/csv",
        )
        return _load(_sample_csv(), SAMPLE_MAP)

    upload = st.sidebar.file_uploader("CSV file", type=["csv"], key="upload")
    if upload is None:
        st.info("Upload a CSV with one row per series per day.")
        return None
    content = upload.getvalue()
    with st.sidebar.expander("Column mapping", expanded=True):
        mapping = _mapping(_read_csv(content).columns.astype(str).tolist())
    if mapping is None:
        st.info("Choose the series, date, actual and forecast columns in the sidebar.")
        return None
    return _load(content, mapping)

import math

import numpy as np
import pandas as pd
import pytest

from forecast_eval.core.preprocess import prepare
from forecast_eval.core.schema import ColumnMap
from forecast_eval.errors import ColumnMappingError


def test_prepare_uses_canonical_columns_sorted_by_date(frame: pd.DataFrame) -> None:
    assert frame.columns[:5].tolist() == ["series", "date", "actual", "forecast", "group"]
    assert frame["date"].is_monotonic_increasing
    assert pd.api.types.is_datetime64_any_dtype(frame["date"])


def test_prepare_does_not_change_its_input(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    before = raw.copy()
    prepare(raw, mapping)
    pd.testing.assert_frame_equal(raw, before)


def test_error_is_actual_minus_forecast_as_given(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    raw.loc[0, "f"] = -5.0
    frame = prepare(raw, mapping).frame
    row = frame[(frame["series"] == "a") & (frame["date"] == "2022-03-03")].iloc[0]
    assert row["forecast"] == -5.0
    assert row["error"] == 105.0
    assert row["ape"] == pytest.approx(105.0)


def test_zero_actual_is_undefined_for_ape_but_not_for_deviation(frame: pd.DataFrame) -> None:
    row = frame[(frame["series"] == "b") & (frame["actual"] == 0)].iloc[0]
    assert math.isnan(row["ape"])
    assert row["deviation_pct"] == pytest.approx(100.0)


def test_rows_without_actual_or_forecast_are_counted(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    raw.loc[0, "y"] = np.nan
    raw.loc[1, "f"] = np.nan
    prepared = prepare(raw, mapping)
    assert len(prepared.frame) == 4
    assert prepared.dropped_rows == 2


def test_missing_group_gets_a_visible_label(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    raw.loc[0, "zone"] = None
    assert "(no group)" in prepare(raw, mapping).frame["group"].tolist()


def test_no_group_column_means_one_group(raw: pd.DataFrame) -> None:
    mapping = ColumnMap(series="id", date="day", actual="y", forecast="f")
    assert prepare(raw, mapping).frame["group"].nunique() == 1


def test_benchmark_gaps_are_kept(raw: pd.DataFrame) -> None:
    raw["b"] = [1.0, np.nan, 3.0, 4.0, 5.0, 6.0]
    mapping = ColumnMap(series="id", date="day", actual="y", forecast="f", benchmarks=("b",))
    assert prepare(raw, mapping).frame["b"].isna().sum() == 1


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [("day", "not a date", "ISO dates"), ("y", "abc", "numeric"), ("f", "abc", "numeric")],
)
def test_unparseable_column_is_a_mapping_error(
    raw: pd.DataFrame, mapping: ColumnMap, column: str, value: str, message: str
) -> None:
    raw[column] = raw[column].astype(object)
    raw.loc[0, column] = value
    with pytest.raises(ColumnMappingError, match=message):
        prepare(raw, mapping)


def test_two_rows_for_one_series_and_day_is_a_mapping_error(
    raw: pd.DataFrame, mapping: ColumnMap
) -> None:
    raw["id"] = "same"
    with pytest.raises(ColumnMappingError, match="one row per series per day"):
        prepare(raw, mapping)


def test_no_usable_rows_is_a_mapping_error(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    raw["y"] = np.nan
    with pytest.raises(ColumnMappingError, match="No rows"):
        prepare(raw, mapping)


def test_timezones_are_dropped_from_dates(raw: pd.DataFrame, mapping: ColumnMap) -> None:
    raw["day"] = raw["day"] + "T00:00:00Z"
    assert prepare(raw, mapping).frame["date"].dt.tz is None

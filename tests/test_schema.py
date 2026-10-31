import pytest

from forecast_eval.core.schema import ColumnMap, guess_column
from forecast_eval.errors import ColumnMappingError

COLUMNS = ["id", "day", "y", "f", "zone", "other"]


@pytest.mark.parametrize(
    ("columns", "role", "expected"),
    [
        (["series_id", "date", "actual"], "series", "series_id"),
        (["Date", "x"], "date", "Date"),
        (["x", "Actual"], "actual", "Actual"),
        (["yhat", "x"], "forecast", "yhat"),
        (["zone", "x"], "group", "zone"),
        (["a", "b"], "date", None),
    ],
)
def test_guess_column(columns: list[str], role: str, expected: str | None) -> None:
    assert guess_column(columns, role) == expected


def test_valid_mapping_passes(mapping: ColumnMap) -> None:
    mapping.validate(COLUMNS)


def test_same_column_for_two_roles_is_rejected() -> None:
    bad = ColumnMap(series="id", date="id", actual="y", forecast="f")
    with pytest.raises(ColumnMappingError, match="more than one role"):
        bad.validate(COLUMNS)


def test_missing_column_is_rejected() -> None:
    bad = ColumnMap(series="nope", date="day", actual="y", forecast="f")
    with pytest.raises(ColumnMappingError, match="nope"):
        bad.validate(COLUMNS)


def test_reserved_benchmark_name_is_rejected() -> None:
    bad = ColumnMap(series="id", date="day", actual="y", forecast="f", benchmarks=("error",))
    with pytest.raises(ColumnMappingError, match="error"):
        bad.validate([*COLUMNS, "error"])


def test_models_list_the_forecast_first_without_repeats() -> None:
    mapping = ColumnMap(series="id", date="day", actual="y", forecast="f", benchmarks=("f", "b"))
    assert mapping.models == {"f": "forecast", "b": "b"}

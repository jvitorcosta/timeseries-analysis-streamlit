import pandas as pd
import pytest

from forecast_eval.core.preprocess import prepare
from forecast_eval.core.schema import ColumnMap


@pytest.fixture
def mapping() -> ColumnMap:
    return ColumnMap(series="id", date="day", actual="y", forecast="f", group="zone")


@pytest.fixture
def raw() -> pd.DataFrame:
    """Two series over three days, in file order rather than date order."""
    return pd.DataFrame(
        {
            "id": ["a", "a", "a", "b", "b", "b"],
            "day": ["2022-03-03", "2022-03-01", "2022-03-02"] * 2,
            "y": [100.0, 100.0, 100.0, 200.0, 200.0, 0.0],
            "f": [90.0, 110.0, 100.0, 200.0, 100.0, 50.0],
            "zone": ["north"] * 6,
        }
    )


@pytest.fixture
def frame(raw: pd.DataFrame, mapping: ColumnMap) -> pd.DataFrame:
    return prepare(raw, mapping).frame

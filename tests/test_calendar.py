from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from forecast_eval.core.calendar import add_calendar_parts, holidays_between, label_holidays

GOLDEN = Path(__file__).parent / "golden" / "holidays_1995_2030.txt"


def test_dates_match_the_original_calendar() -> None:
    expected = GOLDEN.read_text().split()
    found = holidays_between(date(1995, 1, 1), date(2030, 12, 31))
    assert found["date"].dt.strftime("%Y-%m-%d").tolist() == expected


@pytest.mark.parametrize(
    ("day", "name"),
    [
        ("2022-02-28", "Carnival Monday (optional)"),
        ("2022-03-01", "Carnival Tuesday"),
        ("2022-03-02", "Ash Wednesday (optional)"),
        ("2022-04-15", "Good Friday"),
        ("2022-06-16", "Corpus Christi"),
        ("2024-02-13", "Carnival Tuesday"),
        ("2024-05-30", "Corpus Christi"),
        ("2022-12-24", "Christmas Eve (optional)"),
    ],
)
def test_holiday_names(day: str, name: str) -> None:
    found = holidays_between(date(2022, 1, 1), date(2024, 12, 31)).set_index("date")
    assert found.loc[pd.Timestamp(day), "holiday"] == name


def test_two_holidays_on_one_date_share_a_row() -> None:
    found = holidays_between(date(2000, 4, 21), date(2000, 4, 21))
    assert found["holiday"].tolist() == ["Good Friday / Tiradentes"]


def test_a_range_with_no_holiday_is_empty() -> None:
    assert holidays_between(date(2022, 8, 10), date(2022, 8, 11)).empty


@pytest.mark.parametrize(
    ("day", "expected"),
    [("1996-07-09", 0), ("1997-07-09", 1), ("2003-11-20", 0), ("2004-11-20", 1)],
)
def test_rules_start_in_their_first_year(day: str, expected: int) -> None:
    moment = date.fromisoformat(day)
    assert len(holidays_between(moment, moment)) == expected


def test_label_holidays_does_not_add_rows() -> None:
    frame = pd.DataFrame({"date": pd.to_datetime(["2000-04-21", "2000-04-22"]), "x": [1, 2]})
    labelled = label_holidays(frame)
    assert len(labelled) == 2
    assert labelled["holiday"].notna().tolist() == [True, False]


def test_calendar_parts_keep_calendar_order() -> None:
    frame = pd.DataFrame({"date": pd.to_datetime(["2022-12-05", "2022-01-02"])})
    parts = add_calendar_parts(frame)
    assert parts["month"].sort_values().astype(str).tolist() == ["January", "December"]
    assert parts["weekday"].astype(str).tolist() == ["Monday", "Sunday"]

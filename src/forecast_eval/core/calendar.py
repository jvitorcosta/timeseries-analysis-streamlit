"""Month and weekday labels, and a Brazilian holiday calendar for São Paulo.

Dates cover national holidays plus São Paulo state and city ones, applied to every series.
"(optional)" marks days that aren't public holidays but usually change demand.
"""

from calendar import day_name, month_name
from datetime import date

import pandas as pd
from pandas.tseries.holiday import AbstractHolidayCalendar, Holiday
from pandas.tseries.offsets import Day, Easter

from forecast_eval.core.schema import DATE

HOLIDAY = "holiday"
MONTH = "month"
WEEKDAY = "weekday"
MONTHS = list(month_name)[1:]
WEEKDAYS = list(day_name)


def _easter(name: str, days: int) -> Holiday:
    return Holiday(name, month=1, day=1, offset=[Easter(), Day(days)])


class SaoPauloCalendar(AbstractHolidayCalendar):
    rules = [  # noqa: RUF012 - pandas declares rules as a mutable class attribute
        Holiday("New Year's Day", month=1, day=1),
        Holiday("São Paulo Anniversary", month=1, day=25),
        _easter("Carnival Monday (optional)", -48),
        _easter("Carnival Tuesday", -47),
        _easter("Ash Wednesday (optional)", -46),
        _easter("Good Friday", -2),
        _easter("Corpus Christi", 60),
        Holiday("Tiradentes", month=4, day=21),
        Holiday("Labour Day", month=5, day=1),
        Holiday("Constitutionalist Revolution", month=7, day=9, start_date="1997-01-01"),
        Holiday("Independence Day", month=9, day=7),
        Holiday("Our Lady of Aparecida", month=10, day=12),
        Holiday("All Souls' Day", month=11, day=2),
        Holiday("Republic Day", month=11, day=15),
        Holiday("Black Awareness Day", month=11, day=20, start_date="2004-01-01"),
        Holiday("Christmas Eve (optional)", month=12, day=24),
        Holiday("Christmas Day", month=12, day=25),
    ]


def holidays_between(start: date, end: date) -> pd.DataFrame:
    """One row per date, sorted, with names joined when two holidays share a date."""
    named = SaoPauloCalendar().holidays(start, end, return_name=True)
    names = named.groupby(level=0).agg(lambda day: " / ".join(sorted(day)))
    return pd.DataFrame({DATE: names.index, HOLIDAY: names.to_numpy(dtype=object)})


def label_holidays(frame: pd.DataFrame) -> pd.DataFrame:
    """A copy with the holiday name of each row, NaN on ordinary days."""
    holidays = holidays_between(frame[DATE].min().date(), frame[DATE].max().date())
    return frame.merge(holidays, on=DATE, how="left")


def add_calendar_parts(frame: pd.DataFrame) -> pd.DataFrame:
    """A copy with ordered month and weekday columns, so charts sort by the calendar."""
    months = pd.Categorical(frame[DATE].dt.month_name(), categories=MONTHS, ordered=True)
    weekdays = pd.Categorical(frame[DATE].dt.day_name(), categories=WEEKDAYS, ordered=True)
    return frame.assign(**{MONTH: months, WEEKDAY: weekdays})

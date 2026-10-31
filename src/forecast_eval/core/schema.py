"""Which input column plays which role, and the canonical names used after that."""

from collections.abc import Sequence
from dataclasses import dataclass

from forecast_eval.errors import ColumnMappingError

SERIES = "series"
DATE = "date"
ACTUAL = "actual"
FORECAST = "forecast"
GROUP = "group"
ERROR = "error"
APE = "ape"
PERCENTAGE_ERROR = "percentage_error"
DEVIATION = "deviation_pct"

RESERVED = frozenset(
    {SERIES, DATE, ACTUAL, FORECAST, GROUP, ERROR, APE, PERCENTAGE_ERROR, DEVIATION}
)

_GUESSES = {
    SERIES: ("series_id", "series", "id", "item", "site"),
    DATE: ("date", "ds", "day", "timestamp"),
    ACTUAL: ("actual", "y", "observed", "real"),
    FORECAST: ("forecast", "yhat", "predicted", "prediction"),
    GROUP: ("group", "zone", "class", "category"),
}


def guess_column(columns: Sequence[str], role: str) -> str | None:
    """The first column whose lowercase name is a known name for the role."""
    by_name = {column.lower(): column for column in columns}
    return next((by_name[name] for name in _GUESSES[role] if name in by_name), None)


@dataclass(frozen=True)
class ColumnMap:
    series: str
    date: str
    actual: str
    forecast: str
    group: str | None = None
    benchmarks: tuple[str, ...] = ()

    @property
    def models(self) -> dict[str, str]:
        """Display name to canonical column, the evaluated forecast first."""
        others = {name: name for name in self.benchmarks if name != self.forecast}
        return {self.forecast: FORECAST, **others}

    def validate(self, columns: Sequence[str]) -> None:
        roles = [self.series, self.date, self.actual, self.forecast]
        if self.group is not None:
            roles.append(self.group)
        if len(set(roles)) < len(roles):
            raise ColumnMappingError("A column can't play more than one role.")
        missing = [name for name in (*roles, *self.benchmarks) if name not in columns]
        if missing:
            raise ColumnMappingError(f"Columns not in the file: {', '.join(missing)}.")
        reserved = (set(self.models) - {self.forecast}) & (RESERVED | set(roles))
        if reserved:
            names = ", ".join(sorted(reserved))
            raise ColumnMappingError(f"Rename or remove these benchmark columns: {names}.")

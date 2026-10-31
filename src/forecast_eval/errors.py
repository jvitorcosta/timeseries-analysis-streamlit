"""Errors the app reports to the user."""


class ForecastEvalError(Exception):
    """Base class for expected failures."""


class ColumnMappingError(ForecastEvalError):
    """The chosen columns can't be evaluated as a forecast."""


class InsufficientDataError(ForecastEvalError):
    """Too little data for this analysis in the chosen window."""

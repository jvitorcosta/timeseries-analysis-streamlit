import math

import numpy as np
import pytest

from forecast_eval.core.metrics import (
    absolute_percentage_error,
    deviation_from_forecast_pct,
    forecast_error,
    mape,
    mpe,
    percentage_error,
    rmse,
    standardized_residuals,
)


def arr(*values: float) -> np.ndarray:
    return np.array(values, dtype=float)


@pytest.mark.parametrize(
    ("actual", "forecast", "expected"),
    [(100, 50, 50.0), (100, 200, 100.0), (100, 80, 20.0)],
)
def test_ape_divides_by_the_actual(actual: float, forecast: float, expected: float) -> None:
    assert absolute_percentage_error(arr(actual), arr(forecast))[0] == pytest.approx(expected)


def test_error_is_actual_minus_forecast() -> None:
    assert forecast_error(arr(100), arr(80))[0] == 20


def test_percentage_error_has_the_same_sign_as_the_error() -> None:
    assert percentage_error(arr(100), arr(80))[0] == pytest.approx(20.0)
    assert percentage_error(arr(100), arr(120))[0] == pytest.approx(-20.0)


def test_percentage_error_is_undefined_on_a_zero_actual() -> None:
    assert math.isnan(percentage_error(arr(0), arr(50))[0])


def test_ape_keeps_values_above_100() -> None:
    assert absolute_percentage_error(arr(100), arr(1000))[0] == pytest.approx(900.0)


def test_negative_forecast_is_scored_as_given() -> None:
    assert absolute_percentage_error(arr(100), arr(-5))[0] == pytest.approx(105.0)


def test_mape_skips_zero_actuals() -> None:
    assert mape(arr(100, 0, 100), arr(90, 50, 80)) == pytest.approx(15.0)


def test_mape_of_only_zero_actuals_is_nan() -> None:
    assert math.isnan(mape(arr(0, 0), arr(1, 2)))


def test_over_forecasting_is_not_rewarded() -> None:
    actual = arr(100, 100)
    assert mape(actual, arr(120, 120)) == mape(actual, arr(80, 80))


def test_mpe_shows_bias_with_error_sign() -> None:
    assert mpe(arr(100, 100), arr(90, 90)) == pytest.approx(10.0)


def test_rmse_ignores_missing_pairs() -> None:
    assert rmse(arr(1, 2, np.nan), arr(1, 4, 3)) == pytest.approx(math.sqrt(2))


def test_rmse_with_no_pairs_is_nan_not_zero() -> None:
    assert math.isnan(rmse(arr(np.nan), arr(1)))


def test_mismatched_lengths_raise() -> None:
    with pytest.raises(ValueError, match="broadcast"):
        rmse(arr(1, 2), arr(1, 2, 3))


def test_deviation_divides_by_the_forecast() -> None:
    assert deviation_from_forecast_pct(arr(100), arr(95))[0] == pytest.approx(5.2631578)


def test_deviation_is_infinite_when_a_zero_forecast_misses() -> None:
    assert deviation_from_forecast_pct(arr(100), arr(0))[0] == math.inf


def test_deviation_is_zero_when_zero_is_forecast_correctly() -> None:
    assert deviation_from_forecast_pct(arr(0), arr(0))[0] == 0


def test_deviation_uses_the_forecast_magnitude() -> None:
    assert deviation_from_forecast_pct(arr(5), arr(-5))[0] == pytest.approx(200.0)


def test_deviation_propagates_missing_values() -> None:
    assert math.isnan(deviation_from_forecast_pct(arr(np.nan), arr(1))[0])


def test_standardized_residuals_are_centred() -> None:
    z = standardized_residuals(arr(10, 12, 8, 10))
    assert z.mean() == pytest.approx(0)
    assert z.std(ddof=1) == pytest.approx(1)


def test_standardized_residuals_reveal_a_day_against_a_constant_bias() -> None:
    errors = np.array([10.0] * 49 + [25.0])
    assert standardized_residuals(errors)[-1] > 1.96


def test_standardized_residuals_ignore_missing_values() -> None:
    z = standardized_residuals(arr(1, 2, np.nan, 3))
    assert math.isnan(z[2])
    assert z[1] == pytest.approx(0)


@pytest.mark.parametrize("errors", [[1.0], [1.0, 2.0], [3.0, 3.0, 3.0]])
def test_standardized_residuals_undefined_cases_are_nan(errors: list[float]) -> None:
    assert np.isnan(standardized_residuals(np.array(errors))).all()

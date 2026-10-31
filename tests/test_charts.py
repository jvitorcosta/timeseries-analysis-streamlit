import ast
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forecast_eval.charts.benchmark import model_errors, model_lines
from forecast_eval.charts.metrics import bar_chart
from forecast_eval.charts.residuals import box_by, density
from forecast_eval.charts.series import (
    actual_vs_forecast,
    correlogram_chart,
    decomposition_chart,
    error_series,
    percentage_error_scatter,
)
from forecast_eval.core.residuals import correlogram, decompose

SRC = Path(__file__).parents[1] / "src" / "forecast_eval"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.parametrize("path", [*SRC.glob("core/*.py"), *SRC.glob("charts/*.py")], ids=str)
def test_pure_layers_do_not_import_streamlit(path: Path) -> None:
    assert "streamlit" not in _imports(path)


def daily(days: int = 60) -> pd.Series:
    rng = np.random.default_rng(0)
    return pd.Series(rng.normal(size=days), index=pd.date_range("2022-01-01", periods=days))


def test_correlogram_band_is_drawn_at_its_own_lags() -> None:
    result = correlogram(daily())
    fig = correlogram_chart(result, "Autocorrelation")
    band = next(trace for trace in fig.data if trace.name == "upper")
    assert band.x.tolist() == result.lags.tolist()
    assert band.y.tolist() == pytest.approx(result.half_width.tolist())


def test_correlogram_has_a_title() -> None:
    fig = correlogram_chart(correlogram(daily()), "Partial autocorrelation")
    assert fig.layout.title.text == "Partial autocorrelation"


def test_decomposition_has_four_panels() -> None:
    assert len(decomposition_chart(decompose(daily()), "site_a").data) == 4


def test_density_handles_a_single_value() -> None:
    assert len(density(np.array([1.0]), "error", "One day").data) == 1


def test_density_ignores_infinite_and_missing_values() -> None:
    fig = density(np.array([1.0, 2.0, 4.0, np.nan, np.inf]), "error", "t")
    assert fig.data[0].x.tolist() == [1.0, 2.0, 4.0]
    assert len(fig.data) == 2


def test_bar_chart_uses_the_given_axis_title() -> None:
    frame = pd.DataFrame({"group": ["n", "s"], "value": [1.0, 2.0]})
    fig = bar_chart(frame, "group", "t", "%", "#000000", axis_title="Group")
    assert fig.layout.xaxis.title.text == "Group"
    assert fig.data[0].y.tolist() == [1.0, 2.0]


def test_box_by_draws_every_row() -> None:
    frame = pd.DataFrame({"month": ["a", "b"], "ape": [1.0, 2.0]})
    assert len(box_by(frame, "month", "ape", "t").data[0].y) == 2


def test_series_charts_label_the_error_sign() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2022-01-01", periods=3),
            "actual": [1.0, 2.0, 3.0],
            "forecast": [1.0, 1.0, 1.0],
            "error": [0.0, 1.0, 2.0],
            "percentage_error": [0.0, 50.0, 66.0],
        }
    )
    assert "actual - forecast" in error_series(frame, "error", "Error").layout.yaxis.title.text
    assert [t.name for t in actual_vs_forecast(frame, "m").data] == ["Actual", "m", "Error"]
    scatter = percentage_error_scatter(frame, 5)
    assert len(scatter.data) == 1
    assert len(scatter.layout.shapes) == 2


def test_model_charts_handle_more_models_than_colours() -> None:
    columns = {f"m{i}": "forecast" for i in range(12)}
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2022-01-01", periods=2),
            "actual": [1.0, 2.0],
            "forecast": [1.0, 2.0],
        }
    )
    assert len(model_lines(frame, columns).data) == 13
    assert len(model_errors(frame, columns, 5).data) == 12

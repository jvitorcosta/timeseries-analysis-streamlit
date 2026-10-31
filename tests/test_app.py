"""Headless runs of the whole app with Streamlit's AppTest."""

from datetime import date
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from forecast_eval.core.sample import generate_sample

_APP = str(Path(__file__).parents[1] / "streamlit_app.py")
PAGES = ["Metrics", "Residuals", "Benchmark"]


def assert_clean(at: AppTest) -> None:
    assert not at.exception
    assert not at.error
    assert not at.warning


def subheaders(at: AppTest) -> list[str]:
    return [item.value for item in at.subheader]


@pytest.fixture
def app() -> AppTest:
    at = AppTest.from_file(_APP, default_timeout=120).run()
    assert_clean(at)
    return at


def open_page(at: AppTest, page: str) -> AppTest:
    at.radio(key="page").set_value(page).run()
    assert_clean(at)
    return at


def set_window(at: AppTest, start: date, end: date) -> AppTest:
    at.slider(key="period").set_value((start, end)).run()
    assert_clean(at)
    return at


def upload(at: AppTest, content: bytes, name: str = "data.csv") -> AppTest:
    at.radio(key="source").set_value("Upload a CSV").run()
    at.file_uploader(key="upload").upload(name, content, "text/csv").run()
    return at


def test_sample_loads_by_default(app: AppTest) -> None:
    assert [m.label for m in app.metric][:1]
    assert len(app.get("plotly_chart")) > 0


@pytest.mark.parametrize("page", PAGES)
def test_every_page_renders(app: AppTest, page: str) -> None:
    assert len(open_page(app, page).get("plotly_chart")) > 0


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize(
    ("start", "end"),
    [(date(2023, 3, 1), date(2023, 3, 1)), (date(2023, 3, 1), date(2023, 4, 29))],
    ids=["one-day", "sixty-days"],
)
def test_short_windows_stay_clean(app: AppTest, page: str, start: date, end: date) -> None:
    open_page(set_window(app, start, end), page)


def test_holiday_section_shows_on_a_healthy_run(app: AppTest) -> None:
    assert "Holidays" in subheaders(open_page(app, "Residuals"))


def test_rmse_by_month_and_weekday_shows(app: AppTest) -> None:
    assert "RMSE by month and weekday" in subheaders(open_page(app, "Residuals"))


def test_metrics_page_states_the_denominators(app: AppTest) -> None:
    captions = " ".join(c.value for c in app.caption)
    assert "divides by the forecast" in captions
    assert "divides by the actual" in captions


def test_zero_actual_days_are_reported(app: AppTest) -> None:
    open_page(app, "Residuals")
    assert any("zero actual" in c.value for c in app.caption)


@pytest.mark.parametrize("key", ["standardize", "partial"])
def test_residual_toggles(app: AppTest, key: str) -> None:
    open_page(app, "Residuals")
    app.checkbox(key=key).check().run()
    assert_clean(app)


def test_every_decomposition_choice(app: AppTest) -> None:
    open_page(app, "Residuals")
    for column in app.selectbox(key="decompose_column").options:
        app.selectbox(key="decompose_column").select(column).run()
        assert_clean(app)
    app.selectbox(key="decompose_period").select(365).run()
    assert_clean(app)


def test_benchmark_toggles(app: AppTest) -> None:
    open_page(app, "Benchmark")
    app.checkbox(key="hybrid").check().run()
    assert_clean(app)
    assert any(m.value == "**Hybrid**" for m in app.markdown)
    assert any("same data" in c.value for c in app.caption)
    app.checkbox(key="tables").check().run()
    assert_clean(app)
    assert len(app.dataframe) >= 2


def test_benchmark_reports_the_scored_rows(app: AppTest) -> None:
    open_page(app, "Benchmark")
    assert any("every model has a forecast" in c.value for c in app.caption)


def test_benchmark_with_a_second_group(app: AppTest) -> None:
    open_page(app, "Benchmark")
    app.selectbox(key="benchmark_group").select("south").run()
    assert_clean(app)


def test_upload_maps_known_names(app: AppTest) -> None:
    csv = generate_sample().head(400).to_csv(index=False).encode()
    upload(app, csv)
    assert_clean(app)
    assert len(app.get("plotly_chart")) > 0


def test_upload_needs_a_mapping_for_unknown_names(app: AppTest) -> None:
    upload(app, b"a,b,c,d\n1,2022-01-01,1,1\n")
    assert not app.exception
    assert not app.get("plotly_chart")
    assert any("Choose" in item.value for item in app.info)


def test_wrong_mapping_explains_itself(app: AppTest) -> None:
    csv = generate_sample().head(400).to_csv(index=False).encode()
    upload(app, csv)
    app.selectbox(key="map_group").select("(none)").run()
    app.selectbox(key="map_actual").select("zone").run()
    assert not app.exception
    assert any("numeric" in item.value for item in app.error)


def test_one_column_for_two_roles_explains_itself(app: AppTest) -> None:
    csv = generate_sample().head(400).to_csv(index=False).encode()
    upload(app, csv)
    app.selectbox(key="map_actual").select("forecast").run()
    assert not app.exception
    assert any("more than one role" in item.value for item in app.error)


def test_non_csv_explains_itself(app: AppTest) -> None:
    upload(app, b"\xff\xfe\x00\x01garbage")
    assert not app.exception
    assert app.error


def test_a_file_with_one_day_stays_clean(app: AppTest) -> None:
    upload(app, b"series,date,actual,forecast\na,2022-01-01,1,2\n")
    assert_clean(app)
    assert not app.get("slider")


def test_upload_with_no_benchmark_stays_clean(app: AppTest) -> None:
    csv = generate_sample().head(400).drop(columns="zone").to_csv(index=False).encode()
    upload(app, csv)
    open_page(app, "Benchmark")
    assert any("benchmark" in item.value for item in app.info)


def test_widgets_have_labels(app: AppTest) -> None:
    for page in PAGES:
        open_page(app, page)
        for widget in [*app.selectbox, *app.radio, *app.checkbox, *app.slider]:
            assert widget.label

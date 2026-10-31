from importlib import resources

import pandas as pd

from forecast_eval.core.preprocess import prepare
from forecast_eval.core.sample import SAMPLE_MAP, generate_sample


def test_generator_is_seeded() -> None:
    pd.testing.assert_frame_equal(generate_sample(), generate_sample())


def test_committed_csv_matches_the_generator() -> None:
    path = resources.files("forecast_eval") / "resources" / "sample_forecasts.csv"
    with path.open() as handle:
        committed = pd.read_csv(handle)
    pd.testing.assert_frame_equal(committed, generate_sample(), check_exact=False)


def test_sample_passes_the_pipeline() -> None:
    prepared = prepare(generate_sample(), SAMPLE_MAP)
    assert prepared.dropped_rows == 0
    assert prepared.frame["series"].nunique() == 6
    assert prepared.frame["group"].nunique() == 2
    assert (prepared.frame["actual"] == 0).sum() > 0
    assert prepared.frame[SAMPLE_MAP.benchmarks[0]].isna().sum() > 0

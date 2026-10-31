"""Rewrite the bundled sample CSV. Run with: uv run python scripts/make_sample_data.py"""

from pathlib import Path

from forecast_eval.core.sample import generate_sample

TARGET = Path(__file__).parents[1] / "src" / "forecast_eval" / "resources" / "sample_forecasts.csv"


def main() -> None:
    generate_sample().to_csv(TARGET, index=False, lineterminator="\n")
    print(f"Wrote {TARGET}")


if __name__ == "__main__":
    main()

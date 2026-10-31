# Forecast error analysis

Evaluate daily forecasts: where they miss, by series, period and holiday, and against a benchmark.

## Tech stack

- Python 3.12+, managed by **uv** (no pip, no manual venvs)
- src layout: code in `src/forecast_eval/`, tests in `tests/`
- Ruff (lint + format), mypy strict, pytest + pytest-cov
- Streamlit, pandas, Plotly, statsmodels

## Commands

- `make run`: start the app
- `make requirements`: regenerate `requirements.txt` after changing dependencies
- `make check`: lint + typecheck + tests. **Run before saying a task is done.**
- `make format`: auto-format + safe fixes
- `make test` / `uv run pytest tests/test_x.py::test_name -x`: run tests
- `uv add <pkg>` / `uv add --dev <pkg>`: add dependencies
- `uv run <cmd>`: run anything inside the project env

If `make` is unavailable, run the equivalent `uv run ...` line from the `Makefile`.

## Conventions

- Detailed rules: @.claude/rules/code-style.md, @.claude/rules/testing.md, @.claude/rules/api-conventions.md
- Write a failing test first for bug fixes.
- Prefer small, pure functions; side effects at the edges.
- Conventional Commits (`feat:`, `fix:`, ...). See CONTRIBUTING.md.

## Don'ts

- Don't `pip install` or edit `uv.lock` by hand.
- Don't add `# type: ignore` / `# noqa` without a reason comment.
- Don't commit secrets; config comes from environment variables.

## Architecture

`streamlit_app.py` calls `forecast_eval.app.main`. `ui/sidebar.py` loads a CSV into the
canonical frame through `core/preprocess.py`, then `ui/period.py` filters it, and the page
in `ui/` (`overview`, `residuals`, `benchmark`) renders it.

- `core/`: calculations. `metrics` holds every formula, `aggregate` and `benchmark` summarize.
- `charts/`: functions returning Plotly figures.
- `core/` and `charts/` never import Streamlit (`tests/test_charts.py` enforces it).

## Rules

- Error is always actual - forecast. Percentage errors divide by the actual.
- `deviation_from_forecast_pct` is the only metric that divides by the forecast.
- Score forecasts as given, and compare models only on shared rows.
- The sample is synthetic: change `core/sample.py`, then run `scripts/make_sample_data.py`.
- Never add real client names, site ids or data to this repo.

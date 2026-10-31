# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com) and this
project uses [Semantic Versioning](https://semver.org).

## [Unreleased]

## [2.0.0] - 2026-10-31

### Changed

- Rebuilt on Python 3.12 with the current Streamlit, pandas, Plotly and statsmodels, under
  `src/forecast_eval/`, with `core`, `charts` and `ui` layers. The UI is now in English.
- MAPE and MPE divide by the actual. The forecast-based tolerance is a separate metric,
  deviation from forecast, and it drives "days above tolerance".
- Error is always actual minus forecast, on every page.
- Forecasts are scored as given, with no clipping of negatives and no cap at 100%.
- Benchmarks are scored on the rows every model shares, and the row count is shown.
- Standardized residuals are centred on the mean and use the sample standard deviation.
- ACF and PACF lags are calendar days, and short windows cap the lag count.
- The decomposition period can be set, and interpolated days are reported.
- The hybrid forecast takes a per-series choice for any series ids.

### Added

- A seeded synthetic sample dataset as the default, with a download button.
- A column mapping step with guessed defaults and clear errors for a wrong mapping.
- RMSE by month and weekday, computed per series and period.
- MIT license, CI on three operating systems, and tests including AppTest runs of each page.

### Fixed

- The holiday section ran only after an error. It now renders normally.
- Two holidays on one date no longer duplicate a row, and optional days are labelled.
- The ACF band was drawn one lag to the left, and ACF charts had no title.
- Undefined errors in the tables were coloured as on target.

### Removed

- The password and spreadsheet data path, the site-specific model table and filters, the
  second grouping filter, the disabled page, and the Dockerfile.


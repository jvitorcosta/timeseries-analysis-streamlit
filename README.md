# Forecast error analysis (Streamlit)

A single MAPE number says a forecast is "5% off". It doesn't say **where**: which sites,
which weekdays, which holidays, or whether a simpler baseline would have done better.
This app answers those questions for any daily forecast.

I built it in 2022 while working on daily gas-demand forecasting at city-gate level, where
a day above the error tolerance has a contractual cost. It was the tool for comparing
candidate models against the incumbent forecast, series by series and day by day.

Upload a CSV, map its columns (id, date, actual, forecast, benchmark forecasts, class) and
explore. The interface is in Portuguese.

## What it shows

**Global metrics**
- Share of days above the 5% error tolerance, per series and per class.
- MAPE per series and per class over any chosen period.

**Residual analysis**
- Residual distributions and standardised residuals per series.
- MAPE and RMSE by month and by weekday, to expose seasonal bias.
- Error on public holidays (a São Paulo holiday calendar built on `pandas`, including
  moving dates such as Carnival and Corpus Christi).
- Classical seasonal decomposition and ACF/PACF plots of any column.

**Benchmark**
- Several forecasts side by side against the same actuals, with a colour-coded MAPE table
  per series, so you can see where a challenger model beats the incumbent.

Metrics live in [`kpi.py`](kpi.py): MAPE, MPE, MSE, RMSE and RSE.

## Input format

One row per series per day. Column names are free, you pick them in the sidebar:

| Column | Example | Purpose |
|--------|---------|---------|
| id | `site_a` | the series being forecast |
| date | `2022-03-01` | daily timestamp |
| actual | `1520.4` | observed value |
| forecast | `1498.0` | the model being evaluated |
| benchmark(s) | `1610.2` | one or more forecasts to compare against |
| class | `zone_2` | a grouping for aggregated views |

## Run it

```sh
pip install -r requirements.txt
streamlit run app.py
```

Or with Docker:

```sh
docker build -t forecast-error-analysis .
docker run -p 8501:8501 forecast-error-analysis
```

## Status

A 2022 project, kept as it was built (Python 3.9, Streamlit 1.5). Today I'd add a sample
dataset and a hosted demo, move the metrics into a tested package, and add prediction
intervals and bias tracking alongside MAPE.

**Stack:** Python, Streamlit, pandas, NumPy, Plotly, statsmodels

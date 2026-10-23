# Time-series forecast evaluation (Streamlit)

A Streamlit app for checking how good a set of forecasts really is. Upload a CSV with actual values, predictions and an optional benchmark forecast, and the app breaks the error down so you can see where a model works and where it doesn't.

Built in 2022 while I worked on natural-gas demand forecasting in consulting. The interface is in Portuguese.

## What it shows

- **Global metrics:** MAPE per group and per class over a chosen period, and the share of periods where the error goes above 5%.
- **Residual analysis:** how errors behave over time and across groups.
- **Benchmark:** the model compared with a baseline forecast on the same data.

Metrics are implemented in `kpi.py`: MAPE, MPE, MSE, RMSE and RSE.

## Run it

```sh
pip install -r requirements.txt
streamlit run app.py
```

Or build the Docker image from the included `Dockerfile`.

**Stack:** Python, Streamlit, pandas, NumPy, Plotly, statsmodels

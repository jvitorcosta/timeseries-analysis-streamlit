"""The date window every page works on."""

import pandas as pd
import streamlit as st

from forecast_eval.core.aggregate import filter_period
from forecast_eval.core.schema import DATE


def choose_period(frame: pd.DataFrame) -> pd.DataFrame:
    first, last = frame[DATE].min().date(), frame[DATE].max().date()
    if first == last:
        st.caption(f"The data covers one day: {first}.")
        return frame
    start, end = st.slider(
        "Period", min_value=first, max_value=last, value=(first, last), key="period"
    )
    st.caption(f"{start} to {end}: {(end - start).days + 1} calendar days.")
    return filter_period(frame, start, end)

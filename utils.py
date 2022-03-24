import streamlit as st
from kpi import *

MESES =["Janeiro", "Fevereiro", "Março", "Abril",
          "Maio", "Junho", "Julho", "Agosto",
          "Setembro", "Outubro", "Novembro", "Dezembro"]

WEEKDAY = ["Segunda", "Terça",
           "Quarta","Quinta",
           "Sexta", "Sábado", "Domingo"]

nomear_dia = lambda x: WEEKDAY[x]
nomear_mes = lambda x: MESES[x-1]

@st.cache(allow_output_mutation=True, persist = True)
def load_data(file):
    try:
        return pd.read_csv(file, parse_dates=True)
    except:
        st.error(
            "This file can't be converted into a dataframe. Please import a csv file with a valid separator."
        )
        st.stop()
        
def preprocess_dataframe(data: pd.DataFrame,
                         time_col: str,
                         y_true: str,
                         y_predicted: str,
                         ) -> pd.DataFrame:
    
    data[time_col] = pd.to_datetime(data[time_col], format = '%Y-%m-%d')
    data[time_col] = data[time_col].dt.date
    nan_mask = (data[y_true].isna())|(data[y_predicted].isna())
    data = data[~nan_mask]   # remove nan's 
    data[y_predicted] = np.where(data[y_predicted]<0, 0, data[y_predicted])    #Clip para previsões negativas
    data['rmse'] = RMSE(data[y_true],data[y_predicted])
    data['mpe'] = MPE(data[y_true],data[y_predicted])
    data['mape'] = np.abs(data['mpe'])
    data['mape'] = np.where(data['mape']>100, 100, data['mape'])     #Limiar do MAPE para evitar distorções
    data['residuo'] = data[y_true] - data[y_predicted]
    data['acima5'] = (data['mape']>5).astype(int)
    data['acima20'] = (data['mape']>20).astype(int)
    data = data.sort_values(by = time_col, ascending=True)
    return data

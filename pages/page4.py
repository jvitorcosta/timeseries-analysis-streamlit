import time
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from statsmodels.tsa.stattools import pacf, acf
from statsmodels.tsa.seasonal import seasonal_decompose
from pandas.tseries.holiday import AbstractHolidayCalendar, GoodFriday, Holiday, Easter, Day
from typing import List, Any, Dict, Tuple

from utils import nomear_mes, nomear_dia

from kpi import *
from dashboard import *

def create_benchmark_view(df, time_col, data_group, classe, y_true, y_benchmark):
    
    #try:    
    benchmark_df = df.copy()
    benchmark_df[time_col] = pd.to_datetime(benchmark_df[time_col])
    benchmark_df = benchmark_df.groupby([pd.Grouper(key = time_col, freq = 'D'), classe]).sum().reset_index()
    benchmark_df = benchmark_df.reset_index()
    st.session_state['chosen_item'] = st.selectbox('Classe', benchmark_df[classe].unique().tolist())
    days_count = benchmark_df.loc[benchmark_df[classe] == st.session_state['chosen_item']].shape[0]

    '''col_bench = st.columns(2)
    col_bench[0].metric(label=classe,
                value= st.session_state['chosen_item'],
                delta=f"")
    
    col_bench[1].metric(label="Período",
                value=f"{days_count} dias") '''       
    
    st.write(sorted(df.loc[df[classe] == st.session_state['chosen_item']][data_group].unique().tolist()))

    fig_series = go.Figure()
    fig_scatter = go.Figure()
    #fig.update_xaxes(title_text="Data")
    #fig.update_yaxes(title_text= "Erro Médio Percentual", showgrid=False, zerolinecolor='#000000')
    
    benchmark_df['lim_sup'] = 5
    benchmark_df['lim_inf'] = -1*benchmark_df['lim_sup']
    
    rgb_list = ['rgb(120,120,120)',
                'rgb(50,238,0)',
                'rgb(24,227,410)',
                'rgb(220,60,210)',
                'rgb(11,320,0)']  
    
    for num, prev in enumerate(y_benchmark):
    
        benchmark_df['residuo'] = benchmark_df[prev] - benchmark_df[y_true]
        benchmark_df['mpe'] = 100*(benchmark_df['residuo']/benchmark_df[prev])
        benchmark_df['mape'] = np.abs(benchmark_df['mpe'])
        benchmark_df['acima5'] = np.where(benchmark_df['mape']>5, 1, 0)
        benchmark_df['acima20'] = np.where(benchmark_df['mape']>20, 1, 0)
        
        dfplot = benchmark_df.loc[benchmark_df[classe] == st.session_state['chosen_item']]
        
        days_count = dfplot.shape[0]
        mape_metrica = dfplot.mape.clip(0,100).mean()
        
        acima5_mask = (dfplot['acima5']==True)
        days_acima5 = dfplot.loc[acima5_mask].shape[0]
        perc_acima5 = days_acima5/days_count
        
        acima20_mask = (dfplot['acima20']==True)
        days_acima20 = dfplot.loc[acima20_mask].shape[0] 
        perc_acima20 = days_acima20/days_count
        
        col2 = st.columns(4)
        delta1 = np.round(mape_metrica-5,2)
        
        #col2[0].metric(label=data_group,value= st.session_state['chosen_item'],delta=f"")
        #col2[1].metric(label="Período", value=f"{days_count} dias")
        col2[0].metric(label="Previsto", value=f"{prev}")
        
        col2[1].metric(label="MAPE",
                    value=f"{round(mape_metrica,2)}%",
                    delta=f"{delta1}%",
                    delta_color="inverse")
        
        col2[2].metric(label="Dias Acima de 5%",
                    value=f"{round(100*perc_acima5,2)}%",
                    delta=f"{days_acima5} dias",
                    delta_color='off')
        
        col2[3].metric(label="Dias Acima de 20%",
                    value=f"{round(100*perc_acima20,2)}%",
                    delta=f"{days_acima20} dias",
                    delta_color='off')
    
        fig_series.add_trace(go.Scattergl(x= dfplot[time_col],
                                    y= dfplot[prev],
                                    mode='lines',
                                    line=dict(color=rgb_list[num]),
                                    name= prev
                                    )
        )
        fig_scatter.add_trace(go.Scattergl(x=dfplot[time_col],
                                y=dfplot['mpe'],
                                mode='markers',
                                line=dict(color=rgb_list[num]),
                                name= prev
                                )
        )
    
    with st.expander('Tabela'):
            st.dataframe(dfplot[[time_col,
                                classe,
                                y_true]+y_benchmark])
    
        
    with st.expander(f'Visão por {classe}'):
        fig_series.add_trace(go.Scattergl(x= dfplot[time_col],
                                        y= dfplot[y_true],
                                        mode='lines',
                                        line=dict(color='rgb(32,4,114)'),
                                        name='Real'
                                        )
        )
        fig_series.update_xaxes(title_text="Data")
        fig_series.update_yaxes(title_text= "Residuo", showgrid=False, zerolinecolor='#000000')
        fig_series = format_fig(fig_series, '', x_title=time_col, y_title='Resíduo')
        st.plotly_chart(fig_series, use_container_width=True)
            
        
        fig_scatter.add_trace(go.Scattergl(
                    y=dfplot['lim_sup'], 
                    x=dfplot[time_col],
                    line=dict(color='red', dash = 'dash'),
                    name='+5%'
                    )
        )
        fig_scatter.add_trace(go.Scattergl(
                    y=dfplot['lim_inf'], 
                    x=dfplot[time_col],
                    line=dict(color='red', dash = 'dash'),
                    name='-5%'
                    )
        )
        fig_scatter.update_xaxes(title_text="Data")
        fig_scatter.update_yaxes(title_text= "Erro Médio Percentual", showgrid=False, zerolinecolor='#000000')
        fig_scatter = format_fig(fig_scatter, '', x_title=time_col, y_title='Erro Médio Percentual')
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with st.expander(f'Visão por {data_group} da '+st.session_state['chosen_item']):
        
        group_items = sorted(df.loc[df[classe] == st.session_state['chosen_item'],data_group].unique().tolist())
        dfplot2 = df.loc[df[data_group].isin(group_items)]
        
        fig_group = go.Figure()
        
        sd = st.selectbox(f'{data_group}', df.loc[df[data_group].isin(group_items)][data_group].unique().tolist())

        dfplot2 = df.loc[df[data_group] == sd].copy()
        
        col_group = st.columns(2)
        col_group[0].metric(label=data_group,
                value= sd,
                delta=f"")
    
        col_group[1].metric(label="Período",
                value=f"{days_count} dias")   
    
        fig_group.add_trace(go.Scattergl(x= dfplot2[time_col],
                                        y= dfplot2[y_true],
                                        mode='lines',
                                        line=dict(color='rgb(32,4,114)'),
                                        name='Real'
                                        )
        )
        
        for num, prev in enumerate(y_benchmark):
            
            dfplot2['residuo'] = dfplot2[prev] - dfplot2[y_true]
            dfplot2['mpe'] = 100*(dfplot2['residuo']/dfplot2[prev])
            dfplot2['mape'] = np.abs(dfplot2['mpe'])
            dfplot2['acima5'] = np.where(dfplot2['mape']>5, 1, 0)
            dfplot2['acima20'] = np.where(dfplot2['mape']>20, 1, 0)
            
            days_count = dfplot2.shape[0]
            mape_metrica = dfplot2.mape.clip(0,100).mean()
            
            acima5_mask = (dfplot2['acima5']==True)
            days_acima5 = dfplot2.loc[acima5_mask].shape[0]
            perc_acima5 = days_acima5/days_count
            
            acima20_mask = (dfplot2['acima20']==True)
            days_acima20 = dfplot2.loc[acima20_mask].shape[0] 
            perc_acima20 = days_acima20/days_count
        
            colg = st.columns(4)
            deltag = np.round(mape_metrica-5,2)
            
            #col2[0].metric(label=data_group,value= st.session_state['chosen_item'],delta=f"")
            #col2[1].metric(label="Período", value=f"{days_count} dias")
            colg[0].metric(label="Previsto", value=f"{prev}")
            
            colg[1].metric(label="MAPE",
                        value=f"{round(mape_metrica,2)}%",
                        delta=f"{deltag}%",
                        delta_color="inverse")
            
            colg[2].metric(label="Dias Acima de 5%",
                        value=f"{round(100*perc_acima5,2)}%",
                        delta=f"{days_acima5} dias",
                        delta_color='off')
            
            colg[3].metric(label="Dias Acima de 20%",
                        value=f"{round(100*perc_acima20,2)}%",
                        delta=f"{days_acima20} dias",
                        delta_color='off')
        
            fig_group.add_trace(go.Scattergl(x= dfplot2[time_col],
                                        y= dfplot2[prev],
                                        mode='lines',
                                        line=dict(color=rgb_list[num]),
                                        name=prev
                                        )
            )
        
        fig_group.update_xaxes(title_text="Data")
        fig_group.update_yaxes(title_text= "Erro Médio Percentual", showgrid=False, zerolinecolor='#000000')
        fig_group = format_fig(fig_group, '', x_title=time_col, y_title='Erro Médio Percentual')
        st.plotly_chart(fig_group, use_container_width=True)
    #except:pass
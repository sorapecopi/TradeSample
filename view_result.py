import datetime
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import streamlit as st
from mt5.mt5_terminal import Mt5Terminal

def custom_date_parser(x):
    try:
        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S%z')
    except ValueError:
        return datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f%z')

def get_color(row):
    ret_color = None
    if row.action == 'BUY':
        if row.result == 'GET':
            ret_color = "blue"
        else:
            ret_color = "fuchsia"
    elif row.action == 'SELL':
        if row.result == 'GET':
            ret_color = "yellow"
        else:
            ret_color = "lime"
    else:
        raise Exception
    return ret_color

def main():
    st.set_page_config(layout="wide")
    symbol = "USDJPY"
    gran = 'M1'
    mt5 = Mt5Terminal()
    uploaded_file = st.file_uploader("Choose a file", type='csv', key='csv_file')
    if uploaded_file is not None:
        # CSVファイルから
        df_result = pd.read_csv(uploaded_file, parse_dates=['start_time', 'end_time'], date_parser=custom_date_parser)
        df_result = df_result.iloc[:, 1:]
        st.dataframe(df_result)
        from_time = df_result.start_time[0] - datetime.timedelta(hours=1)
        to_time = df_result.iloc[-1].end_time + datetime.timedelta(hours=1)
        df = mt5.get_candle_from_to(symbol, gran, from_time, to_time)
        data1 = [go.Candlestick(x=df.index,
                                open=df.open,
                                high=df.high,
                                low=df.low,
                                close=df.close)]
        fig = go.Figure(data=data1)
        for idx in df_result.index:
            row = df_result.loc[idx]
            s_idx = row.start_time
            e_idx = row.end_time
            s_price = row.start_price
            e_price = row.end_price
            fig.add_trace(
                go.Scatter(
                    x=[s_idx, e_idx],
                    y=[s_price, e_price],
                    mode="lines",
                    # line=dict(color='blue') if row.result == "GET" else dict(color='yellow'),
                    line=dict(color=get_color(row)),
                    showlegend=False
                ))
        fig.update_layout(
            height=1000,
            hovermode='x unified',
            # hovermode='y unified',
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()
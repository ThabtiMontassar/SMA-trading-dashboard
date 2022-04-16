import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
st.set_page_config(layout="wide")
st.title('Trading View')
col1, col2 = st.columns([1, 4])
with st.sidebar:
    st.subheader('Stock Ticker')
    stock = st.text_input('stock name', 'AAPL')
    startdate = st.date_input(
     "start date",
     datetime.date(2022, 4, 2))

    enddate = st.date_input(
     "end date",
     datetime.date(2022, 4, 9))
    freq = st.selectbox(
     'Frequency',
     ('1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo'))
    st.subheader('Mouving Average SMA')
    short = st.number_input('short',value=5)
    long = st.number_input('long', value=8)
    st.subheader('Initial Balance')
    money = st.number_input('Investment ammount', value=500)
    

DATA = yf.download(stock, start=startdate, end=enddate, interval=freq)# valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
DATA.reset_index(inplace=True)
cols=list(DATA.columns)
ind=cols[0]
DATA=DATA.rename(columns={ind: "Date"})
DATA['SMA_9'] = DATA['Close'].rolling(window=short, min_periods=1).mean()
DATA['SMA_30'] = DATA['Close'].rolling(window=long, min_periods=1).mean()





fig = go.Figure()
fig.add_trace(go.Scatter(x=DATA["Date"], y=DATA["Close"],line=dict(color="#ffffff"),name='Close'))
fig.add_trace(go.Scatter(x=DATA["Date"], y=DATA["SMA_9"],line=dict(color="#5e30b2"),name='SMA_Short'))
fig.add_trace(go.Scatter(x=DATA["Date"], y=DATA["SMA_30"],line=dict(color="#e69520"),name='SMA_Long'))
fig.update_layout(paper_bgcolor="#0e1117",plot_bgcolor="#0e1117",legend=dict(font=dict(color="white")))
fig.update_xaxes(showgrid=False, zeroline=False)
fig.update_yaxes(showgrid=False, zeroline=False)
fig.update_xaxes(color="#ffffff")
fig.update_yaxes(color="#ffffff")

# Create a pandas dataframe that is the same size as the BTC_USD dataframe and covers the same dates
trade_signals = pd.DataFrame(index=DATA.index)

# Define the intervals for the Fast and Slow Simple Moving Averages (in days)
short_interval = short
long_interval = long

# Compute the Simple Moving Averages and add it to the dateframe as new columns
trade_signals['Short'] = DATA['Close'].rolling(window=short_interval, min_periods=1).mean()
trade_signals['Long'] = DATA['Close'].rolling(window=long_interval, min_periods=1).mean()

# Create a new column populated with zeros
trade_signals['Signal'] = 0.0

# Wherever the Shorter term SMA is above the Longer term SMA, set the Signal column to 1, otherwise 0
trade_signals['Signal'] = np.where(trade_signals['Short'] > trade_signals['Long'], 1.0, 0.0) 

# Enter your code below and run the cell
trade_signals['Position'] = trade_signals['Signal'].diff()

# Define how much money you will start with (in USD)
initial_balance = money # ten thousand USD

# Create dataframe containing all the dates considered
backtest = pd.DataFrame(index=trade_signals.index)

# Add column containing the daily percent returns of Bitcoin
backtest['BTC_Return'] = DATA['Close'] / DATA['Close'].shift(1) # Current closing price / yesterday's closing price

# Add column containing the daily percent returns of the Moving Average Crossover strategy
backtest['Alg_Return'] = np.where(trade_signals.Signal == 1, backtest.BTC_Return, 1.0)

# Add column containing the daily value of the portfolio using the Crossover strategy
backtest['Balance'] = initial_balance * backtest.Alg_Return.cumprod() # cumulative product

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=DATA["Date"], y=initial_balance*backtest.BTC_Return.cumprod(),line=dict(color="#ffffff"),name='buy & hold'))
fig2.add_trace(go.Scatter(x=DATA["Date"], y=backtest['Balance'],line=dict(color="#048bb0"),name='Algo'))
fig2.update_layout(paper_bgcolor="#0e1117",plot_bgcolor="#0e1117",legend=dict(font=dict(color="white")))
fig2.update_xaxes(showgrid=False, zeroline=False)
fig2.update_yaxes(showgrid=False, zeroline=False)
fig2.update_xaxes(color="#ffffff")
fig2.update_yaxes(color="#ffffff")






st.header('Price Chart')
st.plotly_chart(fig, use_container_width=True)

algopercent=((backtest['Balance'].tail(1).item()-money) / money)*100
buypercent=((initial_balance*backtest.BTC_Return.cumprod().tail(1).item()-money) / money)*100
st.header('Backtest Chart')
col1, col2, col3 = st.columns(3)
col1.metric("Initial Amount", money)
col2.metric("Buy & hold ", round(initial_balance*backtest.BTC_Return.cumprod().tail(1).item(),2), round(buypercent,2))
col3.metric("Algo", round(backtest['Balance'].tail(1).item(),2), round(algopercent,2))

st.plotly_chart(fig2, use_container_width=True)






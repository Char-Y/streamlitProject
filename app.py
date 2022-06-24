# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 23:40:21 2022

@author: yangy
"""

import time
import datetime
import pandas as pd
import requests
import streamlit as st
import plotly.express as px

start_date = datetime.datetime(2020, 1, 1)
end_date = datetime.date.today()
start = int(time.mktime(start_date.timetuple()))
end = int(time.mktime(end_date.timetuple()))
interval = '1d' # 1d, 1m

#%% Grab all data
@st.cache

def grabAllData():
    epsList = []
    tickers = ['TSLA', 'AAPL', 'AMZN', 'NFLX', 'MSFT','JNJ','META','TWTR','^GSPC','^RUT']
    
    for ticker in tickers:
        query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={start}&period2={end}&interval={interval}&events=history&includeAdjustedClose=true'
        df = pd.read_csv(query_string, index_col=['Date']) 
        df['Returns'] = df['Adj Close'].pct_change(1)
        df['Ticker']= ticker
        if ticker =='^GSPC':
            df['Ticker']= 'SP500'
            df['Type'] = 'Index'
        elif ticker == '^RUT':
            df['Ticker']= 'Russell2000'
            df['Type'] = 'Index'
        else:
            df['Type'] = 'Stock'
        epsList.append(df)
        # df.to_csv('{}.csv'.format(ticker))
    dataAll = pd.concat(epsList)
    return dataAll

        
#%% Grab all data

df = grabAllData()
df = df.dropna(axis=0)
tickers = list(df['Ticker'].unique())
indices = tickers[8:]
stocks = tickers[0:8]
StocksColumns = list(df.columns)

#%% Streamlit Web App
st.title("Stock Portfolio Analysis")

stockPick = st.sidebar.multiselect("Pick the stocks to graph",stocks, ['AAPL'])
filterDF1 = df[df['Ticker'].isin(stockPick)]
indexPick = st.sidebar.multiselect("Compare with indices",indices, ['SP500'])
filterDF2 = df[df['Ticker'].isin(indexPick)]

indexPick.extend(stockPick)
filterDF = df[df['Ticker'].isin(indexPick)]
st.write("Stocks selected: " + "; ".join(stockPick))

#Seaborn chart
# fig, ax = plt.subplots() #solved by add this line 
# ax = sns.lineplot(data=filterDF, x=filterDF.index, y="Close", hue='Ticker')
# st.pyplot(fig)
pick = st.sidebar.selectbox('Which data would you like to check?',('Adj Close Price','Daily Returns','Cumulative Returns'))
pickCharts = st.sidebar.radio('Pick a chart type',('Line Chart','Box & Whisker'))
if pick == 'Cumulative Returns': 

    custTitle = "Cumulative Returns Data"
    cumRtrns=(filterDF['Returns']+1).cumprod()
    if pickCharts == "Line Chart":  
        fig = px.line(filterDF, x=filterDF.index, y=cumRtrns, color="Ticker", title=custTitle)
    else:
        fig = px.box(filterDF,
                     x='Ticker',
                     y=cumRtrns,
                     color="Ticker",
                     title=custTitle  )        
    st.plotly_chart(fig)
elif pick == 'Daily Returns':
    custTitle = "Daily Returns Data"
    if pickCharts == 'Box & Whisker':  
        fig = px.box(filterDF,
                     x='Ticker',
                     y='Returns',
                     color="Ticker",
                     title=custTitle  )
    else:   
        fig = px.line(filterDF, x=filterDF.index, y="Returns", color="Ticker", title=custTitle)
    st.plotly_chart(fig)
else:
    custTitle = "Daily Price Data"
    if pickCharts == 'Box & Whisker':  
        fig = px.box(filterDF,
                     x='Ticker',
                     y="Adj Close",
                     color="Ticker",
                     title=custTitle  )
    else:        
        fig = px.line(filterDF, x=filterDF.index, y="Adj Close", color="Ticker", title=custTitle)
    st.plotly_chart(fig)
    st.write(filterDF)


from datetime import datetime
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import io

import streamlit as st
st.header(f"ATR STRANGLE")
st.write("This is a system which trades on Banknifty Options to earn theta on Intraday")
st.write('Please select Slippage & Comissions between 0% to 2% for backtest')
st.write("Minimum Capital Required : 200000")
slip1 = st.slider("Slippage & Comissions in %", min_value=0, max_value=2, value=1)



# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'Please contact me on',
    ('Email : "tejaswi1995@gmail.com"', 'Mobile phone : +91-9900333006')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.write("P.S : The same system can be hedged to give returns around 45-50% pa")
url= "https://raw.githubusercontent.com/tejaswi1995prakash/ATR-STRANGLE-RESULTS/main/BNF%20ATR%20FACTOR%20(6).csv"
download = requests.get(url).content
df = pd.read_csv(io.StringIO(download.decode('utf-8')))
df['Date'] = df['Date'].apply(lambda x : datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
df = df[['Date','total_entry','total_exit']]
df['Capital'] = 200000
def PNL(entry,exit,slippage,lot):
  en = entry - (slippage/100)*entry
  ex = exit + (slippage/100)*exit
  profit = (en - ex)* lot * 25
  return(profit)

PROFITS = []
for i in df.index:
  entry = df.at[i,'total_entry']
  exit = df.at[i,'total_exit']
  profit = PNL(entry,exit,slip1,1)
  PROFITS.append(profit)

df['PNL'] = PROFITS

def single_stats(df):
    original = df.copy()
    # cumulative pnl
    df['CumPNL'] = df['PNL'].cumsum()
    # drawdown
    df['HighValue'] = df['CumPNL'].cummax()
    df['Drawdown'] = df['CumPNL'] - df['HighValue']
    # roi
    df['ROI'] = round((df['PNL']/df['Capital'])*100, 2)
    # cumulative roi
    df['CumROI'] = df['ROI'].cumsum()

    # weekday wise pnl
    df['tmp'] = df.index
    weekDays = ("Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday")
    df['Week'] = df['tmp'].apply(
        lambda x: weekDays[x.to_pydatetime().weekday()])
    week_groups = pd.DataFrame()
    week_groups["PNL"] = df.groupby('Week', sort=True)['PNL'].sum()
    week_groups["ROI"] = df.groupby('Week', sort=True)['ROI'].sum()

    # monthly pnl
    df['Month'] = df['tmp'].apply(lambda x: x.strftime("%b, %Y"))
    month_groups = pd.DataFrame()
    month_groups["PNL"] = df.groupby('Month', sort=False)['PNL'].sum()
    month_groups["ROI"] = df.groupby('Month', sort=False)['ROI'].sum()

    # yearly pnl
    df['Year'] = df['tmp'].apply(lambda x: x.strftime('%Y'))
    year_groups = pd.DataFrame()
    year_groups["PNL"] = df.groupby('Year', sort=False)['PNL'].sum()
    year_groups["ROI"] = df.groupby('Year', sort=False)['ROI'].sum()

    # calculate all statistics of model.
    stats = {}
    stats["Start Date"] = datetime.strftime(df.index[0], "%d-%b-%Y")
    stats["Total Days"] = len(df)
    stats["Winning Day"] = df[df['PNL'] >= 0]['PNL'].count()
    stats["Losing Day"] = df[df['PNL'] < 0]['PNL'].count()
    stats["Winning Accuracy %"] = f"{round((stats['Winning Day']/stats['Total Days'])*100, 2)} %"
    stats["Max Profit"] = round(df["PNL"].max(),1)
    stats["Max Loss"] = round(df["PNL"].min(),1)
    stats["Max Drawdown"] = round(df["Drawdown"].min(),1)
    stats["Avg Profit on Win Days"] = round(
        df[df['PNL'] >= 0]['PNL'].mean(), 2)
    stats["Avg Loss on Loss Days"] = round(df[df['PNL'] < 0]['PNL'].mean(), 2)
    stats["Avg Profit Per day"] = round(df['PNL'].mean(), 2)
    stats["Net profit"] = round(df['PNL'].sum(),1)
    stats["Net Returns %"] = f"{round(df['ROI'].sum(),2)} %"

    stat_table = pd.DataFrame(stats.items(), columns=["Stat", "Value"])
    stat_table['Value'] = stat_table['Value'].astype(str)
    stat_table.set_index("Stat", inplace=True)
    return(stat_table)

df = df.set_index('Date')
df['Date'] = df.index

stats = single_stats(df)
st.table(stats)

#Absolute return plot
import plotly.graph_objects as go
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x= df['Date'], y= df['CumPNL'], fill='tozeroy', name= 'ATR SYSTEM',marker_color = 'Green'))
fig1.update_layout(title = "Performance")

#Percentage return plot
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x= df['Date'], y= df['CumROI'], fill='tozeroy', name= 'ATR SYSTEM',marker_color = 'SeaGreen'))
fig2.update_layout(title = "Performance")

#Drawdown Graph
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x= df['Date'], y= (df['Drawdown']/200000)*100, fill='tozeroy', name= 'ATR SYSTEM',marker_color = 'Red'))
fig3.update_layout(title = "Drawdown")

Year_groups = df.groupby('Year').sum()[['PNL','ROI']]
Month_groups = df.groupby('Month').sum()[['PNL','ROI']]


st.write('Absolute Return Plot')
st.plotly_chart(fig1)
st.write('Percentage Return Plot')
st.plotly_chart(fig2)
st.write('Drawdown in Percentage')
st.plotly_chart(fig3)
st.write(f'Yearwise Return')
st.table(Year_groups)
st.write('Monthwise Return')
st.table(Month_groups)




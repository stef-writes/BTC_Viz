import streamlit as st
import pandas as pd
import plotly.graph_objs as go

# Load the dataset
data = pd.read_csv('/Users/nooz/Desktop/BTC_Data.csv')
data['Date'] = pd.to_datetime(data['Date'])
data.set_index('Date', inplace=True)

# Streamlit App Layout
st.title("Advanced Bitcoin Price Dashboard")

# Sidebar for filtering options
st.sidebar.header("Filter Options")
start_date = st.sidebar.date_input('Start date', data.index.min())
end_date = st.sidebar.date_input('End date', data.index.max())

# Filter dataset by date range
filtered_data = data.loc[start_date:end_date]

# Sidebar options for indicators with definitions
st.sidebar.subheader("Technical Indicators")

# Bollinger Bands
show_bollinger = st.sidebar.checkbox('Show Bollinger Bands')
if show_bollinger:
    st.sidebar.write("""
    **Bollinger Bands**: A volatility indicator that consists of a middle band (usually a 20-day SMA) and two outer bands set two standard deviations away from the middle band. The wider the bands, the higher the volatility.
    """)

# Relative Strength Index (RSI)
show_rsi = st.sidebar.checkbox('Show Relative Strength Index (RSI)')
if show_rsi:
    st.sidebar.write("""
    **RSI (Relative Strength Index)**: A momentum oscillator that measures the speed and change of price movements. RSI ranges from 0 to 100 and is often used to identify overbought (above 70) or oversold (below 30) conditions.
    """)

# MACD (Moving Average Convergence Divergence)
show_macd = st.sidebar.checkbox('Show MACD (Moving Average Convergence Divergence)')
if show_macd:
    st.sidebar.write("""
    **MACD (Moving Average Convergence Divergence)**: A trend-following momentum indicator that shows the relationship between two moving averages of a security’s price, typically the 12-day EMA and the 26-day EMA. A signal line is often plotted alongside the MACD.
    """)

# Average True Range (ATR)
show_atr = st.sidebar.checkbox('Show Average True Range (ATR)')
if show_atr:
    st.sidebar.write("""
    **ATR (Average True Range)**: A volatility indicator that measures the range of price movement over a specified period. ATR is typically calculated over a 14-day period.
    """)

# On-Balance Volume (OBV)
show_obv = st.sidebar.checkbox('Show On-Balance Volume (OBV)')
if show_obv:
    st.sidebar.write("""
    **OBV (On-Balance Volume)**: A cumulative indicator that uses volume flow to predict changes in stock prices. OBV adds volume on up days and subtracts it on down days.
    """)

# Fibonacci Retracement Levels
show_fibonacci = st.sidebar.checkbox('Show Fibonacci Retracement')
if show_fibonacci:
    st.sidebar.write("""
    **Fibonacci Retracement**: A tool that uses horizontal lines to indicate areas of support or resistance at key Fibonacci levels (23.6%, 38.2%, 50%, 61.8%). These levels are derived from the Fibonacci sequence and are used by traders to predict possible reversal levels.
    """)

# Add moving averages to the filtered dataset
sma_period = 20  # Used for Bollinger Bands and base SMA calculation

# Bollinger Bands (Volatility Indicator)
if show_bollinger:
    sma_20 = filtered_data['Close'].rolling(window=sma_period).mean()
    std_20 = filtered_data['Close'].rolling(window=sma_period).std()
    filtered_data['Upper Band'] = sma_20 + (std_20 * 2)
    filtered_data['Lower Band'] = sma_20 - (std_20 * 2)
    filtered_data = filtered_data.dropna()  # Drop rows with NaN due to rolling window

# Relative Strength Index (RSI)
if show_rsi:
    delta = filtered_data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    filtered_data['RSI'] = 100 - (100 / (1 + rs))
    filtered_data = filtered_data.dropna(subset=['RSI'])  # Drop rows with NaN due to RSI calculation

# MACD (Moving Average Convergence Divergence)
if show_macd:
    ema_12 = filtered_data['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = filtered_data['Close'].ewm(span=26, adjust=False).mean()
    filtered_data['MACD'] = ema_12 - ema_26
    filtered_data['Signal Line'] = filtered_data['MACD'].ewm(span=9, adjust=False).mean()
    filtered_data = filtered_data.dropna(subset=['MACD', 'Signal Line'])  # Drop rows with NaN due to MACD calculation

# Average True Range (ATR)
if show_atr:
    filtered_data['High-Low'] = filtered_data['High'] - filtered_data['Low']
    filtered_data['High-Close'] = abs(filtered_data['High'] - filtered_data['Close'].shift(1))
    filtered_data['Low-Close'] = abs(filtered_data['Low'] - filtered_data['Close'].shift(1))
    filtered_data['True Range'] = filtered_data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
    filtered_data['ATR'] = filtered_data['True Range'].rolling(window=14).mean()
    filtered_data = filtered_data.dropna(subset=['ATR'])  # Drop rows with NaN due to ATR calculation

# On-Balance Volume (OBV)
if show_obv:
    filtered_data['Direction'] = filtered_data['Close'].diff().apply(lambda x: 1 if x > 0 else -1)
    filtered_data['OBV'] = (filtered_data['Volume'] * filtered_data['Direction']).cumsum()

# Fibonacci Retracement Levels
if show_fibonacci:
    max_price = filtered_data['Close'].max()
    min_price = filtered_data['Close'].min()
    diff = max_price - min_price
    fibonacci_levels = [max_price - (diff * level) for level in [0.236, 0.382, 0.5, 0.618]]

# Create the candlestick chart with Plotly
fig = go.Figure(data=[go.Candlestick(x=filtered_data.index,
                                     open=filtered_data['Open'],
                                     high=filtered_data['High'],
                                     low=filtered_data['Low'],
                                     close=filtered_data['Close'],
                                     increasing_line_color='green', 
                                     decreasing_line_color='red')])

# Plot Bollinger Bands
if show_bollinger:
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Upper Band'],
                             mode='lines', name='Upper Bollinger Band', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Lower Band'],
                             mode='lines', name='Lower Bollinger Band', line=dict(color='cyan')))

# Plot RSI
if show_rsi:
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['RSI'],
                             mode='lines', name='RSI', line=dict(color='purple')))
    # Optional: Add an additional y-axis for RSI (if you want to keep it separate)
    fig.update_layout(yaxis2=dict(title='RSI', overlaying='y', side='right', showgrid=False))

# Plot MACD and Signal Line
if show_macd:
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['MACD'],
                             mode='lines', name='MACD', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['Signal Line'],
                             mode='lines', name='Signal Line', line=dict(color='red')))

# Plot ATR
if show_atr:
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['ATR'],
                             mode='lines', name='ATR', line=dict(color='orange')))

# Plot OBV
if show_obv:
    fig.add_trace(go.Scatter(x=filtered_data.index, y=filtered_data['OBV'],
                             mode='lines', name='OBV', line=dict(color='blue')))

# Plot Fibonacci Levels
if show_fibonacci:
    for level, value in zip([0.236, 0.382, 0.5, 0.618], fibonacci_levels):
        fig.add_trace(go.Scatter(x=filtered_data.index, y=[value]*len(filtered_data), 
                                 mode='lines', name=f'Fib {level}', line=dict(dash='dash')))

# Add layout and style
fig.update_layout(title="Bitcoin Candlestick Chart with Technical Indicators",
                  xaxis_title="Date", yaxis_title="Price",
                  template='plotly_dark')

# Render the chart in Streamlit
st.plotly_chart(fig, use_container_width=True)

# Display statistics
st.subheader("Summary Statistics")
st.write(filtered_data.describe())

# Option to display raw data
if st.sidebar.checkbox("Show Raw Data"):
    st.subheader("Raw BTC Data")
    st.write(filtered_data)

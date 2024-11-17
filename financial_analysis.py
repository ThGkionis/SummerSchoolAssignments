import streamlit as st
from openai import OpenAI
import yfinance as yf
from datetime import date

# Replace "your_api_key_here" with your actual OpenAI API key
client = OpenAI(api_key="your_api_key_here")

st.title('Interactive Financial Stock Market Comparative Analysis Tool with Enhanced Sentiment Analysis')


# Function to fetch stock data
def get_stock_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data


# Function to analyze sentiment using OpenAI with context
def analyze_sentiment(text, stock_data):
    # Include stock's recent performance summary for context in sentiment analysis
    recent_performance = stock_data.describe().to_string()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a financial sentiment analysis tool with enhanced capabilities. Use the stock's recent performance as context."},
            {"role": "user",
             "content": f"Analyze the sentiment of this text: {text} considering this recent stock performance: {recent_performance}"}
        ]
    )
    response_message = response.choices[0].message.content
    return response_message


# Sidebar for user inputs
st.sidebar.header('User Input Options')
selected_stock = st.sidebar.text_input('Enter Stock Ticker 1', 'AAPL').upper()
selected_stock2 = st.sidebar.text_input('Enter Stock Ticker 2', 'GOOGL').upper()
start_date = st.sidebar.date_input('Start Date', date(2024, 1, 1))
end_date = st.sidebar.date_input('End Date', date(2024, 2, 1))

# Fetch stock data
stock_data = get_stock_data(selected_stock, start_date, end_date)
stock_data2 = get_stock_data(selected_stock2, start_date, end_date)

col1, col2 = st.columns(2)

# Display stock data with enhanced chart options
chart_types = ['Line', 'Bar', 'Area', 'Histogram']

with col1:
    st.subheader(f"Displaying data for: {selected_stock}")
    st.write(stock_data)
    chart_type = st.sidebar.selectbox(f'Select Chart Type for {selected_stock}', chart_types)

    if chart_type == 'Line':
        st.line_chart(stock_data['Close'])
    elif chart_type == 'Bar':
        st.bar_chart(stock_data['Close'])
    elif chart_type == 'Area':
        st.area_chart(stock_data['Close'])
    elif chart_type == 'Histogram':
        st.bar_chart(stock_data['Volume'])

with col2:
    st.subheader(f"Displaying data for: {selected_stock2}")
    st.write(stock_data2)
    chart_type2 = st.sidebar.selectbox(f'Select Chart Type for {selected_stock2}', chart_types)

    if chart_type2 == 'Line':
        st.line_chart(stock_data2['Close'])
    elif chart_type2 == 'Bar':
        st.bar_chart(stock_data2['Close'])
    elif chart_type2 == 'Area':
        st.area_chart(stock_data2['Close'])
    elif chart_type2 == 'Histogram':
        st.bar_chart(stock_data2['Volume'])

# Sentiment Analysis Section
st.header('Enhanced Sentiment Analysis')

# Analyze sentiment based on the stock performance
sentiment1 = analyze_sentiment(f"Analyzing sentiment for {selected_stock}", stock_data)
sentiment2 = analyze_sentiment(f"Analyzing sentiment for {selected_stock2}", stock_data2)

st.subheader(f"Sentiment Analysis for {selected_stock}")
st.write(f"Sentiment: {sentiment1}")

st.subheader(f"Sentiment Analysis for {selected_stock2}")
st.write(f"Sentiment: {sentiment2}")

# Display additional financial metrics
st.sidebar.header("Additional Financial Metrics")
show_ratios = st.sidebar.checkbox("Show Financial Ratios", value=True)
show_technical_indicators = st.sidebar.checkbox("Show Technical Indicators", value=True)

if show_ratios:
    st.header(f"Financial Ratios for {selected_stock} and {selected_stock2}")
    ticker1_info = yf.Ticker(selected_stock).info
    ticker2_info = yf.Ticker(selected_stock2).info

    st.subheader(f"{selected_stock} Ratios")
    st.write(f"P/E Ratio: {ticker1_info.get('forwardPE', 'N/A')}")
    st.write(f"Dividend Yield: {ticker1_info.get('dividendYield', 'N/A')}")
    st.write(f"Market Cap: {ticker1_info.get('marketCap', 'N/A')}")

    st.subheader(f"{selected_stock2} Ratios")
    st.write(f"P/E Ratio: {ticker2_info.get('forwardPE', 'N/A')}")
    st.write(f"Dividend Yield: {ticker2_info.get('dividendYield', 'N/A')}")
    st.write(f"Market Cap: {ticker2_info.get('marketCap', 'N/A')}")

if show_technical_indicators:
    st.header(f"Technical Indicators for {selected_stock} and {selected_stock2}")

    st.subheader(f"{selected_stock} SMA and EMA")
    stock_data['SMA'] = stock_data['Close'].rolling(window=20).mean()
    stock_data['EMA'] = stock_data['Close'].ewm(span=20, adjust=False).mean()
    st.line_chart(stock_data[['Close', 'SMA', 'EMA']])

    st.subheader(f"{selected_stock2} SMA and EMA")
    stock_data2['SMA'] = stock_data2['Close'].rolling(window=20).mean()
    stock_data2['EMA'] = stock_data2['Close'].ewm(span=20, adjust=False).mean()
    st.line_chart(stock_data2[['Close', 'SMA', 'EMA']])

# Comparative Performance using OpenAI
if st.button('Comparative Performance'):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "You are a financial assistant that will retrieve two tables of financial market data and will summarize the comparative performance in text, with a detailed analysis of each stock, key highlights, and a markdown-formatted conclusion."},
            {"role": "user",
             "content": f"This is the {selected_stock} stock data : {stock_data.to_string()}, this is {selected_stock2} stock data: {stock_data2.to_string()}"}
        ]
    )
    completion_message = response.choices[0].message.content
    st.markdown(completion_message)

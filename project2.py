import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Set Streamlit app title
st.title('Stock Portfolio History')

# Function to fetch historical stock data
def get_stock_data(stock, start_date, end_date):
    data = yf.Ticker(stock)
    df = data.history(period="1d", start=start_date, end=end_date)
    return df

# Create Streamlit UI elements for user input
st.sidebar.header("Add Stocks to Your Portfolio")
stock_name = st.sidebar.text_input("Stock Name (e.g., AAPL):")
stock_quantity = st.sidebar.number_input("Quantity:", min_value=1)
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date", pd.Timestamp.today())

if st.sidebar.button("Add to Portfolio"):
    st.session_state.portfolio.append({
        "Stock Name": stock_name,
        "Quantity": stock_quantity,
        "Start Date": start_date,
        "End Date": end_date
    })
    st.sidebar.text("Stock added to your portfolio.")

# Initialize the portfolio in the session state
if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

# Main content
st.header("Stock Portfolio History")

# Display stock portfolio
if len(st.session_state.portfolio) > 0:
    stock_data_combined = pd.concat([get_stock_data(item["Stock Name"], start_date, end_date)['Close'] for item in st.session_state.portfolio], axis=1)
    stock_data_combined.columns = [item["Stock Name"] for item in st.session_state.portfolio]

    fig_individual_stocks = go.Figure()

    for column in stock_data_combined.columns:
        fig_individual_stocks.add_trace(go.Scatter(x=stock_data_combined.index, y=stock_data_combined[column], mode='lines', name=column))

    fig_individual_stocks.update_layout(title='Individual Stock Prices')
    fig_individual_stocks.update_xaxes(title_text='Date')
    fig_individual_stocks.update_yaxes(title_text='Stock Price')

    st.plotly_chart(fig_individual_stocks)

    # Create a pie chart to show portfolio overview
    total_value = stock_data_combined.iloc[-1].sum()
    portfolio_overview = stock_data_combined.iloc[-1] / total_value * 100

    pie_chart = px.pie(
        names=portfolio_overview.index,
        values=portfolio_overview.values,
        title="Portfolio Overview",
    )
    st.plotly_chart(pie_chart)

    # Create an overview table and display the total portfolio value
    overview_data = []
    for stock_name in stock_data_combined.columns:
        stock_quantity = st.session_state.portfolio[stock_data_combined.columns.get_loc(stock_name)]["Quantity"]
        current_price = stock_data_combined[stock_name].iloc[-1]
        value = round(current_price * stock_quantity, 2)
        overview_data.append([stock_name, stock_quantity, current_price, value])

    st.subheader("Portfolio Overview Table")
    st.table(pd.DataFrame(overview_data, columns=["Stock Name", "Quantity", "Current Price", "Value"]))

    st.subheader("Total Portfolio Value")
    st.write(f"Total Portfolio Value: ${total_value:.2f}")

    # Line graph for the total portfolio value
    total_portfolio_value = stock_data_combined.sum(axis=1)
    fig_total_portfolio_value = go.Figure()
    fig_total_portfolio_value.add_trace(go.Scatter(x=stock_data_combined.index, y=total_portfolio_value, mode='lines', name='Total Portfolio Value'))
    fig_total_portfolio_value.update_layout(title='Total Portfolio Value Over Time')
    fig_total_portfolio_value.update_xaxes(title_text='Date')
    fig_total_portfolio_value.update_yaxes(title_text='Total Portfolio Value')
    st.plotly_chart(fig_total_portfolio_value)

# Clear Portfolio button
if st.button("Clear Portfolio"):
    st.session_state.portfolio = []
    st.sidebar.text("Portfolio cleared.")

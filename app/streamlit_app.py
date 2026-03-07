import os
import sys
import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data import fetch_price_data

st.set_page_config(page_title="Portfolio Risk Assessment", layout="wide")

st.title("📊 Automated Risk Assessment Tool")
st.caption("Upload a portfolio CSV (ticker, weight).")

st.sidebar.header("Upload Portfolio")
uploaded = st.sidebar.file_uploader("Portfolio CSV", type=["csv"])

sample_path = Path("data/sample_portfolio.csv")
use_sample = st.sidebar.checkbox("Use sample portfolio", value=(uploaded is None))

df = None
if uploaded is not None and not use_sample:
    df = pd.read_csv(uploaded)
elif sample_path.exists():
    df = pd.read_csv(sample_path)

if df is None:
    st.info("Upload a CSV or enable 'Use sample portfolio'.")
    st.stop()

st.subheader("📌 Portfolio Input")
st.dataframe(df, use_container_width=True)

df.columns = [c.lower().strip() for c in df.columns]

required_cols = {"ticker", "weight"}
if not required_cols.issubset(df.columns):
    st.error("CSV must contain columns: ticker, weight")
    st.stop()

st.success("Portfolio loaded successfully ✅")
# ===============================
# Fetch and Display Price Data
# ===============================

tickers = df["ticker"].tolist()

st.subheader("📈 Fetching Historical Price Data")

try:
    price_data = fetch_price_data(tickers)

    st.success("Historical data fetched successfully ✅")

    # 🔍 Debug
    st.subheader("🔍 Data Points Per Ticker")
    data_points = price_data.notna().sum().rename("data_points")
    st.write(data_points)
    returns = price_data.pct_change().dropna()
    

    # 📊 Normalize prices
    normalized_data = price_data / price_data.iloc[0] * 100
   

    # --- Volatility (Annualized) ---
    # Daily volatility = std of daily returns
    # Annualized volatility = daily vol * sqrt(252 trading days)
    if returns.empty:
        st.warning("Not enough data to calculate volatility yet.")
    else:
        vol_annual = returns.std() * np.sqrt(252)

        st.subheader("Volatility (Annualized Risk)")
        st.dataframe(vol_annual.rename("Volatility"))

    st.subheader("📊 Daily Returns (First 5 rows)")
    st.write(returns.head())
    # ===============================
    # 💼 Portfolio Weighted Returns
    # ===============================

    weights = df.set_index("ticker")["weight"]

    # Ensure correct order
    weights = weights.loc[returns.columns]
    # Covariance matrix
    cov_matrix = returns.cov()

    # Portfolio volatility
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


    portfolio_returns = returns.dot(weights)
    # ==============================
    # 📈 Cumulative Growth (Assets + Portfolio)
    # ==============================

    asset_cum = (1 + returns).cumprod()
    portfolio_cum = (1 + portfolio_returns).cumprod()

    st.subheader("📈 Cumulative Growth (Assets)")
    st.line_chart(asset_cum)

    st.subheader("📈 Cumulative Growth (Portfolio)")
    st.line_chart(portfolio_cum)
    # ==============================
    # 📊 Portfolio Volatility (Covariance Matrix)
    # ==============================

    cov_matrix = returns.cov()  

    portfolio_volatility = np.sqrt(
        weights.T @ cov_matrix @ weights
    )
    annual_portfolio_volatility = portfolio_volatility * np.sqrt(252)

    st.subheader("📊 Portfolio Volatility (Annualized)")
    st.write(annual_portfolio_volatility)

    st.subheader("📈 Portfolio Daily Returns")
    st.write(portfolio_returns.rename("portfolio_return").head())
    # 95% Value at Risk (VaR)
    var_95 = portfolio_returns.quantile(0.05)
    cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
    # ===============================
    # 🚀 Portfolio Cumulative Growth
    # ===============================

    portfolio_cumulative = (1 + portfolio_returns).cumprod()

    st.subheader("🚀 Portfolio Cumulative Performance")
    st.line_chart(portfolio_cumulative)

    st.subheader("📊 Normalized Price Chart (Base = 100)")
    st.line_chart(normalized_data)
    # ===============================
    # 📌 Summary Metrics
    # ===============================
    st.subheader("📌 Summary Metrics")

    trading_days = 252

    avg_daily = portfolio_returns.mean()
    vol_daily = portfolio_returns.std()

    annual_return = avg_daily * trading_days
    annual_vol = vol_daily * (trading_days ** 0.5)

    # risk-free assumed 0 for now
    sharpe = (annual_return / annual_vol) if annual_vol != 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📈 Annual Return", f"{annual_return*100:.2f}%")
    col2.metric("📉 Annual Volatility", f"{annual_vol*100:.2f}%")
    col3.metric("⚡ Sharpe Ratio (rf=0)", f"{sharpe:.2f}")
    col4.metric("⚠️ 95% VaR (Daily)", f"{var_95*100:.2f}%")
    col5.metric("🚨 95% CVaR (Daily)", f"{cvar_95*100:.2f}%")

except Exception as e:
    st.error(f"Error fetching data: {e}")
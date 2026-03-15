import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data import fetch_price_data

st.set_page_config(page_title="Portfolio Risk Assessment", layout="wide")

st.title("Automated Risk Assessment Tool")
st.caption("Upload a portfolio CSV (ticker, weight).")

st.sidebar.header("Upload Portfolio")
uploaded = st.sidebar.file_uploader("Portfolio CSV", type=["csv"])

sample_path = Path("data/sample_portfolio.csv")
use_sample = st.sidebar.checkbox("Use sample portfolio", value=(uploaded is None))
risk_free_rate = st.sidebar.number_input(
    "Risk Free Rate (%)",
    min_value=0.0,
    max_value=20.0,
    value=4.0
)
risk_free_rate = risk_free_rate / 100

df = None
if uploaded is not None and not use_sample:
    df = pd.read_csv(uploaded)
elif sample_path.exists():
    df = pd.read_csv(sample_path)

if df is None:
    st.info("Upload a CSV or enable 'Use sample portfolio'.")
    st.stop()

st.subheader("Portfolio Input")
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

st.subheader("Fetching Historical Price Data")

price_data = fetch_price_data(tickers)

st.success("Historical data fetched successfully ✅")

# Debug
st.subheader("Data Points Per Ticker")
data_points = price_data.notna().sum().rename("data_points")
st.write(data_points)
returns = price_data.pct_change().dropna()
    

# Normalize prices
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

st.subheader("Daily Returns (First 5 rows)")
st.write(returns.head())
# ===============================
# Portfolio Weighted Returns
# ===============================

weights = df.set_index("ticker")["weight"]

# Ensure correct order
weights = weights.loc[returns.columns]
# Covariance matrix
cov_matrix = returns.cov()

# Portfolio volatility
portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))


portfolio_returns = returns.dot(weights)
portfolio_return = portfolio_returns.mean() * 252
# ==============================
# Cumulative Growth (Assets + Portfolio)
# ==============================

asset_cum = (1 + returns).cumprod()
portfolio_cum = (1 + portfolio_returns).cumprod()

st.subheader("Cumulative Growth (Assets)")
st.line_chart(asset_cum)

st.subheader("Cumulative Growth (Portfolio)")
st.line_chart(portfolio_cum)
# ==============================
# Portfolio Volatility (Covariance Matrix)
# ==============================

cov_matrix = returns.cov()  

portfolio_volatility = np.sqrt(
    weights.T @ cov_matrix @ weights
    )
annual_portfolio_volatility = portfolio_volatility * np.sqrt(252)
sharpe_ratio = (portfolio_return - risk_free_rate) / annual_portfolio_volatility

st.subheader("Portfolio Volatility (Annualized)")
st.write(annual_portfolio_volatility)
st.subheader("Sharpe Ratio")
st.write(sharpe_ratio)
if sharpe_ratio < 1:
    st.warning("Poor risk-adjusted return")
elif sharpe_ratio < 2:
    st.info("Good risk-adjusted return")
elif sharpe_ratio < 3:
    st.success("Very good risk-adjusted return")
else:
    st.success("Excellent risk-adjusted return")

st.subheader("Portfolio Daily Returns")
st.write(portfolio_returns.rename("portfolio_return").head())
# 95% Value at Risk (VaR)
var_95 = portfolio_returns.quantile(0.05)
cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
st.subheader("Risk Metrics")
st.write(f"95% Value at Risk (VaR): {var_95:.2%}")
st.write(f"95% Conditional Value at Risk (CVaR): {cvar_95:.2%}")
st.info(f"VaR means that on the worst 5% of days, the portfolio could lose about {abs(var_95):.2%} or more.")
st.warning(f"CVaR means that during those worst-case days, the average loss could be around {abs(cvar_95):.2%}.")

col1, col2, col3 = st.columns(3)

col1.metric("Expected Return", f"{portfolio_return:.2%}")
col2.metric("Volatility", f"{portfolio_volatility:.2%}")
col3.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")

st.subheader("Portfolio Insights")

# Risk interpretation
if portfolio_volatility < 0.15:
    risk_level = "Low"
elif portfolio_volatility < 0.30:
    risk_level = "Moderate"
else:
    risk_level = "High"

# Sharpe ratio interpretation
if sharpe_ratio < 0.5:
    sharpe_comment = "Weak risk-adjusted return"
elif sharpe_ratio < 1.0:
    sharpe_comment = "Decent risk-adjusted return"
else:
    sharpe_comment = "Strong risk-adjusted return"

# Diversification interpretation
if len(tickers) >= 5:
    diversification_comment = "Good diversification across assets"
elif len(tickers) >= 3:
    diversification_comment = "Moderate diversification"
else:
    diversification_comment = "Limited diversification"

st.write(f"**Risk Level:** {risk_level}")
st.write(f"**Sharpe Ratio Insight:** {sharpe_comment}")
st.write(f"**Diversification Insight:** {diversification_comment}")

# ===============================
# Portfolio Cumulative Growth
# ===============================

    
portfolio_cumulative = (1 + portfolio_returns).cumprod()

st.subheader("Portfolio Cumulative Performance")
st.line_chart(portfolio_cumulative)

st.subheader("Normalized Price Chart (Base = 100)")
st.line_chart(normalized_data)

st.subheader("Portfolio Allocation")

allocation_data = df.set_index("ticker")["weight"]

fig, ax = plt.subplots()
ax.pie(allocation_data, labels=allocation_data.index, autopct="%1.1f%%")
ax.axis("equal")

st.pyplot(fig)
    
st.subheader("Asset Correlation Heatmap")

correlation_matrix = returns.corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)

st.pyplot(fig)
    
st.subheader("Efficient Frontier Simulation")

num_portfolios = 500

results = []
weights_list = []

for _ in range(num_portfolios):

    weights = np.random.random(len(df))
    weights /= np.sum(weights)

    portfolio_return = np.sum(returns.mean() * weights) * 252

    portfolio_volatility = np.sqrt(
    np.dot(weights.T, np.dot(returns.cov() * 252, weights))
    )

    sharpe = portfolio_return / portfolio_volatility

    results.append([portfolio_volatility, portfolio_return, sharpe])
    weights_list.append(weights)

results = np.array(results)

fig, ax = plt.subplots()

scatter = ax.scatter(
    results[:, 0],
    results[:, 1],
    c=results[:, 2],
    cmap="viridis"
)

ax.set_xlabel("Volatility (Risk)")
ax.set_ylabel("Return")
ax.set_title("Efficient Frontier")

fig.colorbar(scatter, label="Sharpe Ratio")

st.pyplot(fig)

st.subheader("Efficient Frontier Simulation")

num_portfolios = 500

results = []
weights_list = []

for _ in range(num_portfolios):

    weights = np.random.random(len(df))
    weights /= np.sum(weights)

    portfolio_return = np.sum(returns.mean() * weights) * 252

    portfolio_volatility = np.sqrt(
    np.dot(weights.T, np.dot(returns.cov() * 252, weights))
    )

sharpe = portfolio_return / portfolio_volatility

results.append([portfolio_volatility, portfolio_return, sharpe])
weights_list.append(weights)  
results = np.array(results)

fig, ax = plt.subplots()

scatter = ax.scatter(
    results[:,0],
    results[:,1],
    c=results[:,2],
    cmap="viridis"
)

ax.set_xlabel("Volatility (Risk)")
ax.set_ylabel("Return")
ax.set_title("Efficient Frontier")

fig.colorbar(scatter, label="Sharpe Ratio")

st.pyplot(fig)
# ===============================
# Summary Metrics
# ===============================
st.subheader("Summary Metrics")

trading_days = 252

avg_daily = portfolio_returns.mean()
vol_daily = portfolio_returns.std()

annual_return = avg_daily * trading_days
annual_vol = vol_daily * (trading_days ** 0.5)

# risk-free assumed 0 for now
sharpe = (annual_return / annual_vol) if annual_vol != 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Annual Return", f"{annual_return*100:.2f}%")
col2.metric("Annual Volatility", f"{annual_vol*100:.2f}%")
col3.metric("Sharpe Ratio (rf=0)", f"{sharpe:.2f}")
col4.metric("95% VaR (Daily)", f"{var_95*100:.2f}%")
col5.metric("95% CVaR (Daily)", f"{cvar_95*100:.2f}%")

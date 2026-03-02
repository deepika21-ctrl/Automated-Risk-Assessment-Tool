import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Portfolio Risk Assessment", layout="wide")

st.title("📊 Automated Risk Assessment Tool (Week 1 MVP)")
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
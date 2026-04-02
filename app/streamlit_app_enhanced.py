"""
Enhanced Automated Risk Assessment Tool
Integrates LLM scenario generation, optimization, and Monte Carlo simulation
"""
import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.data import fetch_price_data
from core.config import Config
from core.optimization import PortfolioOptimizer, calculate_risk_metrics
from core.llm_integration import ScenarioGenerator
from core.monte_carlo import MonteCarloSimulator, calculate_max_drawdown, calculate_sortino_ratio

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RiskOS | Portfolio Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Global CSS – dark gamey theme ──────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;900&family=Inter:wght@300;400;600&display=swap');

  /* Base */
  html, body, [class*="css"] {
    background-color: #05080f !important;
    color: #c8d6e5 !important;
    font-family: 'Inter', sans-serif !important;
  }
  .stApp { background: #05080f; }

  /* Hide streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  /* Kill ALL top padding so the login logo sits at the very top-centre */
  .block-container { padding: 0 2.5rem 3rem !important; }
  /* Also strip the inner stVerticalBlock gap that adds extra space */
  .stVerticalBlock { gap: 0 !important; }

  /* ── LOGIN PAGE ── */
  /* Full-screen centred column for all login content */
  .login-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;      /* use full viewport height */
    margin-top: -3rem;      /* pull up past block-container padding */
    gap: 0;
    text-align: center;     /* centre all inline/text children */
  }
  .login-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.2rem; font-weight: 900;
    background: linear-gradient(135deg, #00d2ff, #7b2ff7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 5px; margin-bottom: .4rem;
  }
  .login-subtitle {
    color: #3a5a7a; font-size: .75rem; letter-spacing: 3px;
    text-transform: uppercase; margin-bottom: 2.5rem;
  }
  /* Card that holds the form — sits directly below subtitle */
  .login-card {
    background: linear-gradient(160deg, #0c1828 0%, #080e1c 100%);
    border: 1px solid #1a3050;
    border-radius: 18px;
    padding: 2rem 2.4rem 1.8rem;
    width: 340px;
    text-align: center;
    box-shadow: 0 0 80px rgba(0,210,255,.07),
                0 0 1px rgba(123,47,247,.4),
                inset 0 1px 0 rgba(255,255,255,.04);
    animation: fadeSlideUp .5s ease forwards;
  }
  .login-card h4 {
    color: #c8d6e5;
    font-family: 'Orbitron', sans-serif;
    font-size: .8rem; letter-spacing: 2px;
    margin-bottom: 1rem;
  }
  /* Shrink the username / password inputs to 75% width, centred */
  .login-card .stTextInput { width: 75% !important; margin: 0 auto !important; }
  .login-card .stTextInput > label { font-size: .72rem !important; color: #4a6a8a !important; }
  .login-card .stTextInput > div > div > input {
    font-size: .8rem !important; padding: .35rem .7rem !important;
    height: 34px !important;
  }
  /* ── PAGE TRANSITION  ── */
  /* Prevents the raw white flash when streamlit rerenders */
  [data-stale] .stApp, .stApp[data-stale] {
    animation: fadeTransition .35s ease;
  }
  @keyframes fadeTransition {
    0%   { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
  }

  /* ── HEADER ── */
  .page-header {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.9rem; font-weight: 700;
    background: linear-gradient(90deg, #00d2ff 0%, #7b2ff7 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: 3px; padding-bottom: .25rem;
    border-bottom: 1px solid #1a3050; margin-bottom: 1.5rem;
  }
  .page-tagline {
    color: #4a6a8a; font-size: .8rem; letter-spacing: 1.5px;
    text-transform: uppercase; margin-top: -.5rem; margin-bottom: 1.5rem;
  }

  /* ── SECTION BADGES ── */
  .section-badge {
    display: inline-block;
    font-family: 'Orbitron', sans-serif;
    font-size: .65rem; font-weight: 600; letter-spacing: 2px;
    text-transform: uppercase; padding: .25rem .75rem;
    background: rgba(0,210,255,.08); border: 1px solid rgba(0,210,255,.3);
    border-radius: 20px; color: #00d2ff; margin-bottom: .75rem;
  }

  /* ── METRIC CARDS ── */
  .metric-grid { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
  .m-card {
    flex: 1; min-width: 130px;
    background: linear-gradient(145deg, #0d1a2a, #0a1020);
    border: 1px solid #1a3050; border-radius: 12px;
    padding: 1rem 1.2rem; position: relative; overflow: hidden;
    transition: border-color .3s;
  }
  .m-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #00d2ff, #7b2ff7);
  }
  .m-card:hover { border-color: #00d2ff80; }
  .m-label {
    font-size: .68rem; color: #4a6a8a; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: .3rem;
  }
  .m-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.3rem; font-weight: 600; color: #e0f0ff;
  }
  .m-value.positive { color: #00e676; }
  .m-value.negative { color: #ff5252; }
  .m-value.neutral  { color: #00d2ff; }

  /* ── STATUS BARS ── */
  .status-bar {
    border-radius: 8px; padding: .75rem 1.2rem; margin: .75rem 0;
    font-size: .85rem; border-left: 4px solid;
  }
  .status-success { background: rgba(0,230,118,.08); border-color: #00e676; color: #00e676; }
  .status-warning { background: rgba(255,193,7,.08);  border-color: #ffc107; color: #ffc107; }
  .status-danger  { background: rgba(255,82,82,.08);  border-color: #ff5252; color: #ff5252; }
  .status-info    { background: rgba(0,210,255,.08);  border-color: #00d2ff; color: #00d2ff; }

  /* ── PORTFOLIO CONFIG TABLE ── */
  .config-section {
    background: linear-gradient(145deg, #0d1a2a, #0a1020);
    border: 1px solid #1a3050; border-radius: 14px;
    padding: 1.5rem; margin-bottom: 2rem;
  }

  /* ── DIVIDER ── */
  .glow-divider {
    border: none; height: 1px;
    background: linear-gradient(90deg, transparent, #00d2ff44, #7b2ff744, transparent);
    margin: 2rem 0;
  }

  /* ── TABS ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #0a1020 !important; border-radius: 10px;
    border: 1px solid #1a3050; padding: 4px; gap: 0;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important; border-radius: 8px;
    color: #4a6a8a !important; font-family: 'Orbitron', sans-serif;
    font-size: .65rem; letter-spacing: 1.5px; padding: .5rem 1rem;
    transition: all .25s;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #0d2540, #1a0d30) !important;
    color: #00d2ff !important;
    box-shadow: 0 0 12px rgba(0,210,255,.2);
  }
  .stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

  /* ── BUTTONS ── */
  .stButton > button {
    background: linear-gradient(135deg, #0f2744, #1c0a40) !important;
    border: 1px solid #00d2ff55 !important; color: #00d2ff !important;
    font-family: 'Orbitron', sans-serif; font-size: .65rem;
    letter-spacing: 2px; text-transform: uppercase; border-radius: 8px;
    padding: .6rem 1.5rem; transition: all .25s;
  }
  .stButton > button:hover {
    border-color: #00d2ff !important;
    box-shadow: 0 0 20px rgba(0,210,255,.25) !important;
    transform: translateY(-1px);
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00628a, #3a0070) !important;
    border-color: #00d2ff99 !important;
  }

  /* ── INPUTS & SELECTS ── */
  .stTextInput > div > div > input,
  .stNumberInput > div > div > input,
  .stSelectbox > div > div {
    background: #0a1525 !important; border: 1px solid #1a3050 !important;
    color: #c8d6e5 !important; border-radius: 8px !important;
  }
  .stTextInput > div > div > input:focus,
  .stNumberInput > div > div > input:focus {
    border-color: #00d2ff88 !important;
    box-shadow: 0 0 10px rgba(0,210,255,.15) !important;
  }
  .stSlider > div { color: #00d2ff !important; }

  /* ── DATAFRAMES ── */
  .stDataFrame { border-radius: 10px; overflow: hidden; }
  .stDataFrame thead tr th {
    background: #0d1a2a !important; color: #00d2ff !important;
    font-size: .7rem; letter-spacing: 1px; text-transform: uppercase;
    border-bottom: 1px solid #1a3050;
  }
  .stDataFrame tbody tr:nth-child(even) { background: #080e1a; }
  .stDataFrame tbody tr:hover { background: #0d1e33 !important; }

  /* ── PLOTLY override ── */
  .js-plotly-plot { border-radius: 12px; overflow: hidden; }

  /* ── SPINNER ── */
  .stSpinner > div > div {
    border-top-color: #00d2ff !important;
  }

  /* ── SCROLL FADE-IN ANIMATION  ── */
  @keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .fade-in { animation: fadeSlideUp .6s ease forwards; }
  .fade-in-delay-1 { animation: fadeSlideUp .6s ease .1s forwards; opacity:0; }
  .fade-in-delay-2 { animation: fadeSlideUp .6s ease .2s forwards; opacity:0; }
  .fade-in-delay-3 { animation: fadeSlideUp .6s ease .3s forwards; opacity:0; }

  /* ── LOGOUT in corner ── */
  .logout-btn { position: fixed; top: 14px; right: 20px; z-index: 9999; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ════════════════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ════════════════════════════════════════════════════════════════════════════
USERS = {
    "admin":  "riskos2024",
    "shreya": "portfolio123",
    "deepika": "finance2024",
    "demo":   "demo",
}

def login_page():
    # ── outer wrapper centres everything vertically ──────────────────────────
    st.markdown('<div class="login-center">', unsafe_allow_html=True)

    # Logo + subtitle (pure HTML, always centred)
    st.markdown("""
      <div class="login-logo">RISK<span style="color:#7b2ff7">OS</span></div>
      <div class="login-subtitle">Portfolio Intelligence Platform</div>
    """, unsafe_allow_html=True)

    # ── login card (centred via flex parent) ─────────────────────────────────
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown("<h4>⬡ &nbsp;OPERATOR ACCESS</h4>", unsafe_allow_html=True)

    # Username and password inputs live INSIDE the card, below the logo
    username = st.text_input("Username", placeholder="e.g. demo", key="login_user",
                             label_visibility="visible")
    password = st.text_input("Password", placeholder="e.g. demo", type="password",
                             key="login_pass", label_visibility="visible")

    login_clicked = st.button("ENTER  →", key="login_btn", use_container_width=True)
    st.markdown(
        "<p style='text-align:center;color:#253a52;font-size:.68rem;"
        "margin-top:.6rem;letter-spacing:1px;'>Quick start: demo / demo</p>",
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)   # close .login-card
    st.markdown('</div>', unsafe_allow_html=True)   # close .login-center

    if login_clicked:
        if username in USERS and USERS[username] == password:
            st.session_state.authenticated = True
            st.session_state.username = username
            # Brief JS fade-out before rerun so the transition is smooth
            st.markdown(
                "<style>.stApp{animation:fadeTransition .3s ease;}</style>",
                unsafe_allow_html=True
            )
            st.rerun()
        else:
            st.markdown(
                '<div class="status-bar status-danger" style="margin-top:.8rem;">'
                '❌ Invalid credentials — try demo / demo</div>',
                unsafe_allow_html=True
            )

# ════════════════════════════════════════════════════════════════════════════
#  HELPER – dark plotly layout
# ════════════════════════════════════════════════════════════════════════════
DARK_LAYOUT = dict(
    paper_bgcolor="#05080f",
    plot_bgcolor="#05080f",
    font=dict(color="#c8d6e5", family="Inter"),
    xaxis=dict(gridcolor="#0d1a2a", linecolor="#1a3050", zerolinecolor="#1a3050"),
    yaxis=dict(gridcolor="#0d1a2a", linecolor="#1a3050", zerolinecolor="#1a3050"),
)

# ════════════════════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════════════════════
def main_app():
    # Logout button floating top-right
    st.markdown(f"""
    <div class="logout-btn">
      <span style="color:#4a6a8a;font-size:.75rem;margin-right:.5rem;">
        ⬡ {st.session_state.username.upper()}
      </span>
    </div>
    """, unsafe_allow_html=True)
    _, _, logout_col = st.columns([5, 1, .8])
    with logout_col:
        if st.button("⏻ Exit", key="logout"):
            st.session_state.authenticated = False
            st.rerun()

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown('<div class="page-header fade-in">⬡ RISK OS</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-tagline fade-in">AI-Powered Portfolio Intelligence · MPT · Monte Carlo · LLM Scenarios</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    #  SECTION 1 – PORTFOLIO CONFIGURATION  (horizontal)
    # ════════════════════════════════════════════════════════
    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown('<span class="section-badge fade-in-delay-1">⬡ SECTION 01 · PORTFOLIO CONFIGURATION</span>', unsafe_allow_html=True)

    # Row: upload | risk params | simulation params
    cfg_col1, cfg_col2, cfg_col3 = st.columns([1.4, 1.2, 1.2], gap="medium")

    with cfg_col1:
        st.markdown("##### 📁 Data Source")
        uploaded = st.file_uploader("Upload Portfolio CSV", type=["csv"], label_visibility="collapsed")
        sample_path = Path("data/sample_portfolio.csv")
        use_sample = st.checkbox("Use sample portfolio", value=(uploaded is None))

    with cfg_col2:
        st.markdown("##### ⚙️ Risk Parameters")
        risk_free_rate = st.slider("Risk-Free Rate (%)", 0.0, 10.0, 4.0, 0.1) / 100
        confidence_level = st.slider("VaR Confidence (%)", 90, 99, 95, 1) / 100

    with cfg_col3:
        st.markdown("##### 🎲 Simulation Settings")
        num_simulations = st.select_slider("Simulations", [1000, 5000, 10000, 20000], value=10000)
        initial_investment = st.number_input("Initial Investment ($)", 1000, 10_000_000, 100_000, 10_000)

    # Load portfolio
    df = None
    if uploaded is not None and not use_sample:
        df = pd.read_csv(uploaded)
    elif sample_path.exists():
        df = pd.read_csv(sample_path)

    if df is None:
        st.markdown('<div class="status-bar status-info">📤 Upload a CSV file or enable "Use sample portfolio" to begin.</div>', unsafe_allow_html=True)
        st.stop()

    # Clean & validate
    df.columns = [c.lower().strip() for c in df.columns]
    if not {"ticker", "weight"}.issubset(df.columns):
        st.markdown('<div class="status-bar status-danger">❌ CSV must contain columns: ticker, weight</div>', unsafe_allow_html=True)
        st.stop()

    tickers = df["ticker"].tolist()

    # ── Portfolio overview horizontal ──────────────────────────────────────
    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown('<span class="section-badge fade-in-delay-2">⬡ SECTION 02 · PORTFOLIO COMPOSITION</span>', unsafe_allow_html=True)

    tbl_col, pie_col = st.columns([1.6, 1], gap="medium")

    with tbl_col:
        st.markdown("##### 📋 Holdings Table")
        st.dataframe(df, use_container_width=True, height=200)
        st.markdown('<div class="status-bar status-success">✅ Portfolio loaded · {} assets</div>'.format(len(tickers)), unsafe_allow_html=True)

    with pie_col:
        fig_pie = px.pie(df, values='weight', names='ticker', hole=0.5,
                         color_discrete_sequence=px.colors.sequential.Plasma_r)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label',
                               marker=dict(line=dict(color='#05080f', width=2)))
        fig_pie.update_layout(
            **DARK_LAYOUT,
            title=dict(text="Asset Allocation", font=dict(color="#00d2ff", size=13)),
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False,
            height=220,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ════════════════════════════════════════════════════════
    #  FETCH PRICE DATA
    # ════════════════════════════════════════════════════════
    with st.spinner("🔄 Fetching historical price data from Yahoo Finance..."):
        try:
            price_data = fetch_price_data(tickers)
        except Exception as e:
            st.markdown(f'<div class="status-bar status-danger">❌ Error fetching data: {e}</div>', unsafe_allow_html=True)
            st.stop()

    returns = price_data.pct_change().dropna()
    weights = df.set_index("ticker")["weight"].loc[returns.columns].values

    # Portfolio-level annual stats (used across tabs)
    portfolio_returns   = returns.dot(weights)
    annual_return       = portfolio_returns.mean() * Config.TRADING_DAYS_PER_YEAR
    annual_volatility   = portfolio_returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
    sharpe_ratio        = (annual_return - risk_free_rate) / annual_volatility
    sortino_ratio       = calculate_sortino_ratio(portfolio_returns, risk_free_rate)
    risk_metrics        = calculate_risk_metrics(portfolio_returns, confidence_level)

    # ════════════════════════════════════════════════════════
    #  SECTION 3 – PERFORMANCE MATRIX  (just below config)
    # ════════════════════════════════════════════════════════
    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown('<span class="section-badge fade-in-delay-3">⬡ SECTION 03 · PERFORMANCE MATRIX</span>', unsafe_allow_html=True)

    def sign_class(val):
        if val > 0: return "positive"
        if val < 0: return "negative"
        return "neutral"

    st.markdown(f"""
    <div class="metric-grid fade-in">
      <div class="m-card">
        <div class="m-label">Annual Return</div>
        <div class="m-value {sign_class(annual_return)}">{annual_return:.2%}</div>
      </div>
      <div class="m-card">
        <div class="m-label">Annual Volatility</div>
        <div class="m-value neutral">{annual_volatility:.2%}</div>
      </div>
      <div class="m-card">
        <div class="m-label">Sharpe Ratio</div>
        <div class="m-value {sign_class(sharpe_ratio)}">{sharpe_ratio:.3f}</div>
      </div>
      <div class="m-card">
        <div class="m-label">Sortino Ratio</div>
        <div class="m-value {sign_class(sortino_ratio)}">{sortino_ratio:.3f}</div>
      </div>
      <div class="m-card">
        <div class="m-label">VaR ({confidence_level:.0%})</div>
        <div class="m-value negative">{risk_metrics['var']:.2%}</div>
      </div>
      <div class="m-card">
        <div class="m-label">CVaR ({confidence_level:.0%})</div>
        <div class="m-value negative">{risk_metrics['cvar']:.2%}</div>
      </div>
      <div class="m-card">
        <div class="m-label">Max Drawdown</div>
        <div class="m-value negative">{risk_metrics['max_drawdown']:.2%}</div>
      </div>
      <div class="m-card">
        <div class="m-label">Skewness</div>
        <div class="m-value neutral">{risk_metrics['skewness']:.3f}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Sharpe quality badge
    if sharpe_ratio < 0:
        badge, badge_class = "UNDERPERFORMING · Negative risk-adjusted returns", "status-danger"
    elif sharpe_ratio < 1:
        badge, badge_class = "ACCEPTABLE · Moderate risk-adjusted returns", "status-warning"
    elif sharpe_ratio < 2:
        badge, badge_class = "GOOD · Solid risk-adjusted returns", "status-success"
    else:
        badge, badge_class = "EXCELLENT · Outstanding risk-adjusted returns 🌟", "status-success"

    st.markdown(f'<div class="status-bar {badge_class}">{badge}</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    #  ANALYSIS TABS (scroll down from metrics)
    # ════════════════════════════════════════════════════════
    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown('<span class="section-badge">⬡ SECTION 04 · ANALYSIS MODULES</span>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊  Analysis",
        "🎯  Optimization",
        "🤖  AI Scenarios",
        "🎲  Monte Carlo",
        "⚠️  Stress Test",
    ])

    # ────────────────────────────────────────────────────────
    # TAB 1 · Current Portfolio Analysis
    # ────────────────────────────────────────────────────────
    with tab1:
        st.markdown('<span class="section-badge">CUMULATIVE PERFORMANCE</span>', unsafe_allow_html=True)
        portfolio_cumulative = (1 + portfolio_returns).cumprod()

        fig_cum = go.Figure()
        fig_cum.add_trace(go.Scatter(
            x=portfolio_cumulative.index, y=portfolio_cumulative.values,
            mode='lines', name='Portfolio',
            fill='tozeroy',
            line=dict(color='#00d2ff', width=2),
            fillcolor='rgba(0,210,255,0.07)'
        ))
        fig_cum.update_layout(**DARK_LAYOUT,
            title=dict(text='Portfolio Cumulative Growth', font=dict(color='#00d2ff')),
            xaxis_title='Date', yaxis_title='Growth Multiple',
            hovermode='x unified', height=380
        )
        st.plotly_chart(fig_cum, use_container_width=True)

        # Asset table
        st.markdown('<span class="section-badge">INDIVIDUAL ASSET PERFORMANCE</span>', unsafe_allow_html=True)
        asset_returns = returns.mean() * Config.TRADING_DAYS_PER_YEAR
        asset_volatility = returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
        asset_df = pd.DataFrame({
            'Ticker': returns.columns,
            'Weight': weights,
            'Annual Return': asset_returns.values,
            'Annual Volatility': asset_volatility.values,
            'Sharpe Ratio': (asset_returns.values - risk_free_rate) / asset_volatility.values
        })
        st.dataframe(
            asset_df.style.format({
                'Weight': '{:.1%}', 'Annual Return': '{:.2%}',
                'Annual Volatility': '{:.2%}', 'Sharpe Ratio': '{:.3f}'
            }).background_gradient(subset=['Sharpe Ratio'], cmap='RdYlGn'),
            use_container_width=True
        )

        # Correlation matrix
        st.markdown('<span class="section-badge">CORRELATION MATRIX</span>', unsafe_allow_html=True)
        corr_matrix = returns.corr()
        fig_corr = px.imshow(
            corr_matrix, text_auto='.2f',
            color_continuous_scale='RdBu_r', aspect='auto'
        )
        fig_corr.update_layout(**DARK_LAYOUT, height=380,
            title=dict(text='Asset Correlation Heatmap', font=dict(color='#00d2ff'))
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ────────────────────────────────────────────────────────
    # TAB 2 · Portfolio Optimization
    # ────────────────────────────────────────────────────────
    with tab2:
        st.markdown('<div class="status-bar status-info">📊 Modern Portfolio Theory · Markowitz Optimization · SLSQP Solver</div>', unsafe_allow_html=True)

        try:
            optimizer = PortfolioOptimizer(returns, risk_free_rate)
            col1, col2 = st.columns(2, gap="medium")

            with col1:
                st.markdown('<span class="section-badge">MAX SHARPE PORTFOLIO</span>', unsafe_allow_html=True)
                with st.spinner("Optimizing..."):
                    max_sharpe = optimizer.optimize_sharpe()
                st.markdown(f'<div class="status-bar status-success">✅ Sharpe: {max_sharpe["sharpe_ratio"]:.3f} · Return: {max_sharpe["return"]:.2%} · Vol: {max_sharpe["volatility"]:.2%}</div>', unsafe_allow_html=True)
                opt_df = pd.DataFrame({
                    'Ticker': max_sharpe['tickers'],
                    'Current': weights,
                    'Optimal': max_sharpe['weights'],
                    'Δ': max_sharpe['weights'] - weights
                })
                st.dataframe(opt_df.style.format({'Current':'{:.1%}','Optimal':'{:.1%}','Δ':'{:+.1%}'}).background_gradient(subset=['Δ'], cmap='RdYlGn'), use_container_width=True)

                fig_opt = px.pie(values=max_sharpe['weights'], names=max_sharpe['tickers'], hole=0.45,
                                 color_discrete_sequence=px.colors.sequential.Plasma_r)
                fig_opt.update_layout(**DARK_LAYOUT, height=250, margin=dict(l=10,r=10,t=30,b=10),
                    title=dict(text="Optimal Allocation", font=dict(color="#00d2ff", size=12)), showlegend=False)
                st.plotly_chart(fig_opt, use_container_width=True)

            with col2:
                st.markdown('<span class="section-badge">MIN VOLATILITY PORTFOLIO</span>', unsafe_allow_html=True)
                with st.spinner("Optimizing..."):
                    min_vol = optimizer.optimize_min_volatility()
                st.markdown(f'<div class="status-bar status-info">✅ Min Vol: {min_vol["volatility"]:.2%} · Sharpe: {min_vol["sharpe_ratio"]:.3f}</div>', unsafe_allow_html=True)
                mv_df = pd.DataFrame({
                    'Ticker': min_vol['tickers'],
                    'Current': weights,
                    'Min Vol': min_vol['weights'],
                    'Δ': min_vol['weights'] - weights
                })
                st.dataframe(mv_df.style.format({'Current':'{:.1%}','Min Vol':'{:.1%}','Δ':'{:+.1%}'}).background_gradient(subset=['Δ'], cmap='RdYlGn'), use_container_width=True)

                fig_mv = px.pie(values=min_vol['weights'], names=min_vol['tickers'], hole=0.45,
                                color_discrete_sequence=px.colors.sequential.Viridis)
                fig_mv.update_layout(**DARK_LAYOUT, height=250, margin=dict(l=10,r=10,t=30,b=10),
                    title=dict(text="Min-Vol Allocation", font=dict(color="#00d2ff", size=12)), showlegend=False)
                st.plotly_chart(fig_mv, use_container_width=True)

            # Efficient Frontier
            st.markdown('<span class="section-badge">EFFICIENT FRONTIER</span>', unsafe_allow_html=True)
            with st.spinner("Generating frontier..."):
                frontier_df = optimizer.efficient_frontier(num_portfolios=50)
                random_df   = optimizer.monte_carlo_portfolios(num_portfolios=2000)

            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(
                x=random_df['Volatility'], y=random_df['Return'], mode='markers', name='Random Portfolios',
                marker=dict(size=4, color=random_df['Sharpe'], colorscale='Plasma',
                            showscale=True, colorbar=dict(title="Sharpe"), opacity=0.5)
            ))
            fig_ef.add_trace(go.Scatter(
                x=frontier_df['Volatility'], y=frontier_df['Return'], mode='lines', name='Efficient Frontier',
                line=dict(color='#00d2ff', width=3)
            ))
            fig_ef.add_trace(go.Scatter(
                x=[annual_volatility], y=[annual_return], mode='markers', name='Current',
                marker=dict(size=14, color='#ffd700', symbol='star', line=dict(color='white', width=1))
            ))
            fig_ef.add_trace(go.Scatter(
                x=[max_sharpe['volatility']], y=[max_sharpe['return']], mode='markers', name='Max Sharpe',
                marker=dict(size=12, color='#00e676', symbol='diamond')
            ))
            fig_ef.add_trace(go.Scatter(
                x=[min_vol['volatility']], y=[min_vol['return']], mode='markers', name='Min Vol',
                marker=dict(size=12, color='#7b2ff7', symbol='square')
            ))
            fig_ef.update_layout(**DARK_LAYOUT,
                title=dict(text='Efficient Frontier', font=dict(color='#00d2ff')),
                xaxis_title='Volatility (Risk)', yaxis_title='Expected Return',
                hovermode='closest', height=520
            )
            st.plotly_chart(fig_ef, use_container_width=True)

        except Exception as e:
            st.markdown(f'<div class="status-bar status-danger">❌ Optimization error: {e}</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────────────
    # TAB 3 · AI Scenario Generation
    # ────────────────────────────────────────────────────────
    with tab3:
        st.markdown('<div class="status-bar status-info">🤖 LLM Powered · Mixtral-8x7B via Hugging Face · Prompt Engineering</div>', unsafe_allow_html=True)

        scenario_gen = ScenarioGenerator()
        if not Config.HUGGINGFACE_API_KEY:
            st.markdown('<div class="status-bar status-warning">⚠️ No HuggingFace API key – using fallback scenarios. Set HUGGINGFACE_API_KEY in .env to enable live AI.</div>', unsafe_allow_html=True)

        scenario_type = st.selectbox("Select Scenario", ["recession","inflation","rate_hike","bull_market","volatility_spike"],
            format_func=lambda x: {"recession":"📉 Economic Recession","inflation":"📈 High Inflation (>5%)",
                "rate_hike":"💰 Interest Rate Hike","bull_market":"🚀 Bull Market",
                "volatility_spike":"⚡ Volatility Spike"}[x]
        )

        a_col, b_col = st.columns(2, gap="medium")
        with a_col:
            if st.button("🎲 Generate Scenario", key="gen_scenario", use_container_width=True):
                with st.spinner("🤖 AI analysing..."):
                    text = scenario_gen.generate_market_scenario(tickers, scenario_type)
                st.markdown("#### 📄 AI-Generated Scenario")
                st.markdown(text)

        with b_col:
            if st.button("🔍 AI Risk Assessment", key="gen_risk", use_container_width=True):
                stats = {'return': annual_return, 'volatility': annual_volatility,
                         'sharpe_ratio': sharpe_ratio, 'max_drawdown': risk_metrics['max_drawdown'],
                         'var': risk_metrics['var']}
                with st.spinner("🤖 AI assessing portfolio..."):
                    interp = scenario_gen.interpret_portfolio_risk(stats, tickers)
                st.markdown("#### 💼 Professional Risk Assessment")
                st.markdown(interp)

    # ────────────────────────────────────────────────────────
    # TAB 4 · Monte Carlo Simulation
    # ────────────────────────────────────────────────────────
    with tab4:
        st.markdown(f'<div class="status-bar status-info">🎲 Running up to {num_simulations:,} correlated paths · Cholesky decomposition</div>', unsafe_allow_html=True)

        mc_sim = MonteCarloSimulator(returns, weights)
        sim_days = st.slider("Time Horizon (days)", 30, 756, 252, 30)

        if st.button("▶️ Run Monte Carlo", type="primary", key="run_mc", use_container_width=False):
            with st.spinner(f"Running {num_simulations:,} simulations..."):
                simulations = mc_sim.simulate_paths(initial_value=initial_investment,
                                                     num_simulations=num_simulations, num_days=sim_days)
                stats_mc = mc_sim.get_simulation_statistics(simulations)
                vc = mc_sim.calculate_var_cvar(simulations, confidence_level, sim_days)

            st.markdown(f"""
            <div class="metric-grid">
              <div class="m-card"><div class="m-label">Mean Value</div><div class="m-value positive">${stats_mc['expected_value']:,.0f}</div></div>
              <div class="m-card"><div class="m-label">Median Value</div><div class="m-value neutral">${stats_mc['percentile_50']:,.0f}</div></div>
              <div class="m-card"><div class="m-label">5th Pctile</div><div class="m-value negative">${stats_mc['percentile_5']:,.0f}</div></div>
              <div class="m-card"><div class="m-label">95th Pctile</div><div class="m-value positive">${stats_mc['percentile_95']:,.0f}</div></div>
              <div class="m-card"><div class="m-label">Mean Return</div><div class="m-value {sign_class(stats_mc['mean_return'])}">{stats_mc['mean_return']:.2%}</div></div>
              <div class="m-card"><div class="m-label">Prob. Profit</div><div class="m-value positive">{stats_mc['probability_profit']:.1%}</div></div>
              <div class="m-card"><div class="m-label">VaR $</div><div class="m-value negative">${abs(vc['var_dollar']):,.0f}</div></div>
              <div class="m-card"><div class="m-label">CVaR $</div><div class="m-value negative">${abs(vc['cvar_dollar']):,.0f}</div></div>
            </div>
            """, unsafe_allow_html=True)

            # Paths chart
            fig_mc = go.Figure()
            for i in range(min(80, num_simulations)):
                fig_mc.add_trace(go.Scatter(y=simulations[i], mode='lines',
                    line=dict(width=0.4, color='rgba(0,210,255,0.15)'), hoverinfo='skip', showlegend=False))
            mean_p = simulations.mean(axis=0)
            p5  = np.percentile(simulations, 5, axis=0)
            p95 = np.percentile(simulations, 95, axis=0)
            fig_mc.add_trace(go.Scatter(y=mean_p, mode='lines', name='Mean', line=dict(color='#ff4081', width=2.5)))
            fig_mc.add_trace(go.Scatter(y=p5,  mode='lines', name='5th Pctile', line=dict(color='#ff9800', width=1.5, dash='dash')))
            fig_mc.add_trace(go.Scatter(y=p95, mode='lines', name='95th Pctile', line=dict(color='#00e676', width=1.5, dash='dash')))
            fig_mc.update_layout(**DARK_LAYOUT,
                title=dict(text=f'Monte Carlo – {num_simulations:,} Paths', font=dict(color='#00d2ff')),
                xaxis_title='Days', yaxis_title='Portfolio Value ($)',
                hovermode='x unified', height=430
            )
            st.plotly_chart(fig_mc, use_container_width=True)

            # Distribution
            final_vals = simulations[:, -1]
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(x=final_vals, nbinsx=60, name='Final Values',
                marker=dict(color='rgba(0,210,255,0.5)', line=dict(color='#00d2ff', width=0.5))))
            fig_dist.add_vline(x=initial_investment, line_dash="dash", line_color="#ff5252",
                annotation_text="Initial", annotation_font_color="#ff5252")
            fig_dist.add_vline(x=stats_mc['expected_value'], line_dash="dash", line_color="#00e676",
                annotation_text="Expected", annotation_font_color="#00e676")
            fig_dist.update_layout(**DARK_LAYOUT, height=340,
                title=dict(text='Distribution of Final Values', font=dict(color='#00d2ff')),
                xaxis_title='Portfolio Value ($)', yaxis_title='Frequency'
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    # ────────────────────────────────────────────────────────
    # TAB 5 · Stress Testing
    # ────────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="status-bar status-warning">⚠️ Extreme scenario stress testing · 1,000 simulations per scenario</div>', unsafe_allow_html=True)

        stress_scenarios = {
            "Market Crash (-30%)":  {t: -0.30 for t in tickers},
            "Tech Selloff":         {t: -0.40 if t in ('AAPL','MSFT','GOOGL') else -0.10 for t in tickers},
            "Bond Crisis":          {t: -0.25 if t in ('TLT','AGG') else -0.05 for t in tickers},
            "Stagflation":          {t: -0.20 for t in tickers},
            "Bull Market (+40%)":   {t:  0.40 for t in tickers},
        }

        if st.button("🧪 Run Stress Tests", type="primary", key="run_stress"):
            mc2 = MonteCarloSimulator(returns, weights)
            with st.spinner("Running stress tests..."):
                stress_results = mc2.stress_test(scenarios=stress_scenarios,
                                                  initial_value=initial_investment, num_simulations=1000)

            st.markdown('<div class="status-bar status-success">✅ All stress scenarios complete</div>', unsafe_allow_html=True)

            dr = stress_results.copy()
            for col_name in ['Mean_Value','Median_Value','Worst_5pct','Best_5pct','Std_Dev']:
                dr[col_name] = dr[col_name].apply(lambda x: f"${x:,.0f}")
            dr['Probability_Loss'] = dr['Probability_Loss'].apply(lambda x: f"{x:.1%}")
            st.dataframe(dr, use_container_width=True)

            # Bar chart
            raw = stress_results.copy()
            fig_str = go.Figure()
            fig_str.add_trace(go.Bar(name='Worst 5%',  x=raw['Scenario'], y=raw['Worst_5pct'], marker_color='#ff5252'))
            fig_str.add_trace(go.Bar(name='Mean',      x=raw['Scenario'], y=raw['Mean_Value'],  marker_color='#00d2ff'))
            fig_str.add_trace(go.Bar(name='Best 5%',   x=raw['Scenario'], y=raw['Best_5pct'],   marker_color='#00e676'))
            fig_str.add_hline(y=initial_investment, line_dash='dash', line_color='#ffd700',
                annotation_text=f"Initial ${initial_investment:,.0f}", annotation_font_color='#ffd700')
            fig_str.update_layout(**DARK_LAYOUT,
                title=dict(text='Portfolio Value Under Stress', font=dict(color='#00d2ff')),
                barmode='group', xaxis_title='Scenario', yaxis_title='Portfolio Value ($)', height=460
            )
            st.plotly_chart(fig_str, use_container_width=True)

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown('<hr class="glow-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align:center;color:#1a3050;font-size:.7rem;letter-spacing:2px;font-family:Orbitron,sans-serif;'>
      RISK OS · AI-POWERED PORTFOLIO INTELLIGENCE · STREAMLIT + SCIPY + KUBERNETES
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
#  ROUTING
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state.authenticated:
    login_page()
else:
    main_app()

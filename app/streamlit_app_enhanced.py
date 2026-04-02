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

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    layout=Config.APP_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🎯 Automated Risk Assessment Tool</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Portfolio Optimization with LLM Scenario Generation & Monte Carlo Simulation**")

# Sidebar - Portfolio Upload
st.sidebar.header("📊 Portfolio Configuration")

uploaded = st.sidebar.file_uploader("Upload Portfolio CSV", type=["csv"])
sample_path = Path("data/sample_portfolio.csv")
use_sample = st.sidebar.checkbox("Use sample portfolio", value=(uploaded is None))

# Risk parameters
st.sidebar.subheader("Risk Parameters")
risk_free_rate = st.sidebar.slider(
    "Risk-Free Rate (%)",
    min_value=0.0,
    max_value=10.0,
    value=4.0,
    step=0.1
) / 100

confidence_level = st.sidebar.slider(
    "VaR Confidence Level (%)",
    min_value=90,
    max_value=99,
    value=95,
    step=1
) / 100

# Monte Carlo settings
st.sidebar.subheader("Simulation Settings")
num_simulations = st.sidebar.select_slider(
    "Number of Simulations",
    options=[1000, 5000, 10000, 20000],
    value=10000
)

initial_investment = st.sidebar.number_input(
    "Initial Investment ($)",
    min_value=1000,
    max_value=10000000,
    value=100000,
    step=10000
)

# Load portfolio
df = None
if uploaded is not None and not use_sample:
    df = pd.read_csv(uploaded)
elif sample_path.exists():
    df = pd.read_csv(sample_path)

if df is None:
    st.info("📤 Upload a CSV file or enable 'Use sample portfolio' to begin.")
    st.stop()

# Clean column names
df.columns = [c.lower().strip() for c in df.columns]

# Validate columns
required_cols = {"ticker", "weight"}
if not required_cols.issubset(df.columns):
    st.error("❌ CSV must contain columns: ticker, weight")
    st.stop()

# Display portfolio
st.subheader("📋 Portfolio Composition")
col1, col2 = st.columns([2, 1])

with col1:
    st.dataframe(df, use_container_width=True)

with col2:
    fig_pie = px.pie(
        df,
        values='weight',
        names='ticker',
        title='Asset Allocation',
        hole=0.4
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

st.success("✅ Portfolio loaded successfully")

# Fetch price data
tickers = df["ticker"].tolist()

with st.spinner("🔄 Fetching historical price data..."):
    try:
        price_data = fetch_price_data(tickers)
        st.success(f"✅ Fetched {len(price_data)} days of historical data")
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        st.stop()

# Calculate returns
returns = price_data.pct_change().dropna()
weights = df.set_index("ticker")["weight"].loc[returns.columns].values

# Create tabs for different analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Current Portfolio Analysis",
    "🎯 Portfolio Optimization",
    "🤖 AI Scenario Generation",
    "🎲 Monte Carlo Simulation",
    "⚠️ Stress Testing"
])

# ==========================================
# TAB 1: Current Portfolio Analysis
# ==========================================
with tab1:
    st.header("Current Portfolio Performance")
    
    # Calculate portfolio metrics
    portfolio_returns = returns.dot(weights)
    
    # Annual metrics
    annual_return = portfolio_returns.mean() * Config.TRADING_DAYS_PER_YEAR
    annual_volatility = portfolio_returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    sortino_ratio = calculate_sortino_ratio(portfolio_returns, risk_free_rate)
    
    # Risk metrics
    risk_metrics = calculate_risk_metrics(portfolio_returns, confidence_level)
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Annual Return", f"{annual_return:.2%}")
    col2.metric("Annual Volatility", f"{annual_volatility:.2%}")
    col3.metric("Sharpe Ratio", f"{sharpe_ratio:.3f}")
    col4.metric("Sortino Ratio", f"{sortino_ratio:.3f}")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("VaR (95%)", f"{risk_metrics['var']:.2%}")
    col6.metric("CVaR (95%)", f"{risk_metrics['cvar']:.2%}")
    col7.metric("Max Drawdown", f"{risk_metrics['max_drawdown']:.2%}")
    col8.metric("Skewness", f"{risk_metrics['skewness']:.3f}")
    
    # Portfolio interpretation
    st.subheader("📈 Portfolio Insights")
    
    if sharpe_ratio < 0:
        risk_class = "danger-box"
        sharpe_comment = "⚠️ Poor risk-adjusted returns - portfolio is underperforming"
    elif sharpe_ratio < 1:
        risk_class = "warning-box"
        sharpe_comment = "⚡ Acceptable risk-adjusted returns"
    elif sharpe_ratio < 2:
        risk_class = "success-box"
        sharpe_comment = "✅ Good risk-adjusted returns"
    else:
        risk_class = "success-box"
        sharpe_comment = "🌟 Excellent risk-adjusted returns"
    
    st.markdown(f'<div class="{risk_class}">{sharpe_comment}</div>', unsafe_allow_html=True)
    
    # Cumulative returns chart
    st.subheader("📊 Cumulative Performance")
    portfolio_cumulative = (1 + portfolio_returns).cumprod()
    
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=portfolio_cumulative.values,
        mode='lines',
        name='Portfolio',
        line=dict(color='#1f77b4', width=2)
    ))
    fig_cum.update_layout(
        title='Portfolio Cumulative Growth',
        xaxis_title='Date',
        yaxis_title='Growth Multiple',
        hovermode='x unified'
    )
    st.plotly_chart(fig_cum, use_container_width=True)
    
    # Asset performance comparison
    st.subheader("📊 Individual Asset Performance")
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
            'Weight': '{:.1%}',
            'Annual Return': '{:.2%}',
            'Annual Volatility': '{:.2%}',
            'Sharpe Ratio': '{:.3f}'
        }).background_gradient(subset=['Sharpe Ratio'], cmap='RdYlGn'),
        use_container_width=True
    )
    
    # Correlation heatmap
    st.subheader("🔗 Asset Correlation Matrix")
    corr_matrix = returns.corr()
    
    fig_corr = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        aspect='auto',
        title='Asset Correlation Heatmap'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ==========================================
# TAB 2: Portfolio Optimization
# ==========================================
with tab2:
    st.header("🎯 Portfolio Optimization")
    
    st.info("📊 Using Modern Portfolio Theory (MPT) to find optimal asset allocations")
    
    try:
        optimizer = PortfolioOptimizer(returns, risk_free_rate)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Maximum Sharpe Ratio Portfolio")
            with st.spinner("Optimizing..."):
                max_sharpe = optimizer.optimize_sharpe()
            
            st.success(f"✅ Optimal Sharpe Ratio: {max_sharpe['sharpe_ratio']:.3f}")
            st.metric("Expected Return", f"{max_sharpe['return']:.2%}")
            st.metric("Expected Volatility", f"{max_sharpe['volatility']:.2%}")
            
            # Display optimal weights
            optimal_weights_df = pd.DataFrame({
                'Ticker': max_sharpe['tickers'],
                'Current Weight': weights,
                'Optimal Weight': max_sharpe['weights'],
                'Change': max_sharpe['weights'] - weights
            })
            
            st.dataframe(
                optimal_weights_df.style.format({
                    'Current Weight': '{:.1%}',
                    'Optimal Weight': '{:.1%}',
                    'Change': '{:+.1%}'
                }).background_gradient(subset=['Change'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            # Pie chart of optimal allocation
            fig_optimal = px.pie(
                values=max_sharpe['weights'],
                names=max_sharpe['tickers'],
                title='Optimal Allocation',
                hole=0.4
            )
            st.plotly_chart(fig_optimal, use_container_width=True)
        
        with col2:
            st.subheader("🛡️ Minimum Volatility Portfolio")
            with st.spinner("Optimizing..."):
                min_vol = optimizer.optimize_min_volatility()
            
            st.success(f"✅ Minimum Volatility: {min_vol['volatility']:.2%}")
            st.metric("Expected Return", f"{min_vol['return']:.2%}")
            st.metric("Sharpe Ratio", f"{min_vol['sharpe_ratio']:.3f}")
            
            # Display min vol weights
            min_vol_weights_df = pd.DataFrame({
                'Ticker': min_vol['tickers'],
                'Current Weight': weights,
                'Min Vol Weight': min_vol['weights'],
                'Change': min_vol['weights'] - weights
            })
            
            st.dataframe(
                min_vol_weights_df.style.format({
                    'Current Weight': '{:.1%}',
                    'Min Vol Weight': '{:.1%}',
                    'Change': '{:+.1%}'
                }).background_gradient(subset=['Change'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            # Pie chart of min vol allocation
            fig_minvol = px.pie(
                values=min_vol['weights'],
                names=min_vol['tickers'],
                title='Minimum Volatility Allocation',
                hole=0.4
            )
            st.plotly_chart(fig_minvol, use_container_width=True)
        
        # Efficient Frontier
        st.subheader("📈 Efficient Frontier")
        
        with st.spinner("Generating efficient frontier..."):
            frontier_df = optimizer.efficient_frontier(num_portfolios=50)
            random_df = optimizer.monte_carlo_portfolios(num_portfolios=2000)
        
        fig_frontier = go.Figure()
        
        # Random portfolios
        fig_frontier.add_trace(go.Scatter(
            x=random_df['Volatility'],
            y=random_df['Return'],
            mode='markers',
            name='Random Portfolios',
            marker=dict(
                size=4,
                color=random_df['Sharpe'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Sharpe Ratio"),
                opacity=0.6
            )
        ))
        
        # Efficient frontier
        fig_frontier.add_trace(go.Scatter(
            x=frontier_df['Volatility'],
            y=frontier_df['Return'],
            mode='lines',
            name='Efficient Frontier',
            line=dict(color='red', width=3)
        ))
        
        # Current portfolio
        current_return = annual_return
        current_vol = annual_volatility
        fig_frontier.add_trace(go.Scatter(
            x=[current_vol],
            y=[current_return],
            mode='markers',
            name='Current Portfolio',
            marker=dict(size=15, color='yellow', symbol='star', line=dict(color='black', width=2))
        ))
        
        # Max Sharpe
        fig_frontier.add_trace(go.Scatter(
            x=[max_sharpe['volatility']],
            y=[max_sharpe['return']],
            mode='markers',
            name='Max Sharpe',
            marker=dict(size=12, color='green', symbol='diamond')
        ))
        
        # Min Volatility
        fig_frontier.add_trace(go.Scatter(
            x=[min_vol['volatility']],
            y=[min_vol['return']],
            mode='markers',
            name='Min Volatility',
            marker=dict(size=12, color='blue', symbol='square')
        ))
        
        fig_frontier.update_layout(
            title='Efficient Frontier & Portfolio Optimization',
            xaxis_title='Volatility (Risk)',
            yaxis_title='Expected Return',
            hovermode='closest',
            height=600
        )
        
        st.plotly_chart(fig_frontier, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Optimization error: {str(e)}")

# ==========================================
# TAB 3: AI Scenario Generation
# ==========================================
with tab3:
    st.header("🤖 AI-Powered Scenario Generation")
    
    st.info("💡 Using Large Language Models to generate market scenarios and risk assessments")
    
    # Initialize scenario generator
    scenario_gen = ScenarioGenerator()
    
    # Check if API key is set
    if not Config.HUGGINGFACE_API_KEY:
        st.warning("⚠️ Hugging Face API key not set. Using fallback scenarios. Set HUGGINGFACE_API_KEY in .env to enable AI generation.")
    
    # Scenario selection
    scenario_type = st.selectbox(
        "Select Scenario Type",
        ["recession", "inflation", "rate_hike", "bull_market", "volatility_spike"]
    )
    
    scenario_names = {
        "recession": "📉 Economic Recession",
        "inflation": "📈 High Inflation (>5%)",
        "rate_hike": "💰 Interest Rate Hike",
        "bull_market": "🚀 Bull Market",
        "volatility_spike": "⚡ Market Volatility Spike"
    }
    
    st.subheader(scenario_names[scenario_type])
    
    if st.button("🎲 Generate Scenario Analysis"):
        with st.spinner("🤖 AI is analyzing market conditions..."):
            scenario_text = scenario_gen.generate_market_scenario(tickers, scenario_type)
        
        st.markdown("### 📄 AI-Generated Analysis")
        st.markdown(scenario_text)
    
    st.divider()
    
    # Portfolio risk interpretation
    st.subheader("🎯 AI Portfolio Risk Interpretation")
    
    if st.button("🔍 Get AI Risk Assessment"):
        portfolio_stats = {
            'return': annual_return,
            'volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': risk_metrics['max_drawdown'],
            'var': risk_metrics['var']
        }
        
        with st.spinner("🤖 AI is analyzing your portfolio..."):
            interpretation = scenario_gen.interpret_portfolio_risk(portfolio_stats, tickers)
        
        st.markdown("### 💼 Professional Risk Assessment")
        st.markdown(interpretation)

# ==========================================
# TAB 4: Monte Carlo Simulation
# ==========================================
with tab4:
    st.header("🎲 Monte Carlo Simulation")
    
    st.info(f"🔢 Running {num_simulations:,} simulations to project portfolio performance")
    
    # Initialize simulator
    mc_simulator = MonteCarloSimulator(returns, weights)
    
    simulation_days = st.slider(
        "Simulation Time Horizon (days)",
        min_value=30,
        max_value=756,
        value=252,
        step=30
    )
    
    if st.button("▶️ Run Monte Carlo Simulation", type="primary"):
        with st.spinner(f"🎲 Running {num_simulations:,} simulations..."):
            simulations = mc_simulator.simulate_paths(
                initial_value=initial_investment,
                num_simulations=num_simulations,
                num_days=simulation_days
            )
            
            stats = mc_simulator.get_simulation_statistics(simulations)
            var_cvar = mc_simulator.calculate_var_cvar(simulations, confidence_level, simulation_days)
        
        st.success(f"✅ Completed {num_simulations:,} simulations")
        
        # Display statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean Portfolio Value", f"${stats['expected_value']:,.0f}")
        col2.metric("Median Value", f"${stats['percentile_50']:,.0f}")
        col3.metric("5th Percentile", f"${stats['percentile_5']:,.0f}")
        col4.metric("95th Percentile", f"${stats['percentile_95']:,.0f}")
        
        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Mean Return", f"{stats['mean_return']:.2%}")
        col6.metric("Probability of Profit", f"{stats['probability_profit']:.1%}")
        col7.metric(f"VaR ({confidence_level:.0%})", f"${abs(var_cvar['var_dollar']):,.0f}")
        col8.metric(f"CVaR ({confidence_level:.0%})", f"${abs(var_cvar['cvar_dollar']):,.0f}")
        
        # Simulation paths visualization
        st.subheader("📊 Simulated Portfolio Paths")
        
        fig_sim = go.Figure()
        
        # Plot a subset of paths
        num_paths_to_plot = min(100, num_simulations)
        for i in range(num_paths_to_plot):
            fig_sim.add_trace(go.Scatter(
                y=simulations[i],
                mode='lines',
                line=dict(width=0.5),
                opacity=0.1,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        # Add mean path
        mean_path = simulations.mean(axis=0)
        fig_sim.add_trace(go.Scatter(
            y=mean_path,
            mode='lines',
            name='Mean Path',
            line=dict(color='red', width=3)
        ))
        
        # Add percentiles
        p5 = np.percentile(simulations, 5, axis=0)
        p95 = np.percentile(simulations, 95, axis=0)
        
        fig_sim.add_trace(go.Scatter(
            y=p5,
            mode='lines',
            name='5th Percentile',
            line=dict(color='orange', width=2, dash='dash')
        ))
        
        fig_sim.add_trace(go.Scatter(
            y=p95,
            mode='lines',
            name='95th Percentile',
            line=dict(color='green', width=2, dash='dash')
        ))
        
        fig_sim.update_layout(
            title=f'Monte Carlo Simulation - {num_simulations:,} Paths',
            xaxis_title='Days',
            yaxis_title='Portfolio Value ($)',
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig_sim, use_container_width=True)
        
        # Distribution of final values
        st.subheader("📊 Distribution of Final Portfolio Values")
        
        final_values = simulations[:, -1]
        
        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=final_values,
            nbinsx=50,
            name='Final Values',
            marker_color='steelblue'
        ))
        
        fig_dist.add_vline(
            x=initial_investment,
            line_dash="dash",
            line_color="red",
            annotation_text="Initial Investment"
        )
        
        fig_dist.add_vline(
            x=stats['expected_value'],
            line_dash="dash",
            line_color="green",
            annotation_text="Expected Value"
        )
        
        fig_dist.update_layout(
            title='Distribution of Final Portfolio Values',
            xaxis_title='Portfolio Value ($)',
            yaxis_title='Frequency',
            showlegend=True
        )
        
        st.plotly_chart(fig_dist, use_container_width=True)

# ==========================================
# TAB 5: Stress Testing
# ==========================================
with tab5:
    st.header("⚠️ Portfolio Stress Testing")
    
    st.info("🔬 Testing portfolio performance under extreme market scenarios")
    
    # Define stress scenarios
    stress_scenarios = {
        "Market Crash (-30%)": {ticker: -0.30 for ticker in tickers},
        "Tech Selloff": {ticker: -0.40 if 'AAPL' in ticker or 'MSFT' in ticker or 'GOOGL' in ticker else -0.10 for ticker in tickers},
        "Bond Crisis": {ticker: -0.25 if 'TLT' in ticker or 'AGG' in ticker else -0.05 for ticker in tickers},
        "Stagflation": {ticker: -0.20 for ticker in tickers},
        "Bull Market (+40%)": {ticker: 0.40 for ticker in tickers}
    }
    
    if st.button("🧪 Run Stress Tests", type="primary"):
        mc_simulator = MonteCarloSimulator(returns, weights)
        
        with st.spinner("🧪 Running stress tests..."):
            stress_results = mc_simulator.stress_test(
                scenarios=stress_scenarios,
                initial_value=initial_investment,
                num_simulations=1000
            )
        
        st.success("✅ Stress testing complete")
        
        # Display results table
        st.subheader("📊 Stress Test Results")
        
        display_results = stress_results.copy()
        display_results['Mean_Value'] = display_results['Mean_Value'].apply(lambda x: f"${x:,.0f}")
        display_results['Median_Value'] = display_results['Median_Value'].apply(lambda x: f"${x:,.0f}")
        display_results['Worst_5pct'] = display_results['Worst_5pct'].apply(lambda x: f"${x:,.0f}")
        display_results['Best_5pct'] = display_results['Best_5pct'].apply(lambda x: f"${x:,.0f}")
        display_results['Std_Dev'] = display_results['Std_Dev'].apply(lambda x: f"${x:,.0f}")
        display_results['Probability_Loss'] = display_results['Probability_Loss'].apply(lambda x: f"{x:.1%}")
        
        st.dataframe(display_results, use_container_width=True)
        
        # Visualization
        st.subheader("📊 Scenario Comparison")
        
        fig_stress = go.Figure()
        
        scenarios_list = stress_results['Scenario'].tolist()
        mean_values = [float(x.replace('$', '').replace(',', '')) for x in display_results['Mean_Value']]
        worst_values = [float(x.replace('$', '').replace(',', '')) for x in display_results['Worst_5pct']]
        best_values = [float(x.replace('$', '').replace(',', '')) for x in display_results['Best_5pct']]
        
        fig_stress.add_trace(go.Bar(
            name='Worst 5%',
            x=scenarios_list,
            y=worst_values,
            marker_color='red'
        ))
        
        fig_stress.add_trace(go.Bar(
            name='Mean',
            x=scenarios_list,
            y=mean_values,
            marker_color='blue'
        ))
        
        fig_stress.add_trace(go.Bar(
            name='Best 5%',
            x=scenarios_list,
            y=best_values,
            marker_color='green'
        ))
        
        fig_stress.add_hline(
            y=initial_investment,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Initial: ${initial_investment:,.0f}"
        )
        
        fig_stress.update_layout(
            title='Portfolio Value Under Stress Scenarios',
            xaxis_title='Scenario',
            yaxis_title='Portfolio Value ($)',
            barmode='group',
            height=500
        )
        
        st.plotly_chart(fig_stress, use_container_width=True)

# Footer
st.divider()
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Automated Risk Assessment Tool</strong> | Powered by AI & Advanced Portfolio Theory</p>
    <p>Built with Streamlit, Scipy, Hugging Face & Kubernetes</p>
</div>
""", unsafe_allow_html=True)

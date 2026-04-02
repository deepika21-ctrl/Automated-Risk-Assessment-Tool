"""
Unit Tests for Automated Risk Assessment Tool
"""
import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Import modules to test
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.optimization import PortfolioOptimizer, calculate_risk_metrics
from core.monte_carlo import MonteCarloSimulator, calculate_max_drawdown, calculate_sortino_ratio
from core.config import Config


# ==========================================
# Fixtures
# ==========================================

@pytest.fixture
def sample_returns():
    """Generate sample return data for testing"""
    np.random.seed(42)
    dates = pd.date_range(start='2022-01-01', periods=252, freq='D')
    
    returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252),
        'MSFT': np.random.normal(0.0008, 0.018, 252),
        'GOOGL': np.random.normal(0.0009, 0.019, 252),
    }, index=dates)
    
    return returns


@pytest.fixture
def sample_weights():
    """Generate sample portfolio weights"""
    return np.array([0.4, 0.35, 0.25])


# ==========================================
# Configuration Tests
# ==========================================

def test_config_validation():
    """Test configuration validation"""
    assert Config.TRADING_DAYS_PER_YEAR == 252
    assert Config.VAR_CONFIDENCE_LEVEL == 0.95
    assert Config.NUM_SIMULATIONS == 10000


def test_config_validate_method():
    """Test Config.validate() method"""
    result = Config.validate()
    assert result == True


# ==========================================
# Portfolio Optimization Tests
# ==========================================

def test_portfolio_optimizer_initialization(sample_returns):
    """Test PortfolioOptimizer initialization"""
    optimizer = PortfolioOptimizer(sample_returns)
    
    assert optimizer.num_assets == 3
    assert len(optimizer.mean_returns) == 3
    assert optimizer.cov_matrix.shape == (3, 3)


def test_portfolio_stats(sample_returns, sample_weights):
    """Test portfolio statistics calculation"""
    optimizer = PortfolioOptimizer(sample_returns)
    ret, vol, sharpe = optimizer.portfolio_stats(sample_weights)
    
    assert isinstance(ret, float)
    assert isinstance(vol, float)
    assert isinstance(sharpe, float)
    assert vol >= 0


def test_optimize_sharpe(sample_returns):
    """Test maximum Sharpe ratio optimization"""
    optimizer = PortfolioOptimizer(sample_returns)
    result = optimizer.optimize_sharpe()
    
    assert 'weights' in result
    assert 'return' in result
    assert 'volatility' in result
    assert 'sharpe_ratio' in result
    
    # Weights should sum to 1
    assert np.isclose(result['weights'].sum(), 1.0)
    
    # All weights should be non-negative
    assert np.all(result['weights'] >= 0)
    
    # Volatility should be positive
    assert result['volatility'] > 0


def test_optimize_min_volatility(sample_returns):
    """Test minimum volatility optimization"""
    optimizer = PortfolioOptimizer(sample_returns)
    result = optimizer.optimize_min_volatility()
    
    assert 'weights' in result
    assert np.isclose(result['weights'].sum(), 1.0)
    assert result['volatility'] > 0


def test_efficient_frontier(sample_returns):
    """Test efficient frontier generation"""
    optimizer = PortfolioOptimizer(sample_returns)
    frontier = optimizer.efficient_frontier(num_portfolios=20)
    
    assert isinstance(frontier, pd.DataFrame)
    assert len(frontier) > 0
    assert 'Return' in frontier.columns
    assert 'Volatility' in frontier.columns
    assert 'Sharpe' in frontier.columns


def test_monte_carlo_portfolios(sample_returns):
    """Test random portfolio generation"""
    optimizer = PortfolioOptimizer(sample_returns)
    random_portfolios = optimizer.monte_carlo_portfolios(num_portfolios=100)
    
    assert len(random_portfolios) == 100
    assert 'Return' in random_portfolios.columns
    assert 'Volatility' in random_portfolios.columns


# ==========================================
# Risk Metrics Tests
# ==========================================

def test_calculate_risk_metrics(sample_returns):
    """Test risk metrics calculation"""
    portfolio_returns = sample_returns.mean(axis=1)
    metrics = calculate_risk_metrics(portfolio_returns)
    
    assert 'var' in metrics
    assert 'cvar' in metrics
    assert 'max_drawdown' in metrics
    assert 'volatility' in metrics
    assert 'skewness' in metrics
    assert 'kurtosis' in metrics
    
    # VaR should be negative (loss)
    assert metrics['var'] <= 0
    
    # CVaR should be more negative than VaR
    assert metrics['cvar'] <= metrics['var']
    
    # Max drawdown should be negative
    assert metrics['max_drawdown'] <= 0


# ==========================================
# Monte Carlo Simulation Tests
# ==========================================

def test_monte_carlo_simulator_initialization(sample_returns, sample_weights):
    """Test MonteCarloSimulator initialization"""
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    assert simulator.num_assets == 3
    assert len(simulator.weights) == 3
    assert np.isclose(simulator.weights.sum(), 1.0)


def test_simulate_paths(sample_returns, sample_weights):
    """Test portfolio path simulation"""
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    initial_value = 100000
    num_sims = 100
    num_days = 252
    
    simulations = simulator.simulate_paths(
        initial_value=initial_value,
        num_simulations=num_sims,
        num_days=num_days
    )
    
    assert simulations.shape == (num_sims, num_days)
    assert np.all(simulations[:, 0] == initial_value)
    assert np.all(simulations > 0)  # Portfolio values should be positive


def test_calculate_var_cvar(sample_returns, sample_weights):
    """Test VaR and CVaR calculation from simulations"""
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    simulations = simulator.simulate_paths(
        initial_value=100000,
        num_simulations=100,
        num_days=252
    )
    
    var_cvar = simulator.calculate_var_cvar(simulations)
    
    assert 'var' in var_cvar
    assert 'cvar' in var_cvar
    assert 'var_dollar' in var_cvar
    assert 'cvar_dollar' in var_cvar
    
    # CVaR should be worse (more negative) than VaR
    assert var_cvar['cvar'] <= var_cvar['var']


def test_get_simulation_statistics(sample_returns, sample_weights):
    """Test simulation statistics calculation"""
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    simulations = simulator.simulate_paths(
        initial_value=100000,
        num_simulations=100,
        num_days=252
    )
    
    stats = simulator.get_simulation_statistics(simulations)
    
    assert 'mean_return' in stats
    assert 'std_return' in stats
    assert 'probability_profit' in stats
    assert 'expected_value' in stats
    
    # Probability should be between 0 and 1
    assert 0 <= stats['probability_profit'] <= 1


def test_stress_test(sample_returns, sample_weights):
    """Test stress testing functionality"""
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    scenarios = {
        "Market Crash": {"AAPL": -0.30, "MSFT": -0.25, "GOOGL": -0.28}
    }
    
    results = simulator.stress_test(
        scenarios=scenarios,
        initial_value=100000,
        num_simulations=50
    )
    
    assert isinstance(results, pd.DataFrame)
    assert len(results) == 1
    assert 'Scenario' in results.columns
    assert 'Mean_Value' in results.columns


# ==========================================
# Helper Function Tests
# ==========================================

def test_calculate_max_drawdown():
    """Test maximum drawdown calculation"""
    portfolio_values = np.array([100, 110, 105, 120, 115, 130, 125])
    
    max_dd = calculate_max_drawdown(portfolio_values)
    
    assert isinstance(max_dd, float)
    assert max_dd <= 0  # Drawdown should be negative


def test_calculate_sortino_ratio(sample_returns):
    """Test Sortino ratio calculation"""
    portfolio_returns = sample_returns.mean(axis=1)
    
    sortino = calculate_sortino_ratio(portfolio_returns)
    
    assert isinstance(sortino, float)


# ==========================================
# Integration Tests
# ==========================================

def test_full_optimization_workflow(sample_returns):
    """Test complete optimization workflow"""
    # Initialize optimizer
    optimizer = PortfolioOptimizer(sample_returns)
    
    # Find max Sharpe portfolio
    max_sharpe = optimizer.optimize_sharpe()
    
    # Find min volatility portfolio
    min_vol = optimizer.optimize_min_volatility()
    
    # Generate efficient frontier
    frontier = optimizer.efficient_frontier(num_portfolios=10)
    
    # Verify max Sharpe has highest Sharpe among optimized portfolios
    assert max_sharpe['sharpe_ratio'] >= min_vol['sharpe_ratio']
    
    # Verify min vol has lowest volatility
    assert min_vol['volatility'] <= max_sharpe['volatility']


def test_full_simulation_workflow(sample_returns, sample_weights):
    """Test complete simulation workflow"""
    # Initialize simulator
    simulator = MonteCarloSimulator(sample_returns, sample_weights)
    
    # Run simulations
    sims = simulator.simulate_paths(
        initial_value=100000,
        num_simulations=50,
        num_days=252
    )
    
    # Calculate metrics
    stats = simulator.get_simulation_statistics(sims)
    var_cvar = simulator.calculate_var_cvar(sims)
    
    # Verify results are reasonable
    assert stats['expected_value'] > 0
    assert -1 <= stats['mean_return'] <= 5  # Reasonable annual return range
    assert var_cvar['var'] < 0  # VaR should represent a loss


# ==========================================
# Edge Case Tests
# ==========================================

def test_single_asset_optimization():
    """Test optimization with single asset (should return 100% weight)"""
    dates = pd.date_range(start='2022-01-01', periods=252, freq='D')
    single_asset_returns = pd.DataFrame({
        'AAPL': np.random.normal(0.001, 0.02, 252)
    }, index=dates)
    
    optimizer = PortfolioOptimizer(single_asset_returns)
    result = optimizer.optimize_sharpe()
    
    assert np.isclose(result['weights'][0], 1.0)


def test_zero_volatility_handling():
    """Test handling of zero volatility (constant returns)"""
    dates = pd.date_range(start='2022-01-01', periods=252, freq='D')
    constant_returns = pd.DataFrame({
        'ASSET': np.zeros(252)
    }, index=dates)
    
    metrics = calculate_risk_metrics(constant_returns['ASSET'])
    
    assert metrics['volatility'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

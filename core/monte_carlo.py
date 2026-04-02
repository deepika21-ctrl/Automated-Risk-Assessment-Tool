"""
Monte Carlo Simulation for Portfolio Stress Testing
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from core.config import Config


class MonteCarloSimulator:
    """
    Run Monte Carlo simulations for portfolio stress testing
    """
    
    def __init__(self, returns: pd.DataFrame, current_weights: np.ndarray):
        """
        Initialize simulator
        
        Args:
            returns: Historical returns DataFrame
            current_weights: Current portfolio weights
        """
        self.returns = returns
        self.weights = current_weights
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()
        self.num_assets = len(returns.columns)
        
    def simulate_paths(self, 
                      initial_value: float = 100000,
                      num_simulations: int = Config.NUM_SIMULATIONS,
                      num_days: int = Config.SIMULATION_DAYS) -> np.ndarray:
        """
        Simulate portfolio value paths
        
        Args:
            initial_value: Starting portfolio value
            num_simulations: Number of simulation paths
            num_days: Number of days to simulate
            
        Returns:
            Array of shape (num_simulations, num_days) with portfolio values
        """
        # Generate correlated random returns
        L = np.linalg.cholesky(self.cov_matrix)
        
        simulations = np.zeros((num_simulations, num_days))
        simulations[:, 0] = initial_value
        
        for sim in range(num_simulations):
            portfolio_value = initial_value
            
            for day in range(1, num_days):
                # Generate correlated random returns
                random_returns = np.random.normal(0, 1, self.num_assets)
                correlated_returns = self.mean_returns.values + L @ random_returns
                
                # Calculate portfolio return
                portfolio_return = np.dot(self.weights, correlated_returns)
                
                # Update portfolio value
                portfolio_value *= (1 + portfolio_return)
                simulations[sim, day] = portfolio_value
        
        return simulations
    
    def calculate_var_cvar(self, 
                          simulations: np.ndarray,
                          confidence_level: float = 0.95,
                          time_horizon: int = 252) -> Dict:
        """
        Calculate VaR and CVaR from simulations
        
        Args:
            simulations: Simulation results
            confidence_level: Confidence level (default 95%)
            time_horizon: Time horizon in days
            
        Returns:
            Dictionary with VaR and CVaR metrics
        """
        final_values = simulations[:, -1]
        initial_value = simulations[0, 0]
        
        # Calculate returns
        returns = (final_values - initial_value) / initial_value
        
        # VaR: percentile of losses
        var = np.percentile(returns, (1 - confidence_level) * 100)
        
        # CVaR: average of losses beyond VaR
        cvar = returns[returns <= var].mean()
        
        return {
            'var': var,
            'cvar': cvar,
            'var_dollar': var * initial_value,
            'cvar_dollar': cvar * initial_value,
            'confidence_level': confidence_level,
            'time_horizon_days': time_horizon
        }
    
    def stress_test(self, 
                   scenarios: Dict[str, Dict],
                   initial_value: float = 100000,
                   num_simulations: int = 1000) -> pd.DataFrame:
        """
        Run stress tests under different scenarios
        
        Args:
            scenarios: Dictionary of scenario adjustments
            initial_value: Starting portfolio value
            num_simulations: Number of simulations per scenario
            
        Returns:
            DataFrame with stress test results
        """
        results = []
        
        for scenario_name, adjustments in scenarios.items():
            # Adjust mean returns based on scenario
            adjusted_mean = self.mean_returns.copy()
            
            for ticker, adjustment in adjustments.items():
                if ticker in adjusted_mean.index:
                    adjusted_mean[ticker] *= (1 + adjustment)
            
            # Run simulation with adjusted parameters
            temp_simulator = MonteCarloSimulator(self.returns, self.weights)
            temp_simulator.mean_returns = adjusted_mean
            
            sims = temp_simulator.simulate_paths(
                initial_value=initial_value,
                num_simulations=num_simulations,
                num_days=252
            )
            
            final_values = sims[:, -1]
            
            results.append({
                'Scenario': scenario_name,
                'Mean_Value': final_values.mean(),
                'Median_Value': np.median(final_values),
                'Worst_5pct': np.percentile(final_values, 5),
                'Best_5pct': np.percentile(final_values, 95),
                'Std_Dev': final_values.std(),
                'Probability_Loss': (final_values < initial_value).mean()
            })
        
        return pd.DataFrame(results)
    
    def get_simulation_statistics(self, simulations: np.ndarray) -> Dict:
        """
        Calculate statistics from simulation results
        
        Args:
            simulations: Array of simulation paths
            
        Returns:
            Dictionary of statistics
        """
        final_values = simulations[:, -1]
        initial_value = simulations[0, 0]
        
        returns = (final_values - initial_value) / initial_value
        
        return {
            'mean_return': returns.mean(),
            'median_return': np.median(returns),
            'std_return': returns.std(),
            'min_return': returns.min(),
            'max_return': returns.max(),
            'probability_profit': (returns > 0).mean(),
            'probability_loss_gt_10pct': (returns < -0.10).mean(),
            'probability_loss_gt_20pct': (returns < -0.20).mean(),
            'expected_value': final_values.mean(),
            'percentile_5': np.percentile(final_values, 5),
            'percentile_25': np.percentile(final_values, 25),
            'percentile_50': np.percentile(final_values, 50),
            'percentile_75': np.percentile(final_values, 75),
            'percentile_95': np.percentile(final_values, 95)
        }
    
    def efficient_frontier_monte_carlo(self,
                                       num_portfolios: int = 5000) -> pd.DataFrame:
        """
        Generate random portfolios for efficient frontier visualization
        
        Args:
            num_portfolios: Number of random portfolios to generate
            
        Returns:
            DataFrame with portfolio statistics
        """
        results = []
        
        annual_return_factor = Config.TRADING_DAYS_PER_YEAR
        
        for _ in range(num_portfolios):
            # Generate random weights
            weights = np.random.random(self.num_assets)
            weights /= np.sum(weights)
            
            # Calculate portfolio metrics
            portfolio_return = np.sum(self.mean_returns * weights) * annual_return_factor
            portfolio_std = np.sqrt(
                np.dot(weights.T, np.dot(self.cov_matrix * annual_return_factor, weights))
            )
            sharpe_ratio = portfolio_return / portfolio_std if portfolio_std > 0 else 0
            
            results.append({
                'Return': portfolio_return,
                'Volatility': portfolio_std,
                'Sharpe': sharpe_ratio,
                'Weights': weights
            })
        
        return pd.DataFrame(results)


def calculate_max_drawdown(portfolio_values: np.ndarray) -> float:
    """
    Calculate maximum drawdown from a series of portfolio values
    
    Args:
        portfolio_values: Array of portfolio values over time
        
    Returns:
        Maximum drawdown as a decimal
    """
    cumulative_max = np.maximum.accumulate(portfolio_values)
    drawdown = (portfolio_values - cumulative_max) / cumulative_max
    return np.min(drawdown)


def calculate_sortino_ratio(returns: pd.Series, 
                            risk_free_rate: float = Config.DEFAULT_RISK_FREE_RATE,
                            target_return: float = 0) -> float:
    """
    Calculate Sortino ratio (similar to Sharpe but only considers downside risk)
    
    Args:
        returns: Series of returns
        risk_free_rate: Risk-free rate
        target_return: Target return threshold
        
    Returns:
        Sortino ratio
    """
    excess_returns = returns - risk_free_rate / Config.TRADING_DAYS_PER_YEAR
    downside_returns = returns[returns < target_return]
    
    if len(downside_returns) == 0:
        return np.inf
    
    downside_std = downside_returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
    
    if downside_std == 0:
        return np.inf
    
    return (excess_returns.mean() * Config.TRADING_DAYS_PER_YEAR) / downside_std

"""
Portfolio Optimization Module
Implements Modern Portfolio Theory (MPT) and efficient frontier calculation
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
from core.config import Config


class PortfolioOptimizer:
    """
    Portfolio optimization using mean-variance optimization (Markowitz)
    """
    
    def __init__(self, returns: pd.DataFrame, risk_free_rate: float = Config.DEFAULT_RISK_FREE_RATE):
        """
        Initialize optimizer with historical returns
        
        Args:
            returns: DataFrame of asset returns
            risk_free_rate: Risk-free rate for Sharpe ratio calculation
        """
        self.returns = returns
        self.risk_free_rate = risk_free_rate
        self.mean_returns = returns.mean() * Config.TRADING_DAYS_PER_YEAR
        self.cov_matrix = returns.cov() * Config.TRADING_DAYS_PER_YEAR
        self.num_assets = len(returns.columns)
        
    def portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio statistics
        
        Returns:
            Tuple of (return, volatility, sharpe_ratio)
        """
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return portfolio_return, portfolio_std, sharpe_ratio
    
    def negative_sharpe(self, weights: np.ndarray) -> float:
        """Negative Sharpe ratio (for minimization)"""
        return -self.portfolio_stats(weights)[2]
    
    def portfolio_volatility(self, weights: np.ndarray) -> float:
        """Calculate portfolio volatility"""
        return self.portfolio_stats(weights)[1]
    
    def optimize_sharpe(self) -> Dict:
        """
        Find portfolio with maximum Sharpe ratio
        
        Returns:
            Dictionary with optimized weights and portfolio stats
        """
        # Constraints: weights sum to 1
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        
        # Bounds: each weight between min and max
        bounds = tuple((Config.MIN_WEIGHT_PER_ASSET, Config.MAX_WEIGHT_PER_ASSET) 
                      for _ in range(self.num_assets))
        
        # Initial guess: equal weights
        init_weights = np.array([1/self.num_assets] * self.num_assets)
        
        # Optimize
        result = minimize(
            self.negative_sharpe,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_stats(optimal_weights)
        
        return {
            'weights': optimal_weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'tickers': self.returns.columns.tolist()
        }
    
    def optimize_min_volatility(self, target_return: Optional[float] = None) -> Dict:
        """
        Find minimum variance portfolio (optionally with target return)
        
        Args:
            target_return: If specified, finds min variance portfolio with this return
            
        Returns:
            Dictionary with optimized weights and portfolio stats
        """
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        
        # Add return constraint if target specified
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: self.portfolio_stats(x)[0] - target_return
            })
        
        bounds = tuple((Config.MIN_WEIGHT_PER_ASSET, Config.MAX_WEIGHT_PER_ASSET) 
                      for _ in range(self.num_assets))
        
        init_weights = np.array([1/self.num_assets] * self.num_assets)
        
        result = minimize(
            self.portfolio_volatility,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if not result.success:
            raise ValueError(f"Optimization failed: {result.message}")
        
        optimal_weights = result.x
        ret, vol, sharpe = self.portfolio_stats(optimal_weights)
        
        return {
            'weights': optimal_weights,
            'return': ret,
            'volatility': vol,
            'sharpe_ratio': sharpe,
            'tickers': self.returns.columns.tolist()
        }
    
    def efficient_frontier(self, num_portfolios: int = 100) -> pd.DataFrame:
        """
        Generate efficient frontier
        
        Args:
            num_portfolios: Number of portfolios to generate
            
        Returns:
            DataFrame with portfolio statistics
        """
        # Get min and max returns
        min_vol_portfolio = self.optimize_min_volatility()
        max_sharpe_portfolio = self.optimize_sharpe()
        
        min_return = min_vol_portfolio['return']
        max_return = self.mean_returns.max()
        
        # Generate target returns
        target_returns = np.linspace(min_return, max_return, num_portfolios)
        
        frontier_portfolios = []
        
        for target in target_returns:
            try:
                result = self.optimize_min_volatility(target_return=target)
                frontier_portfolios.append({
                    'Return': result['return'],
                    'Volatility': result['volatility'],
                    'Sharpe': result['sharpe_ratio']
                })
            except:
                # Skip if optimization fails for this target
                continue
        
        return pd.DataFrame(frontier_portfolios)
    
    def monte_carlo_portfolios(self, num_portfolios: int = 5000) -> pd.DataFrame:
        """
        Generate random portfolios for visualization
        
        Returns:
            DataFrame with random portfolio statistics
        """
        results = []
        
        for _ in range(num_portfolios):
            # Random weights
            weights = np.random.random(self.num_assets)
            weights /= np.sum(weights)
            
            # Calculate stats
            ret, vol, sharpe = self.portfolio_stats(weights)
            
            results.append({
                'Return': ret,
                'Volatility': vol,
                'Sharpe': sharpe
            })
        
        return pd.DataFrame(results)


def calculate_risk_metrics(returns: pd.Series, confidence_level: float = 0.95) -> Dict:
    """
    Calculate comprehensive risk metrics for a return series
    
    Args:
        returns: Series of portfolio returns
        confidence_level: Confidence level for VaR and CVaR
        
    Returns:
        Dictionary of risk metrics
    """
    # Value at Risk (VaR)
    var = returns.quantile(1 - confidence_level)
    
    # Conditional Value at Risk (CVaR)
    cvar = returns[returns <= var].mean()
    
    # Maximum Drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    # Volatility (annualized)
    volatility = returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
    
    # Downside deviation
    negative_returns = returns[returns < 0]
    downside_std = negative_returns.std() * np.sqrt(Config.TRADING_DAYS_PER_YEAR)
    
    return {
        'var': var,
        'cvar': cvar,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'downside_deviation': downside_std,
        'skewness': returns.skew(),
        'kurtosis': returns.kurtosis()
    }

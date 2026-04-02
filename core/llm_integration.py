"""
LLM Integration for Scenario Generation
Uses Hugging Face API to generate market scenarios
"""
import requests
import json
from typing import List, Dict, Optional
from core.config import Config


class ScenarioGenerator:
    """
    Generate market scenarios using LLM
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize scenario generator
        
        Args:
            api_key: Hugging Face API key (defaults to config)
        """
        self.api_key = api_key or Config.HUGGINGFACE_API_KEY
        self.model = Config.HUGGINGFACE_MODEL
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        
    def _call_api(self, prompt: str) -> str:
        """
        Call Hugging Face Inference API
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
        """
        if not self.api_key:
            return self._fallback_scenario()
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": Config.MAX_TOKENS,
                "temperature": Config.TEMPERATURE,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get('generated_text', self._fallback_scenario())
                return str(result)
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return self._fallback_scenario()
                
        except Exception as e:
            print(f"Exception calling API: {str(e)}")
            return self._fallback_scenario()
    
    def _fallback_scenario(self) -> str:
        """Return a default scenario when API is unavailable"""
        return """Market Stress Scenario Analysis:

**Recession Scenario:**
- Stocks: -25% to -35%
- Bonds: +5% to +10%
- Commodities: -15% to -20%
- Volatility: Increases significantly

**Interest Rate Hike:**
- Stocks: -10% to -15%
- Bonds: -8% to -12%
- Real Estate: -5% to -10%

**Geopolitical Crisis:**
- Equities: -15% to -25%
- Safe havens (Gold): +10% to +20%
- Energy: +20% to +40%
"""
    
    def generate_market_scenario(self, 
                                 portfolio_tickers: List[str],
                                 scenario_type: str = "recession") -> str:
        """
        Generate a detailed market scenario
        
        Args:
            portfolio_tickers: List of ticker symbols in portfolio
            scenario_type: Type of scenario (recession, inflation, rate_hike, etc.)
            
        Returns:
            Generated scenario description
        """
        prompt = self._build_scenario_prompt(portfolio_tickers, scenario_type)
        return self._call_api(prompt)
    
    def _build_scenario_prompt(self, tickers: List[str], scenario_type: str) -> str:
        """Build prompt for scenario generation"""
        
        ticker_str = ", ".join(tickers)
        
        prompts = {
            "recession": f"""<s>[INST] You are a financial analyst. Analyze the impact of an economic recession on a portfolio containing: {ticker_str}.

Provide:
1. Expected price changes for each asset class
2. Correlation changes during the crisis
3. Risk assessment
4. Recommended adjustments

Keep response under 300 words. [/INST]""",
            
            "inflation": f"""<s>[INST] You are a financial analyst. Analyze the impact of high inflation (6-8% annually) on a portfolio with: {ticker_str}.

Provide:
1. How each asset performs in high inflation
2. Real vs nominal returns
3. Portfolio rebalancing suggestions

Keep response under 300 words. [/INST]""",
            
            "rate_hike": f"""<s>[INST] You are a financial analyst. Analyze the impact of Federal Reserve raising interest rates by 2% on a portfolio containing: {ticker_str}.

Provide:
1. Impact on each asset class
2. Duration risk for bonds
3. Sector rotation recommendations

Keep response under 300 words. [/INST]""",
            
            "bull_market": f"""<s>[INST] You are a financial analyst. Analyze the portfolio performance during a strong bull market for: {ticker_str}.

Provide:
1. Growth expectations
2. Momentum opportunities
3. Profit-taking strategies

Keep response under 300 words. [/INST]""",
            
            "volatility_spike": f"""<s>[INST] You are a financial analyst. Analyze the impact of a sudden volatility spike (VIX > 40) on: {ticker_str}.

Provide:
1. Short-term price impacts
2. Hedging strategies
3. Risk management adjustments

Keep response under 300 words. [/INST]"""
        }
        
        return prompts.get(scenario_type, prompts["recession"])
    
    def generate_stress_test_scenarios(self, tickers: List[str]) -> Dict[str, str]:
        """
        Generate multiple stress test scenarios
        
        Returns:
            Dictionary mapping scenario names to descriptions
        """
        scenarios = {}
        
        scenario_types = ["recession", "inflation", "rate_hike", "volatility_spike"]
        
        for scenario_type in scenario_types:
            scenarios[scenario_type] = self.generate_market_scenario(tickers, scenario_type)
        
        return scenarios
    
    def interpret_portfolio_risk(self, 
                                 portfolio_stats: Dict,
                                 tickers: List[str]) -> str:
        """
        Get LLM interpretation of portfolio risk metrics
        
        Args:
            portfolio_stats: Dictionary with return, volatility, sharpe, etc.
            tickers: List of tickers in portfolio
            
        Returns:
            Natural language interpretation
        """
        ticker_str = ", ".join(tickers)
        
        prompt = f"""<s>[INST] You are a financial advisor. Interpret these portfolio metrics for a client:

Portfolio: {ticker_str}
- Annual Return: {portfolio_stats.get('return', 0):.2%}
- Volatility: {portfolio_stats.get('volatility', 0):.2%}
- Sharpe Ratio: {portfolio_stats.get('sharpe_ratio', 0):.2f}
- Max Drawdown: {portfolio_stats.get('max_drawdown', 0):.2%}
- VaR (95%): {portfolio_stats.get('var', 0):.2%}

Provide:
1. Risk level assessment
2. Suitability for different investor profiles
3. Specific improvement recommendations

Keep response professional and under 250 words. [/INST]"""
        
        return self._call_api(prompt)


# Predefined scenario templates (fallback when LLM unavailable)
SCENARIO_TEMPLATES = {
    "recession": {
        "name": "Economic Recession",
        "adjustments": {
            "Stocks": -0.25,
            "Bonds": 0.08,
            "Commodities": -0.15,
            "Cash": 0.0
        },
        "description": "Defensive positioning with increased bond allocation"
    },
    "inflation": {
        "name": "High Inflation (>5%)",
        "adjustments": {
            "Stocks": -0.10,
            "Bonds": -0.15,
            "Commodities": 0.20,
            "Real Estate": 0.08
        },
        "description": "Shift toward inflation-protected assets"
    },
    "rate_hike": {
        "name": "Interest Rate Increase",
        "adjustments": {
            "Stocks": -0.12,
            "Bonds": -0.10,
            "Cash": 0.02
        },
        "description": "Reduce duration risk, increase cash position"
    }
}

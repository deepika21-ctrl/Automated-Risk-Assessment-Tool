"""
Configuration file for Portfolio Risk Assessment Tool
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # API Keys
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Data Settings
    DEFAULT_PERIOD_YEARS = 2
    TRADING_DAYS_PER_YEAR = 252
    
    # Risk Metrics
    VAR_CONFIDENCE_LEVEL = 0.95
    CVAR_CONFIDENCE_LEVEL = 0.95
    DEFAULT_RISK_FREE_RATE = 0.04  # 4%
    
    # Monte Carlo Simulation
    NUM_SIMULATIONS = 10000
    SIMULATION_DAYS = 252  # 1 year
    
    # Optimization
    MAX_WEIGHT_PER_ASSET = 0.40  # 40% max allocation
    MIN_WEIGHT_PER_ASSET = 0.00  # 0% min allocation
    
    # LLM Settings
    HUGGINGFACE_MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    MAX_TOKENS = 512
    TEMPERATURE = 0.7
    
    # Application
    APP_TITLE = "Automated Risk Assessment Tool"
    APP_LAYOUT = "wide"
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.HUGGINGFACE_API_KEY:
            print("⚠️  Warning: HUGGINGFACE_API_KEY not set. LLM features will be limited.")
        return True

# Validate on import
Config.validate()

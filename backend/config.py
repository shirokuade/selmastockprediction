"""
Configuration settings for the stock prediction backend
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    environment: str = "development"

    # CORS Settings
    allowed_origins: str = "http://localhost:3000"

    # Data Configuration
    data_dir: str = "./data"
    qlib_data_dir: str = "./qlib_data"
    model_dir: str = "./models"

    # Stock Market Settings
    default_market: str = "IDX"
    stock_suffix: str = ".JK"  # Indonesian stocks on Yahoo Finance

    # Database
    database_url: str = "sqlite+aiosqlite:///./stock_predictor.db"

    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    # Model Configuration
    model_type: str = "lightgbm"
    training_period: int = 1825  # 5 years for daily data
    prediction_horizon: int = 5  # days ahead

    # Data interval settings
    training_interval: str = "1d"  # "1d" for daily (5 years available)
                                   # "1h" for hourly (max 730 days/2 years due to Yahoo limit)
    prediction_interval: str = "1d"  # Interval for making predictions

    # Indonesian Stock Market
    idx_stocks: List[str] = [
        "BBCA", "BMRI", "BBRI", "TLKM", "ASII", "UNVR", "HMSP",
        "ICBP", "KLBF", "INDF", "SMGR", "GGRM", "PGAS", "ITMG",
        "ADRO", "PTBA", "INCO", "ANTM", "TINS", "MEDC"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def effective_training_period(self) -> int:
        """
        Get effective training period based on interval
        Yahoo Finance limits: hourly data max 730 days, daily unlimited
        """
        if self.training_interval in ["1h", "60m"]:
            # Hourly data limited to 2 years max
            return min(self.training_period, 730)
        elif self.training_interval in ["1m", "2m", "5m", "15m", "30m"]:
            # Minute data severely limited
            return min(self.training_period, 7)
        else:
            # Daily or longer - use full period
            return self.training_period

    def get_stock_symbol(self, symbol: str) -> str:
        """Convert Indonesian stock symbol to Yahoo Finance format"""
        symbol = symbol.upper().strip()
        if not symbol.endswith(self.stock_suffix):
            return f"{symbol}{self.stock_suffix}"
        return symbol

    def validate_stock_symbol(self, symbol: str) -> bool:
        """Validate if stock symbol is in Indonesian stock list"""
        clean_symbol = symbol.upper().strip().replace(self.stock_suffix, "")
        return clean_symbol in self.idx_stocks


# Global settings instance
settings = Settings()

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
    training_period: int = 1825  # 5 years
    prediction_horizon: int = 5  # days ahead

    # Indonesian Stock Market
    idx_stocks: List[str] = [
        "BBCA", "BMDR", "BBRI", "TLKM", "ASII", "UNVR", "HMSP",
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

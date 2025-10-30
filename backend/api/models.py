"""
Pydantic models for API request/response
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime


class StockSymbolRequest(BaseModel):
    """Request model for stock symbol"""
    symbol: str = Field(..., description="Stock symbol (e.g., BBCA, BMRI)")

    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        if not v or not v.strip():
            raise ValueError("Stock symbol cannot be empty")
        return v.upper().strip()


class PredictionRequest(BaseModel):
    """Request model for prediction"""
    symbol: str = Field(..., description="Stock symbol (e.g., BBCA, BMRI)")
    days: int = Field(5, description="Number of days to predict", ge=1, le=30)

    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        if not v or not v.strip():
            raise ValueError("Stock symbol cannot be empty")
        return v.upper().strip()


class StockData(BaseModel):
    """Stock data model"""
    symbol: str
    name: Optional[str] = None
    current_price: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    volume: Optional[int] = None
    market_cap: Optional[float] = None
    last_updated: Optional[datetime] = None


class PredictionData(BaseModel):
    """Individual prediction data point"""
    date: str
    price: float
    confidence: float


class PredictionResult(BaseModel):
    """Prediction result model"""
    symbol: str
    current_price: float
    predictions: List[PredictionData]
    trend: str  # "up", "down", "stable"
    confidence: float
    signal: str = "HOLD"  # "STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"
    generated_at: datetime


class UserSettings(BaseModel):
    """User settings model"""
    default_stock: str = Field(..., description="Default stock symbol")
    prediction_days: int = Field(5, description="Default prediction days", ge=1, le=30)
    notification_enabled: bool = Field(False, description="Enable notifications")

    @validator('default_stock')
    def validate_stock(cls, v):
        """Validate stock symbol"""
        if not v or not v.strip():
            raise ValueError("Default stock cannot be empty")
        return v.upper().strip()


class UserSettingsResponse(BaseModel):
    """User settings response"""
    settings: UserSettings
    saved_at: datetime


class AvailableStocksResponse(BaseModel):
    """Available stocks response"""
    stocks: List[Dict[str, str]]  # [{"symbol": "BBCA", "name": "Bank Central Asia"}]
    total: int


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    message: str
    timestamp: datetime


class SuccessResponse(BaseModel):
    """Success response model"""
    success: bool
    message: str


# Portfolio models
class PortfolioStock(BaseModel):
    """Portfolio stock holding"""
    symbol: str
    shares: int = Field(..., gt=0, description="Number of shares")
    purchase_price: float = Field(..., gt=0, description="Purchase price per share")
    purchase_date: Optional[str] = None

    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol"""
        if not v or not v.strip():
            raise ValueError("Stock symbol cannot be empty")
        return v.upper().strip()


class PortfolioResponse(BaseModel):
    """Portfolio response with current values"""
    stocks: List[Dict]  # Contains stock details with current prices
    total_investment: float
    current_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    last_updated: datetime


class AddPortfolioStockRequest(BaseModel):
    """Request to add stock to portfolio"""
    symbol: str
    shares: int = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)
    purchase_date: Optional[str] = None


# Activity Log models
class ActivityLog(BaseModel):
    """Activity log entry"""
    id: Optional[int] = None
    timestamp: datetime
    activity_type: str  # "prediction", "training", "daily_update", "weekly_retrain", "error"
    symbol: Optional[str] = None
    message: str
    details: Optional[Dict] = None


class ActivityLogResponse(BaseModel):
    """Activity logs response"""
    logs: List[ActivityLog]
    total: int

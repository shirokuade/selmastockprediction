"""
Database models for prediction engine
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class StockPrice(Base):
    """Daily stock price tracking for top 100 stocks"""
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    name = Column(String, nullable=True)
    date = Column(DateTime, index=True, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)
    market_cap = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class WeeklyPrediction(Base):
    """Weekly predictions for stocks (Monday to Friday)"""
    __tablename__ = "weekly_predictions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    week_start = Column(DateTime, index=True, nullable=False)  # Monday date

    # Monday purchase price
    monday_price = Column(Float, nullable=False)

    # Algorithm predictions
    algorithm_1 = Column(String, nullable=False)  # e.g., "LightGBM"
    prediction_1 = Column(Float, nullable=False)  # Predicted Friday price

    algorithm_2 = Column(String, nullable=False)  # e.g., "XGBoost"
    prediction_2 = Column(Float, nullable=False)  # Predicted Friday price

    # Average prediction
    avg_prediction = Column(Float, nullable=False)
    predicted_gain_percent = Column(Float, nullable=False)

    # Actual results (updated on Friday)
    actual_friday_price = Column(Float, nullable=True)
    actual_gain_percent = Column(Float, nullable=True)

    # Accuracy tracking
    is_correct = Column(Boolean, nullable=True)  # True if actual gain >= 2.5%
    prediction_error = Column(Float, nullable=True)  # Difference between predicted and actual

    # Status
    is_active = Column(Boolean, default=True)  # False after Friday close

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Top100Stock(Base):
    """List of top 100 most popular Indonesian stocks"""
    __tablename__ = "top_100_stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    rank = Column(Integer, nullable=False)  # 1-100
    sector = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prediction_engine.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

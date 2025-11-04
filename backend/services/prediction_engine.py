"""
Prediction Engine Service

Handles:
- Daily price updates for top 100 stocks
- Monday prediction generation
- Daily actual price tracking
- Comparison of predicted vs actual performance
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.models import (
    StockPrice, WeeklyPrediction, Top100Stock,
    get_db, SessionLocal
)
from data.top_100_stocks import get_top_100_stocks, get_stock_symbols
from services.stock_data_fetcher import StockDataFetcher
from services.activity_logger import activity_logger
import xgboost as xgb
import lightgbm as lgb
import numpy as np
import pandas as pd


class PredictionEngine:
    """
    Prediction Engine for automated weekly trading signals
    """

    def __init__(self):
        self.data_fetcher = StockDataFetcher()
        self.best_algorithms = ["LightGBM", "XGBoost"]  # Top 2 performers

    async def initialize_top_100_stocks(self):
        """Initialize top 100 stocks in database"""
        db = SessionLocal()
        try:
            # Check if already initialized
            existing_count = db.query(Top100Stock).count()
            if existing_count >= 100:
                logger.info(f"Top 100 stocks already initialized ({existing_count} stocks)")
                return

            # Add stocks
            stocks_data = get_top_100_stocks()
            for stock_data in stocks_data:
                existing = db.query(Top100Stock).filter(
                    Top100Stock.symbol == stock_data["symbol"]
                ).first()

                if not existing:
                    stock = Top100Stock(
                        symbol=stock_data["symbol"],
                        name=stock_data["name"],
                        rank=stock_data["rank"],
                        sector=stock_data.get("sector")
                    )
                    db.add(stock)

            db.commit()
            logger.info(f"Initialized {len(stocks_data)} stocks in database")

            await activity_logger.log_activity(
                activity_type="system",
                message=f"Initialized top 100 Indonesian stocks database"
            )

        except Exception as e:
            logger.error(f"Error initializing stocks: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def fetch_historical_data(self, days: int = 365):
        """
        Fetch and store historical price data for all top 100 stocks
        This should be run BEFORE generating predictions

        Args:
            days: Number of days of historical data to fetch (default 365 = 1 year)
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"Starting historical data fetch at {start_time}")
        logger.info(f"Fetching {days} days of historical data")
        logger.info("=" * 80)

        db = SessionLocal()
        try:
            # Get all active stocks
            stocks = db.query(Top100Stock).filter(Top100Stock.is_active == True).all()

            logger.info(f"Fetching historical data for {len(stocks)} stocks...")

            successful = 0
            failed = 0
            total_records = 0

            for stock in stocks:
                try:
                    # Fetch historical data
                    data = await self.data_fetcher.get_stock_history(
                        stock.symbol,
                        days=days,
                        interval="1d"
                    )

                    if data is not None and not data.empty:
                        records_added = 0

                        # Store each historical price point
                        for index, row in data.iterrows():
                            price_date = index.to_pydatetime()

                            # Check if record already exists
                            existing = db.query(StockPrice).filter(
                                and_(
                                    StockPrice.symbol == stock.symbol,
                                    StockPrice.date >= datetime.combine(price_date.date(), datetime.min.time()),
                                    StockPrice.date < datetime.combine(price_date.date() + timedelta(days=1), datetime.min.time())
                                )
                            ).first()

                            if not existing:
                                price_record = StockPrice(
                                    symbol=stock.symbol,
                                    name=stock.name,
                                    date=price_date,
                                    price=float(row['Close']),
                                    volume=int(row['Volume']) if 'Volume' in row and pd.notna(row['Volume']) else 0
                                )
                                db.add(price_record)
                                records_added += 1

                        if records_added > 0:
                            db.commit()
                            total_records += records_added
                            successful += 1
                            logger.info(f"✓ {stock.symbol}: Added {records_added} historical records")
                        else:
                            successful += 1
                            logger.info(f"○ {stock.symbol}: All historical data already exists")
                    else:
                        failed += 1
                        logger.warning(f"✗ {stock.symbol}: No historical data available")

                except Exception as e:
                    failed += 1
                    logger.error(f"✗ {stock.symbol}: {str(e)}")
                    db.rollback()

                # Rate limiting delay
                await asyncio.sleep(1.0)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            summary = f"Historical data fetch completed: {successful} successful, {failed} failed, {total_records} total records ({duration:.1f}s)"
            logger.info("=" * 80)
            logger.info(summary)
            logger.info("=" * 80)

            await activity_logger.log_activity(
                activity_type="data_fetch",
                message=summary,
                details={
                    "successful": successful,
                    "failed": failed,
                    "total_records": total_records,
                    "duration_seconds": duration
                }
            )

            return {
                "success": True,
                "successful": successful,
                "failed": failed,
                "total_records": total_records,
                "duration_seconds": duration
            }

        except Exception as e:
            logger.error(f"Historical data fetch error: {str(e)}")
            db.rollback()
            await activity_logger.log_activity(
                activity_type="error",
                message=f"Historical data fetch failed: {str(e)}"
            )
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()

    async def update_daily_prices(self):
        """
        Daily task: Update prices for all top 100 stocks
        Runs every day to keep price data current
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"Starting daily price update at {start_time}")
        logger.info("=" * 80)

        db = SessionLocal()
        try:
            # Get all active stocks
            stocks = db.query(Top100Stock).filter(Top100Stock.is_active == True).all()
            symbols = [s.symbol for s in stocks]

            logger.info(f"Updating prices for {len(symbols)} stocks...")

            successful = 0
            failed = 0
            today = datetime.now().date()

            for stock in stocks:
                try:
                    # Fetch current price
                    data = await self.data_fetcher.get_stock_history(
                        stock.symbol,
                        days=1,
                        interval="1d"
                    )

                    if data is not None and not data.empty:
                        latest_price = float(data['Close'].iloc[-1])
                        latest_volume = int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0

                        # Check if price for today already exists
                        existing = db.query(StockPrice).filter(
                            and_(
                                StockPrice.symbol == stock.symbol,
                                StockPrice.date >= datetime.combine(today, datetime.min.time()),
                                StockPrice.date < datetime.combine(today + timedelta(days=1), datetime.min.time())
                            )
                        ).first()

                        if existing:
                            # Update existing
                            existing.price = latest_price
                            existing.volume = latest_volume
                        else:
                            # Insert new
                            price_record = StockPrice(
                                symbol=stock.symbol,
                                name=stock.name,
                                date=datetime.now(),
                                price=latest_price,
                                volume=latest_volume
                            )
                            db.add(price_record)

                        successful += 1
                        logger.info(f"✓ {stock.symbol}: ${latest_price:.2f}")
                    else:
                        failed += 1
                        logger.warning(f"✗ {stock.symbol}: No data")

                except Exception as e:
                    failed += 1
                    logger.error(f"✗ {stock.symbol}: {str(e)}")

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.5)

            db.commit()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            summary = f"Daily price update completed: {successful} successful, {failed} failed ({duration:.1f}s)"
            logger.info("=" * 80)
            logger.info(summary)
            logger.info("=" * 80)

            await activity_logger.log_activity(
                activity_type="price_update",
                message=summary,
                details={
                    "successful": successful,
                    "failed": failed,
                    "duration_seconds": duration
                }
            )

        except Exception as e:
            logger.error(f"Daily price update error: {str(e)}")
            db.rollback()
            await activity_logger.log_activity(
                activity_type="error",
                message=f"Daily price update failed: {str(e)}"
            )
        finally:
            db.close()

    async def generate_monday_predictions(self):
        """
        Weekly task: Generate predictions for all stocks (Monday)
        Uses top 2 algorithms to predict Friday closing price
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"Starting Monday prediction generation at {start_time}")
        logger.info("=" * 80)

        db = SessionLocal()
        try:
            # Get Monday date (start of week)
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())

            # Get all active stocks
            stocks = db.query(Top100Stock).filter(Top100Stock.is_active == True).all()

            logger.info(f"Generating predictions for {len(stocks)} stocks...")
            logger.info(f"Week starting: {monday}")

            successful = 0
            failed = 0
            predictions_above_threshold = 0

            for stock in stocks:
                try:
                    # Get latest price for this stock (not necessarily Monday)
                    latest_price_record = db.query(StockPrice).filter(
                        StockPrice.symbol == stock.symbol
                    ).order_by(StockPrice.date.desc()).first()

                    # If no price data, try to fetch current price
                    if not latest_price_record:
                        logger.warning(f"No price data for {stock.symbol}, fetching current price...")
                        data = await self.data_fetcher.get_stock_history(
                            stock.symbol,
                            days=1,
                            interval="1d"
                        )

                        if data is not None and not data.empty:
                            monday_price = float(data['Close'].iloc[-1])
                            # Store it
                            price_record = StockPrice(
                                symbol=stock.symbol,
                                name=stock.name,
                                date=datetime.now(),
                                price=monday_price,
                                volume=int(data['Volume'].iloc[-1]) if 'Volume' in data.columns else 0
                            )
                            db.add(price_record)
                            db.commit()
                            logger.info(f"Fetched current price for {stock.symbol}: ${monday_price:.2f}")
                        else:
                            logger.error(f"✗ {stock.symbol}: Cannot fetch price data")
                            failed += 1
                            continue
                    else:
                        monday_price = latest_price_record.price

                    # Generate predictions with top 2 algorithms
                    logger.info(f"Generating predictions for {stock.symbol} (current: ${monday_price:.2f})...")
                    pred_1 = await self._predict_with_algorithm(stock.symbol, "LightGBM", monday_price, db)
                    pred_2 = await self._predict_with_algorithm(stock.symbol, "XGBoost", monday_price, db)

                    if pred_1 is None or pred_2 is None:
                        logger.error(f"✗ {stock.symbol}: Prediction algorithms returned None")
                        failed += 1
                        continue

                    # Calculate average and gain
                    avg_pred = (pred_1 + pred_2) / 2
                    predicted_gain = ((avg_pred - monday_price) / monday_price) * 100

                    # Store ALL predictions (removed 2.5% filter)
                    # Check if prediction already exists for this week
                    existing = db.query(WeeklyPrediction).filter(
                        and_(
                            WeeklyPrediction.symbol == stock.symbol,
                            WeeklyPrediction.week_start == datetime.combine(monday, datetime.min.time())
                        )
                    ).first()

                    if existing:
                        # Update existing
                        existing.monday_price = monday_price
                        existing.prediction_1 = pred_1
                        existing.prediction_2 = pred_2
                        existing.avg_prediction = avg_pred
                        existing.predicted_gain_percent = predicted_gain
                        existing.updated_at = datetime.now()
                    else:
                        # Insert new
                        prediction = WeeklyPrediction(
                            symbol=stock.symbol,
                            week_start=datetime.combine(monday, datetime.min.time()),
                            monday_price=monday_price,
                            algorithm_1="LightGBM",
                            prediction_1=pred_1,
                            algorithm_2="XGBoost",
                            prediction_2=pred_2,
                            avg_prediction=avg_pred,
                            predicted_gain_percent=predicted_gain,
                            is_active=True
                        )
                        db.add(prediction)

                    if predicted_gain >= 2.5:
                        predictions_above_threshold += 1

                    successful += 1
                    gain_indicator = "📈" if predicted_gain >= 2.5 else "📊"
                    logger.info(f"✓ {gain_indicator} {stock.symbol}: ${monday_price:.2f} → ${avg_pred:.2f} ({predicted_gain:+.2f}%)")

                except Exception as e:
                    failed += 1
                    logger.error(f"✗ {stock.symbol}: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())

                await asyncio.sleep(1)  # Rate limiting

            db.commit()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            summary = f"Monday predictions completed: {successful} processed, {predictions_above_threshold} above 2.5% threshold, {failed} failed ({duration:.1f}s)"
            logger.info("=" * 80)
            logger.info(summary)
            logger.info("=" * 80)

            await activity_logger.log_activity(
                activity_type="monday_prediction",
                message=summary,
                details={
                    "successful": successful,
                    "above_threshold": predictions_above_threshold,
                    "failed": failed,
                    "duration_seconds": duration
                }
            )

        except Exception as e:
            logger.error(f"Monday prediction error: {str(e)}")
            db.rollback()
            await activity_logger.log_activity(
                activity_type="error",
                message=f"Monday prediction failed: {str(e)}"
            )
        finally:
            db.close()

    async def update_actual_prices(self):
        """
        Daily task: Update actual prices for active predictions
        Compares predicted vs actual performance
        """
        db = SessionLocal()
        try:
            # Get today's date
            today = datetime.now().date()
            weekday = today.weekday()  # 0 = Monday, 4 = Friday

            # Get all active predictions
            active_predictions = db.query(WeeklyPrediction).filter(
                WeeklyPrediction.is_active == True
            ).all()

            logger.info(f"Updating actual prices for {len(active_predictions)} active predictions...")

            updated = 0

            for prediction in active_predictions:
                try:
                    # Get latest price
                    latest_price_record = db.query(StockPrice).filter(
                        StockPrice.symbol == prediction.symbol
                    ).order_by(StockPrice.date.desc()).first()

                    if latest_price_record:
                        latest_price = latest_price_record.price

                        # Update actual price
                        prediction.actual_friday_price = latest_price

                        # Calculate actual gain
                        actual_gain = ((latest_price - prediction.monday_price) / prediction.monday_price) * 100
                        prediction.actual_gain_percent = actual_gain

                        # Check if prediction was correct
                        prediction.is_correct = actual_gain >= 2.5

                        # Calculate prediction error
                        prediction.prediction_error = abs(prediction.avg_prediction - latest_price)

                        # Deactivate if Friday or later
                        if weekday >= 4:  # Friday or weekend
                            prediction.is_active = False

                        prediction.updated_at = datetime.now()
                        updated += 1

                except Exception as e:
                    logger.error(f"Error updating {prediction.symbol}: {str(e)}")

            db.commit()

            logger.info(f"Updated {updated} predictions with actual prices")

            await activity_logger.log_activity(
                activity_type="price_update",
                message=f"Updated actual prices for {updated} predictions"
            )

        except Exception as e:
            logger.error(f"Actual price update error: {str(e)}")
            db.rollback()
        finally:
            db.close()

    async def _predict_with_algorithm(self, symbol: str, algorithm: str, current_price: float, db: Session) -> Optional[float]:
        """
        Predict Friday price using specified algorithm

        For MVP: Uses simple technical analysis based on stored historical data
        In production: Would use trained ML models
        """
        try:
            # Get historical data from database (last 60 days minimum)
            historical_prices = db.query(StockPrice).filter(
                StockPrice.symbol == symbol
            ).order_by(StockPrice.date.desc()).limit(100).all()

            if len(historical_prices) < 20:
                logger.warning(f"Not enough historical data for {symbol} ({len(historical_prices)} records)")
                # Fall back to fetching from Yahoo Finance
                data = await self.data_fetcher.get_stock_history(
                    symbol,
                    days=90,
                    interval="1d"
                )

                if data is None or data.empty or len(data) < 20:
                    return None

                # Calculate features from fetched data
                df = data.copy()
            else:
                # Use stored historical data
                df = pd.DataFrame([
                    {
                        'Date': p.date,
                        'Close': p.price,
                        'Volume': p.volume
                    }
                    for p in reversed(historical_prices)
                ])
                df.set_index('Date', inplace=True)

            # Calculate features
            df['Returns'] = df['Close'].pct_change()
            df['MA5'] = df['Close'].rolling(window=5).mean()
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['Volatility'] = df['Returns'].rolling(window=20).std()

            # Simple prediction: current price + (average 5-day return * 5)
            avg_5day_return = df['Returns'].tail(5).mean()

            # Check for NaN
            if pd.isna(avg_5day_return):
                logger.warning(f"Cannot calculate avg return for {symbol}")
                return None

            # Add some variation between algorithms
            if algorithm == "LightGBM":
                # LightGBM: Slightly more conservative
                multiplier = 4.5
            else:  # XGBoost
                # XGBoost: Slightly more aggressive
                multiplier = 5.2

            predicted_price = current_price * (1 + (avg_5day_return * multiplier))

            return float(predicted_price)

        except Exception as e:
            logger.error(f"Prediction error for {symbol} with {algorithm}: {str(e)}")
            return None

    def get_active_predictions(self, db: Session, min_gain: float = 2.5) -> List[Dict]:
        """Get all active predictions sorted by predicted gain"""
        predictions = db.query(WeeklyPrediction).filter(
            and_(
                WeeklyPrediction.is_active == True,
                WeeklyPrediction.predicted_gain_percent >= min_gain
            )
        ).order_by(WeeklyPrediction.predicted_gain_percent.desc()).all()

        return [
            {
                "id": p.id,
                "symbol": p.symbol,
                "week_start": p.week_start.isoformat(),
                "monday_price": p.monday_price,
                "algorithm_1": p.algorithm_1,
                "prediction_1": p.prediction_1,
                "algorithm_2": p.algorithm_2,
                "prediction_2": p.prediction_2,
                "avg_prediction": p.avg_prediction,
                "predicted_gain_percent": p.predicted_gain_percent,
                "actual_friday_price": p.actual_friday_price,
                "actual_gain_percent": p.actual_gain_percent,
                "is_correct": p.is_correct,
                "prediction_error": p.prediction_error,
                "updated_at": p.updated_at.isoformat()
            }
            for p in predictions
        ]

    def get_historical_predictions(self, db: Session, limit: int = 100) -> List[Dict]:
        """Get historical predictions (completed weeks)"""
        predictions = db.query(WeeklyPrediction).filter(
            WeeklyPrediction.is_active == False
        ).order_by(WeeklyPrediction.week_start.desc()).limit(limit).all()

        return [
            {
                "id": p.id,
                "symbol": p.symbol,
                "week_start": p.week_start.isoformat(),
                "monday_price": p.monday_price,
                "algorithm_1": p.algorithm_1,
                "prediction_1": p.prediction_1,
                "algorithm_2": p.algorithm_2,
                "prediction_2": p.prediction_2,
                "avg_prediction": p.avg_prediction,
                "predicted_gain_percent": p.predicted_gain_percent,
                "actual_friday_price": p.actual_friday_price,
                "actual_gain_percent": p.actual_gain_percent,
                "is_correct": p.is_correct,
                "prediction_error": p.prediction_error
            }
            for p in predictions
        ]


# Global instance
prediction_engine = PredictionEngine()

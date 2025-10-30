"""
Stock prediction service using Qlib and machine learning models
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, Dict, List
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

from config import settings
from api.models import PredictionResult
from services.qlib_handler import QlibHandler
from services.stock_data_fetcher import StockDataFetcher


class StockPredictor:
    """Predict stock prices using machine learning"""

    def __init__(self):
        self.qlib_handler = QlibHandler()
        self.stock_fetcher = StockDataFetcher()
        self.scalers = {}  # Cache for feature scalers

    async def predict(self, symbol: str, days: int = 5) -> Optional[PredictionResult]:
        """
        Predict stock prices for specified number of days

        Args:
            symbol: Stock symbol
            days: Number of days to predict

        Returns:
            PredictionResult or None
        """
        try:
            logger.info(f"Starting prediction for {symbol}, days: {days}")

            # Get current stock price
            stock_info = await self.stock_fetcher.get_stock_info(symbol)
            if not stock_info:
                logger.error(f"Could not fetch current price for {symbol}")
                return None

            current_price = stock_info.current_price

            # Load or train model
            model = await self.qlib_handler.load_model(symbol)
            if model is None:
                logger.info(f"No trained model found for {symbol}, training new model...")
                success = await self.train_model(symbol)
                if not success:
                    logger.error(f"Failed to train model for {symbol}")
                    return None
                model = await self.qlib_handler.load_model(symbol)

            if model is None:
                logger.error("Model is still None after training")
                return None

            # Prepare recent data for prediction
            recent_data = await self.qlib_handler.prepare_data_for_analysis(symbol)
            if recent_data is None or recent_data.empty:
                logger.error(f"No data available for prediction")
                return None

            # Get features
            feature_cols = self.qlib_handler.get_feature_columns()

            # Drop NaN values
            recent_data = recent_data.dropna(subset=feature_cols)
            if recent_data.empty:
                logger.error("No valid data after removing NaN values")
                return None

            # Get the most recent features
            latest_features = recent_data[feature_cols].iloc[-1:].values

            # Load scaler if exists
            scaler = await self._load_scaler(symbol)
            if scaler:
                latest_features = scaler.transform(latest_features)

            # Generate predictions
            predictions = []
            current_pred_price = current_price

            for i in range(days):
                # Predict next day
                pred_return = model.predict(latest_features)[0]

                # Calculate predicted price
                pred_price = current_pred_price * (1 + pred_return)

                # Store prediction
                pred_date = datetime.now() + timedelta(days=i+1)
                predictions.append({
                    "date": pred_date.strftime("%Y-%m-%d"),
                    "price": round(float(pred_price), 2),
                    "confidence": self._calculate_confidence(pred_return, i)
                })

                # Update for next iteration
                current_pred_price = pred_price

                # Update features for next prediction (simplified)
                # In a more sophisticated model, you'd update all features
                latest_features = self._update_features(latest_features, pred_return)

            # Determine trend
            trend = self._determine_trend(current_price, predictions[-1]["price"])

            # Calculate overall confidence
            avg_confidence = np.mean([p["confidence"] for p in predictions])

            return PredictionResult(
                symbol=symbol,
                current_price=current_price,
                predictions=predictions,
                trend=trend,
                confidence=round(float(avg_confidence), 4),
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def train_model(self, symbol: str) -> bool:
        """
        Train prediction model for a stock

        Args:
            symbol: Stock symbol

        Returns:
            True if training successful
        """
        try:
            logger.info(f"Training model for {symbol}")

            # Prepare training data
            data = await self.qlib_handler.prepare_data_for_analysis(symbol)
            if data is None or data.empty:
                logger.error(f"No data available for training {symbol}")
                return False

            # Get feature columns
            feature_cols = self.qlib_handler.get_feature_columns()

            # Prepare target (next day return)
            data['target'] = data['return'].shift(-1)

            # Drop NaN values
            data = data.dropna(subset=feature_cols + ['target'])

            if len(data) < 100:
                logger.error(f"Insufficient data for training: {len(data)} records")
                return False

            # Split features and target
            X = data[feature_cols].values
            y = data['target'].values

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Save scaler
            await self._save_scaler(scaler, symbol)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, shuffle=False
            )

            # Train model (using Gradient Boosting)
            logger.info(f"Training Gradient Boosting model with {len(X_train)} samples")
            model = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                verbose=0
            )

            model.fit(X_train, y_train)

            # Evaluate
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)

            logger.info(f"Model trained - Train R²: {train_score:.4f}, Test R²: {test_score:.4f}")

            # Save model
            success = await self.qlib_handler.save_model(model, symbol)

            return success

        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _calculate_confidence(self, pred_return: float, day_index: int) -> float:
        """
        Calculate confidence score for prediction

        Args:
            pred_return: Predicted return
            day_index: Day index (0-based)

        Returns:
            Confidence score (0-1)
        """
        # Confidence decreases with prediction horizon
        base_confidence = 0.85
        decay_rate = 0.05
        confidence = base_confidence * (1 - decay_rate * day_index)

        # Adjust for extreme predictions
        if abs(pred_return) > 0.05:  # > 5% change
            confidence *= 0.8

        return max(0.3, min(0.95, confidence))

    def _determine_trend(self, current_price: float, future_price: float) -> str:
        """
        Determine price trend

        Args:
            current_price: Current price
            future_price: Predicted future price

        Returns:
            "up", "down", or "stable"
        """
        change_percent = (future_price - current_price) / current_price * 100

        if change_percent > 2:
            return "up"
        elif change_percent < -2:
            return "down"
        else:
            return "stable"

    def _update_features(self, features: np.ndarray, pred_return: float) -> np.ndarray:
        """
        Update features for next prediction (simplified version)

        Args:
            features: Current feature array
            pred_return: Predicted return

        Returns:
            Updated feature array
        """
        # This is a simplified version
        # In a real implementation, you'd update all technical indicators
        updated = features.copy()
        updated[0, 0] = pred_return  # Update return
        return updated

    async def _save_scaler(self, scaler: StandardScaler, symbol: str) -> bool:
        """
        Save feature scaler

        Args:
            scaler: Fitted scaler
            symbol: Stock symbol

        Returns:
            True if successful
        """
        try:
            scaler_path = os.path.join(settings.model_dir, f"{symbol}_scaler.pkl")
            joblib.dump(scaler, scaler_path)
            self.scalers[symbol] = scaler
            logger.info(f"Scaler saved for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error saving scaler: {str(e)}")
            return False

    async def _load_scaler(self, symbol: str) -> Optional[StandardScaler]:
        """
        Load feature scaler

        Args:
            symbol: Stock symbol

        Returns:
            Scaler or None
        """
        try:
            # Check cache
            if symbol in self.scalers:
                return self.scalers[symbol]

            scaler_path = os.path.join(settings.model_dir, f"{symbol}_scaler.pkl")
            if not os.path.exists(scaler_path):
                return None

            scaler = joblib.load(scaler_path)
            self.scalers[symbol] = scaler
            logger.info(f"Scaler loaded for {symbol}")
            return scaler

        except Exception as e:
            logger.error(f"Error loading scaler: {str(e)}")
            return None

    async def get_model_status(self, symbol: str) -> Dict:
        """
        Get model status information

        Args:
            symbol: Stock symbol

        Returns:
            Status information dictionary
        """
        try:
            model_info = self.qlib_handler.get_model_info(symbol)
            scaler_path = os.path.join(settings.model_dir, f"{symbol}_scaler.pkl")
            has_scaler = os.path.exists(scaler_path)

            return {
                "model_exists": model_info.get("exists", False),
                "scaler_exists": has_scaler,
                "model_info": model_info,
                "ready_for_prediction": model_info.get("exists", False) and has_scaler
            }

        except Exception as e:
            logger.error(f"Error getting model status: {str(e)}")
            return {
                "model_exists": False,
                "scaler_exists": False,
                "ready_for_prediction": False,
                "error": str(e)
            }

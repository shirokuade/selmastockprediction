"""
Ensemble predictor combining XGBoost, LightGBM, and Random Forest
Optimized for personal trading with weighted voting
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, Dict, List, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import xgboost as xgb
import lightgbm as lgb
import joblib
import os

from config import settings
from api.models import PredictionResult, PredictionData
from services.qlib_handler import QlibHandler
from services.stock_data_fetcher import StockDataFetcher


class EnsemblePredictor:
    """
    Ensemble predictor with 3 models for robust predictions
    - XGBoost: 40% weight (fast, accurate, interpretable)
    - LightGBM: 30% weight (even faster, great for daily updates)
    - Random Forest: 30% weight (robust, less overfitting)
    """

    def __init__(self):
        self.qlib_handler = QlibHandler()
        self.stock_fetcher = StockDataFetcher()
        self.scalers = {}

        # Model weights based on comparative analysis
        self.weights = {
            'xgboost': 0.40,
            'lightgbm': 0.30,
            'random_forest': 0.30
        }

    async def predict(self, symbol: str, days: int = 5) -> Optional[PredictionResult]:
        """
        Generate ensemble prediction for a stock

        Args:
            symbol: Stock symbol
            days: Number of days to predict

        Returns:
            PredictionResult with ensemble predictions and signals
        """
        try:
            logger.info(f"Starting ensemble prediction for {symbol}, days: {days}")

            # Get current stock price
            stock_info = await self.stock_fetcher.get_stock_info(symbol)
            if not stock_info:
                logger.error(f"Could not fetch current price for {symbol}")
                return None

            current_price = stock_info.current_price

            # Load all 3 models
            models = await self._load_models(symbol)
            if not models:
                logger.info(f"No trained models found for {symbol}, training new ensemble...")
                success = await self.train_ensemble(symbol)
                if not success:
                    logger.error(f"Failed to train ensemble for {symbol}")
                    return None
                models = await self._load_models(symbol)

            if not models:
                logger.error("Models are still None after training")
                return None

            # Prepare recent data for prediction
            recent_data = await self.qlib_handler.prepare_data_for_analysis(symbol)
            if recent_data is None or recent_data.empty:
                logger.error(f"No data available for prediction")
                return None

            # Get features
            feature_cols = self.qlib_handler.get_feature_columns()
            recent_data = recent_data.dropna(subset=feature_cols)

            if recent_data.empty:
                logger.error("No valid data after removing NaN values")
                return None

            # Get the most recent features
            latest_features = recent_data[feature_cols].iloc[-1:].values

            # Load scaler
            scaler = await self._load_scaler(symbol)
            if scaler:
                latest_features = scaler.transform(latest_features)

            # Generate ensemble predictions
            predictions = []
            current_pred_price = current_price

            for i in range(days):
                # Get predictions from all models
                ensemble_pred = self._ensemble_predict(models, latest_features)

                # Calculate predicted price
                pred_price = current_pred_price * (1 + ensemble_pred)

                # Store prediction
                pred_date = datetime.now() + timedelta(days=i+1)
                predictions.append(PredictionData(
                    date=pred_date.strftime("%Y-%m-%d"),
                    price=round(float(pred_price), 2),
                    confidence=self._calculate_confidence(ensemble_pred, i)
                ))

                # Update for next iteration
                current_pred_price = pred_price
                latest_features = self._update_features(latest_features, ensemble_pred)

            # Determine trend
            trend = self._determine_trend(current_price, predictions[-1].price)

            # Calculate overall confidence
            avg_confidence = np.mean([p.confidence for p in predictions])

            # Calculate signal (BUY/HOLD/SELL)
            signal = self._calculate_signal(current_price, predictions, avg_confidence)

            result = PredictionResult(
                symbol=symbol,
                current_price=current_price,
                predictions=predictions,
                trend=trend,
                confidence=round(float(avg_confidence), 4),
                generated_at=datetime.now()
            )

            # Add signal to result (we'll extend the model later)
            result.signal = signal  # type: ignore

            return result

        except Exception as e:
            logger.error(f"Error in ensemble prediction: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    def _ensemble_predict(self, models: Dict, features: np.ndarray) -> float:
        """
        Make weighted ensemble prediction

        Args:
            models: Dictionary of trained models
            features: Feature array

        Returns:
            Weighted average prediction
        """
        predictions = {}

        # Get prediction from each model
        if 'xgboost' in models:
            predictions['xgboost'] = models['xgboost'].predict(features)[0]

        if 'lightgbm' in models:
            predictions['lightgbm'] = models['lightgbm'].predict(features)[0]

        if 'random_forest' in models:
            predictions['random_forest'] = models['random_forest'].predict(features)[0]

        # Weighted average
        ensemble_pred = sum(
            predictions[name] * self.weights[name]
            for name in predictions
        )

        logger.debug(f"Individual predictions: {predictions}")
        logger.debug(f"Ensemble prediction: {ensemble_pred}")

        return ensemble_pred

    def _calculate_signal(
        self,
        current_price: float,
        predictions: List[PredictionData],
        confidence: float
    ) -> str:
        """
        Calculate BUY/HOLD/SELL signal based on predictions

        Rules:
        - STRONG BUY: +3%+ predicted, confidence >80%
        - BUY: +1.5% to +3% predicted, confidence >75%
        - HOLD: -1.5% to +1.5% predicted
        - SELL: -3% to -1.5% predicted, confidence >75%
        - STRONG SELL: -3%+ predicted, confidence >80%
        """
        # Calculate average predicted change
        final_price = predictions[-1].price
        change_percent = ((final_price - current_price) / current_price) * 100

        logger.info(f"Signal calculation: change={change_percent:.2f}%, confidence={confidence:.2f}")

        if change_percent >= 3.0 and confidence >= 0.80:
            return "STRONG_BUY"
        elif change_percent >= 1.5 and confidence >= 0.75:
            return "BUY"
        elif change_percent <= -3.0 and confidence >= 0.80:
            return "STRONG_SELL"
        elif change_percent <= -1.5 and confidence >= 0.75:
            return "SELL"
        else:
            return "HOLD"

    async def train_ensemble(self, symbol: str) -> bool:
        """
        Train all 3 models in the ensemble

        Args:
            symbol: Stock symbol

        Returns:
            True if all models trained successfully
        """
        try:
            logger.info(f"Training ensemble for {symbol}")

            # Prepare training data
            data = await self.qlib_handler.prepare_data_for_analysis(symbol)
            if data is None or data.empty:
                logger.error(f"No data available for training {symbol}")
                return False

            # Get features
            feature_cols = self.qlib_handler.get_feature_columns()
            data['target'] = data['return'].shift(-1)
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
            await self._save_scaler(scaler, symbol)

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, shuffle=False
            )

            logger.info(f"Training with {len(X_train)} samples")

            # Train XGBoost (40% weight)
            logger.info("Training XGBoost...")
            xgb_model = xgb.XGBRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                verbosity=0
            )
            xgb_model.fit(X_train, y_train)
            xgb_score = xgb_model.score(X_test, y_test)
            logger.info(f"XGBoost Test R²: {xgb_score:.4f}")
            await self._save_model(xgb_model, symbol, 'xgboost')

            # Train LightGBM (30% weight)
            logger.info("Training LightGBM...")
            lgb_model = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42,
                verbose=-1
            )
            lgb_model.fit(X_train, y_train)
            lgb_score = lgb_model.score(X_test, y_test)
            logger.info(f"LightGBM Test R²: {lgb_score:.4f}")
            await self._save_model(lgb_model, symbol, 'lightgbm')

            # Train Random Forest (30% weight)
            logger.info("Training Random Forest...")
            rf_model = RandomForestRegressor(
                n_estimators=100,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )
            rf_model.fit(X_train, y_train)
            rf_score = rf_model.score(X_test, y_test)
            logger.info(f"Random Forest Test R²: {rf_score:.4f}")
            await self._save_model(rf_model, symbol, 'random_forest')

            # Calculate ensemble score
            ensemble_pred = (
                xgb_model.predict(X_test) * self.weights['xgboost'] +
                lgb_model.predict(X_test) * self.weights['lightgbm'] +
                rf_model.predict(X_test) * self.weights['random_forest']
            )
            from sklearn.metrics import r2_score
            ensemble_score = r2_score(y_test, ensemble_pred)

            logger.info(f"Ensemble Test R²: {ensemble_score:.4f}")
            logger.info(f"✓ Ensemble trained successfully for {symbol}")

            return True

        except Exception as e:
            logger.error(f"Error training ensemble: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    async def _load_models(self, symbol: str) -> Optional[Dict]:
        """Load all models for a symbol"""
        models = {}

        try:
            # Try to load each model
            xgb_path = os.path.join(settings.model_dir, f"{symbol}_xgboost.pkl")
            if os.path.exists(xgb_path):
                models['xgboost'] = joblib.load(xgb_path)
                logger.info(f"Loaded XGBoost model for {symbol}")

            lgb_path = os.path.join(settings.model_dir, f"{symbol}_lightgbm.pkl")
            if os.path.exists(lgb_path):
                models['lightgbm'] = joblib.load(lgb_path)
                logger.info(f"Loaded LightGBM model for {symbol}")

            rf_path = os.path.join(settings.model_dir, f"{symbol}_random_forest.pkl")
            if os.path.exists(rf_path):
                models['random_forest'] = joblib.load(rf_path)
                logger.info(f"Loaded Random Forest model for {symbol}")

            return models if models else None

        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return None

    async def _save_model(self, model, symbol: str, model_name: str) -> bool:
        """Save a model"""
        try:
            model_path = os.path.join(settings.model_dir, f"{symbol}_{model_name}.pkl")
            joblib.dump(model, model_path)
            logger.info(f"Saved {model_name} model for {symbol}")
            return True
        except Exception as e:
            logger.error(f"Error saving {model_name} model: {str(e)}")
            return False

    async def _save_scaler(self, scaler: StandardScaler, symbol: str) -> bool:
        """Save feature scaler"""
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
        """Load feature scaler"""
        try:
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

    def _calculate_confidence(self, pred_return: float, day_index: int) -> float:
        """Calculate confidence score for prediction"""
        base_confidence = 0.85
        decay_rate = 0.05
        confidence = base_confidence * (1 - decay_rate * day_index)

        # Adjust for extreme predictions
        if abs(pred_return) > 0.05:
            confidence *= 0.8

        return max(0.3, min(0.95, confidence))

    def _determine_trend(self, current_price: float, future_price: float) -> str:
        """Determine price trend"""
        change_percent = (future_price - current_price) / current_price * 100

        if change_percent > 2:
            return "up"
        elif change_percent < -2:
            return "down"
        else:
            return "stable"

    def _update_features(self, features: np.ndarray, pred_return: float) -> np.ndarray:
        """Update features for next prediction (simplified)"""
        updated = features.copy()
        updated[0, 0] = pred_return
        return updated

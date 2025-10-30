"""
Prediction-related API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from datetime import datetime

from api.models import PredictionRequest, PredictionResult
from services.ensemble_predictor import EnsemblePredictor
from services.activity_logger import activity_logger
from config import settings

router = APIRouter()
predictor = EnsemblePredictor()


@router.post("/predict", response_model=PredictionResult)
async def predict_stock(request: PredictionRequest):
    """
    Predict stock prices for specified number of days
    """
    try:
        symbol = request.symbol
        days = request.days

        logger.info(f"Generating prediction for: {symbol}, days: {days}")

        # Validate stock symbol
        if not settings.validate_stock_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {symbol}. Must be a valid Indonesian stock."
            )

        # Generate predictions
        result = await predictor.predict(symbol, days)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate predictions"
            )

        # Log activity
        await activity_logger.log_activity(
            activity_type="prediction",
            message=f"Generated {days}-day prediction for {symbol} (Signal: {result.signal})",
            symbol=symbol,
            details={
                "days": days,
                "current_price": result.current_price,
                "signal": result.signal,
                "confidence": result.confidence
            }
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction: {str(e)}")

        # Log error
        await activity_logger.log_activity(
            activity_type="error",
            message=f"Prediction failed for {symbol}: {str(e)}",
            symbol=symbol
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/train")
async def train_model(symbol: str):
    """
    Train or retrain model for a specific stock
    """
    try:
        logger.info(f"Training model for: {symbol}")

        # Validate stock symbol
        if not settings.validate_stock_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {symbol}"
            )

        # Train model
        success = await predictor.train_model(symbol)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Model training failed"
            )

        # Log activity
        await activity_logger.log_activity(
            activity_type="training",
            message=f"Trained ensemble model for {symbol}",
            symbol=symbol,
            details={
                "models": ["XGBoost", "LightGBM", "Random Forest"],
                "weights": {"xgboost": 0.4, "lightgbm": 0.3, "random_forest": 0.3}
            }
        )

        return {
            "message": f"Model trained successfully for {symbol}",
            "symbol": symbol,
            "timestamp": datetime.now()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")

        # Log error
        await activity_logger.log_activity(
            activity_type="error",
            message=f"Training failed for {symbol}: {str(e)}",
            symbol=symbol
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}"
        )


@router.get("/model-status/{symbol}")
async def get_model_status(symbol: str):
    """
    Get model status for a specific stock
    """
    try:
        logger.info(f"Checking model status for: {symbol}")

        status_info = await predictor.get_model_status(symbol)

        return {
            "symbol": symbol,
            "status": status_info,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get model status: {str(e)}"
        )

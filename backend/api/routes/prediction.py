"""
Prediction-related API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from datetime import datetime

from api.models import PredictionRequest, PredictionResult
from services.predictor import StockPredictor
from config import settings

router = APIRouter()
predictor = StockPredictor()


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

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating prediction: {str(e)}")
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

        return {
            "message": f"Model trained successfully for {symbol}",
            "symbol": symbol,
            "timestamp": datetime.now()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
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

"""
Prediction Engine API routes
"""
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from sqlalchemy.orm import Session

from database.models import get_db
from services.prediction_engine import prediction_engine
from services.activity_logger import activity_logger


router = APIRouter(prefix="/api/prediction-engine", tags=["prediction_engine"])


@router.get("/predictions/active")
async def get_active_predictions(
    min_gain: float = 0.0,
    db: Session = Depends(get_db)
):
    """
    Get all active predictions for current week

    Returns predictions sorted by highest gain potential
    Shows all predictions by default (min_gain=0)
    """
    try:
        predictions = prediction_engine.get_active_predictions(db, min_gain=min_gain)

        return {
            "predictions": predictions,
            "total": len(predictions),
            "min_gain_threshold": min_gain
        }

    except Exception as e:
        logger.error(f"Error getting active predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictions/historical")
async def get_historical_predictions(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get historical predictions (completed weeks)

    Shows past predictions with actual results for comparison
    """
    try:
        predictions = prediction_engine.get_historical_predictions(db, limit=limit)

        # Calculate accuracy stats
        total = len(predictions)
        correct = len([p for p in predictions if p.get('is_correct') == True])
        accuracy = (correct / total * 100) if total > 0 else 0

        return {
            "predictions": predictions,
            "total": total,
            "correct_predictions": correct,
            "accuracy_percent": accuracy
        }

    except Exception as e:
        logger.error(f"Error getting historical predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_prediction_engine():
    """
    Initialize prediction engine

    - Loads top 100 stocks into database
    - Sets up initial state

    Only needs to be run once
    """
    try:
        logger.info("Initializing prediction engine...")

        await prediction_engine.initialize_top_100_stocks()

        await activity_logger.log_activity(
            activity_type="system",
            message="Prediction engine initialized successfully"
        )

        return {
            "success": True,
            "message": "Prediction engine initialized successfully"
        }

    except Exception as e:
        logger.error(f"Error initializing prediction engine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/fetch-history")
async def trigger_fetch_historical_data(days: int = 365):
    """
    Fetch historical price data for all top 100 stocks

    This should be run BEFORE generating predictions to ensure
    the database has enough historical data.

    Args:
        days: Number of days of historical data to fetch (default: 365)

    Returns:
        Status of the operation with details on records fetched
    """
    try:
        logger.info(f"Manual trigger: Fetch historical data ({days} days)")

        await activity_logger.log_activity(
            activity_type="system",
            message=f"Historical data fetch manually triggered ({days} days)"
        )

        # Run the fetch (this will take a while)
        import asyncio
        asyncio.create_task(prediction_engine.fetch_historical_data(days=days))

        return {
            "success": True,
            "message": f"Historical data fetch started for {days} days",
            "warning": "This process may take 10-15 minutes for 100 stocks",
            "note": "Check activity logs for progress. You can generate predictions after this completes."
        }

    except Exception as e:
        logger.error(f"Error triggering historical data fetch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/price-update")
async def trigger_price_update():
    """
    Manually trigger daily price update

    Updates prices for all top 100 stocks
    """
    try:
        logger.info("Manual trigger: Daily price update")

        await activity_logger.log_activity(
            activity_type="system",
            message="Daily price update manually triggered"
        )

        # Trigger in background
        import asyncio
        asyncio.create_task(prediction_engine.update_daily_prices())

        return {
            "success": True,
            "message": "Daily price update triggered",
            "note": "Check activity logs for progress"
        }

    except Exception as e:
        logger.error(f"Error triggering price update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/monday-predictions")
async def trigger_monday_predictions():
    """
    Manually trigger Monday prediction generation

    Generates 5-day predictions for all top 100 stocks
    """
    try:
        logger.info("Manual trigger: Monday predictions")

        await activity_logger.log_activity(
            activity_type="system",
            message="Monday prediction generation manually triggered"
        )

        # Trigger in background
        import asyncio
        asyncio.create_task(prediction_engine.generate_monday_predictions())

        return {
            "success": True,
            "message": "Monday prediction generation triggered",
            "warning": "This process may take 5-10 minutes for 100 stocks",
            "note": "Check activity logs for progress"
        }

    except Exception as e:
        logger.error(f"Error triggering Monday predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/actual-price-update")
async def trigger_actual_price_update():
    """
    Manually trigger actual price update

    Updates actual prices for comparison with predictions
    """
    try:
        logger.info("Manual trigger: Actual price update")

        await activity_logger.log_activity(
            activity_type="system",
            message="Actual price update manually triggered"
        )

        # Trigger in background
        import asyncio
        asyncio.create_task(prediction_engine.update_actual_prices())

        return {
            "success": True,
            "message": "Actual price update triggered",
            "note": "Check activity logs for progress"
        }

    except Exception as e:
        logger.error(f"Error triggering actual price update: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_prediction_stats(db: Session = Depends(get_db)):
    """
    Get prediction engine statistics

    Returns overall performance metrics
    """
    try:
        # Get historical predictions for stats
        historical = prediction_engine.get_historical_predictions(db, limit=1000)

        total_predictions = len(historical)
        correct_predictions = len([p for p in historical if p.get('is_correct') == True])
        accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0

        # Calculate average gains
        predicted_gains = [p.get('predicted_gain_percent', 0) for p in historical]
        actual_gains = [p.get('actual_gain_percent', 0) for p in historical if p.get('actual_gain_percent') is not None]

        avg_predicted_gain = sum(predicted_gains) / len(predicted_gains) if predicted_gains else 0
        avg_actual_gain = sum(actual_gains) / len(actual_gains) if actual_gains else 0

        # Get active predictions count
        active = prediction_engine.get_active_predictions(db, min_gain=0.0)

        return {
            "active_predictions": len(active),
            "total_historical_predictions": total_predictions,
            "correct_predictions": correct_predictions,
            "accuracy_percent": accuracy,
            "average_predicted_gain": avg_predicted_gain,
            "average_actual_gain": avg_actual_gain
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

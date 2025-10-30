"""
Activity log API routes
"""
from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from typing import Optional

from api.models import ActivityLogResponse
from services.activity_logger import activity_logger


router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("/logs")
async def get_activity_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to retrieve"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    symbol: Optional[str] = Query(None, description="Filter by stock symbol")
) -> ActivityLogResponse:
    """
    Get activity logs with optional filtering

    Args:
        limit: Number of logs to retrieve (default: 100, max: 1000)
        activity_type: Filter by activity type (prediction, training, daily_update, etc.)
        symbol: Filter by stock symbol

    Returns:
        List of activity logs sorted by timestamp (newest first)
    """
    try:
        logger.info(f"Fetching activity logs: limit={limit}, type={activity_type}, symbol={symbol}")

        # Apply filters
        if activity_type and symbol:
            # Get by type first, then filter by symbol in memory
            logs = await activity_logger.get_logs_by_type(activity_type, limit=limit * 2)
            logs = [log for log in logs if log.symbol == symbol.upper()]
            logs = logs[:limit]
        elif activity_type:
            logs = await activity_logger.get_logs_by_type(activity_type, limit=limit)
        elif symbol:
            logs = await activity_logger.get_logs_by_symbol(symbol, limit=limit)
        else:
            logs = await activity_logger.get_recent_logs(limit=limit)

        return ActivityLogResponse(
            logs=logs,
            total=len(logs)
        )

    except Exception as e:
        logger.error(f"Error fetching activity logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/types")
async def get_activity_types() -> dict:
    """
    Get list of available activity types

    Returns:
        List of activity types with descriptions
    """
    return {
        "types": [
            {
                "type": "prediction",
                "description": "Stock prediction generated"
            },
            {
                "type": "training",
                "description": "Model training completed"
            },
            {
                "type": "daily_update",
                "description": "Daily routine executed (6 AM WIB)"
            },
            {
                "type": "weekly_retrain",
                "description": "Weekly model retraining (Sunday 2 AM WIB)"
            },
            {
                "type": "portfolio_update",
                "description": "Portfolio modified (stock added/removed)"
            },
            {
                "type": "portfolio_view",
                "description": "Portfolio viewed"
            },
            {
                "type": "settings_update",
                "description": "Settings modified"
            },
            {
                "type": "error",
                "description": "Error occurred"
            }
        ]
    }


@router.get("/logs/summary")
async def get_activity_summary() -> dict:
    """
    Get summary statistics of recent activity

    Returns:
        Summary of activity counts by type (last 24 hours)
    """
    try:
        logger.info("Fetching activity summary")

        # Get all logs from last 24 hours
        all_logs = await activity_logger.get_recent_logs(limit=1000)

        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_logs = [log for log in all_logs if log.timestamp >= cutoff_time]

        # Count by type
        type_counts = {}
        for log in recent_logs:
            type_counts[log.activity_type] = type_counts.get(log.activity_type, 0) + 1

        # Count errors
        error_count = type_counts.get("error", 0)

        # Get most active stocks
        stock_counts = {}
        for log in recent_logs:
            if log.symbol:
                stock_counts[log.symbol] = stock_counts.get(log.symbol, 0) + 1

        # Sort stocks by activity
        top_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "period": "last_24_hours",
            "total_activities": len(recent_logs),
            "by_type": type_counts,
            "error_count": error_count,
            "top_active_stocks": [
                {"symbol": symbol, "count": count}
                for symbol, count in top_stocks
            ],
            "last_activity": recent_logs[0].timestamp.isoformat() if recent_logs else None
        }

    except Exception as e:
        logger.error(f"Error fetching activity summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/logs/clear")
async def clear_old_logs(days: int = Query(30, ge=1, le=365, description="Keep logs from last N days")) -> dict:
    """
    Clear old activity logs (keep only recent)

    Args:
        days: Number of days to keep (default: 30)

    Returns:
        Number of logs cleared
    """
    try:
        logger.info(f"Clearing logs older than {days} days")

        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(days=days)

        # Get all logs
        all_logs = await activity_logger.get_recent_logs(limit=10000)

        # Filter logs to keep
        logs_to_keep = [log for log in all_logs if log.timestamp >= cutoff_time]
        cleared_count = len(all_logs) - len(logs_to_keep)

        # Save filtered logs
        import aiofiles
        import json
        from services.activity_logger import ACTIVITY_LOG_FILE

        async with aiofiles.open(ACTIVITY_LOG_FILE, mode='w') as f:
            for log in logs_to_keep:
                log_dict = log.dict()
                log_dict['timestamp'] = log.timestamp.isoformat()
                await f.write(json.dumps(log_dict) + '\n')

        # Log the cleanup
        await activity_logger.log_activity(
            activity_type="system",
            message=f"Cleared {cleared_count} old logs (kept last {days} days)"
        )

        logger.info(f"Cleared {cleared_count} logs, kept {len(logs_to_keep)} logs")

        return {
            "success": True,
            "cleared": cleared_count,
            "kept": len(logs_to_keep),
            "cutoff_date": cutoff_time.isoformat()
        }

    except Exception as e:
        logger.error(f"Error clearing old logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

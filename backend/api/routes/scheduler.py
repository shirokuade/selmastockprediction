"""
Scheduler management API routes
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from services.scheduler import scheduler_service
from services.activity_logger import activity_logger


router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


@router.get("/status")
async def get_scheduler_status():
    """
    Get scheduler status and next run times

    Returns:
        Scheduler status with next scheduled times for daily and weekly routines
    """
    try:
        next_runs = scheduler_service.get_next_run_times()

        return {
            "status": "running" if scheduler_service.scheduler else "stopped",
            "timezone": "Asia/Jakarta (WIB)",
            "schedules": {
                "daily_prediction": {
                    "description": "Generate predictions for portfolio stocks",
                    "schedule": "Every day at 6:00 AM WIB",
                    "next_run": next_runs.get("daily_prediction")
                },
                "weekly_retrain": {
                    "description": "Retrain all models with 5 years data",
                    "schedule": "Every Sunday at 2:00 AM WIB",
                    "next_run": next_runs.get("weekly_retrain")
                }
            }
        }

    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/daily")
async def trigger_daily_routine():
    """
    Manually trigger the daily prediction routine

    Use this to test the daily routine or run predictions on demand.
    """
    try:
        logger.info("Manual trigger: Daily prediction routine")

        # Log the manual trigger
        await activity_logger.log_activity(
            activity_type="system",
            message="Daily prediction routine manually triggered"
        )

        # Trigger in background (don't wait for completion)
        import asyncio
        asyncio.create_task(scheduler_service.trigger_daily_routine_now())

        return {
            "success": True,
            "message": "Daily prediction routine triggered successfully",
            "note": "Check activity logs for progress"
        }

    except Exception as e:
        logger.error(f"Error triggering daily routine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger/weekly")
async def trigger_weekly_routine():
    """
    Manually trigger the weekly retraining routine

    Warning: This will retrain all models and may take 10-30 minutes.
    """
    try:
        logger.info("Manual trigger: Weekly retraining routine")

        # Log the manual trigger
        await activity_logger.log_activity(
            activity_type="system",
            message="Weekly retraining routine manually triggered"
        )

        # Trigger in background (don't wait for completion)
        import asyncio
        asyncio.create_task(scheduler_service.trigger_weekly_routine_now())

        return {
            "success": True,
            "message": "Weekly retraining routine triggered successfully",
            "warning": "This process may take 10-30 minutes",
            "note": "Check activity logs for progress"
        }

    except Exception as e:
        logger.error(f"Error triggering weekly routine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs")
async def list_scheduled_jobs():
    """
    List all scheduled jobs with details

    Returns:
        List of scheduled jobs with their next run times
    """
    try:
        if not scheduler_service.scheduler:
            return {
                "jobs": [],
                "message": "Scheduler not running"
            }

        jobs = []
        for job in scheduler_service.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return {
            "jobs": jobs,
            "total": len(jobs)
        }

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

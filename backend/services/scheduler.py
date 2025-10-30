"""
Background job scheduler for automated predictions and training
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from datetime import datetime
import pytz
import asyncio
from typing import Optional

from services.ensemble_predictor import EnsemblePredictor
from services.portfolio_manager import portfolio_manager
from services.activity_logger import activity_logger
from services.stock_data_fetcher import StockDataFetcher
from config import settings


class SchedulerService:
    """
    Background scheduler for automated stock prediction and model training

    Schedules:
    - Daily at 6 AM WIB: Fetch latest data and generate predictions for portfolio stocks
    - Weekly Sunday 2 AM WIB: Retrain all models with 5 years of historical data
    """

    def __init__(self):
        self.scheduler: Optional[AsyncIOScheduler] = None
        self.predictor = EnsemblePredictor()
        self.data_fetcher = StockDataFetcher()
        self.timezone = pytz.timezone('Asia/Jakarta')  # WIB timezone

    async def start(self):
        """Start the scheduler"""
        if self.scheduler is not None:
            logger.warning("Scheduler already running")
            return

        self.scheduler = AsyncIOScheduler(timezone=self.timezone)

        # Daily routine: 6 AM WIB - Generate predictions
        self.scheduler.add_job(
            self.daily_prediction_routine,
            trigger=CronTrigger(hour=6, minute=0, timezone=self.timezone),
            id='daily_prediction',
            name='Daily Prediction Routine (6 AM WIB)',
            replace_existing=True
        )

        # Weekly routine: Sunday 2 AM WIB - Retrain models
        self.scheduler.add_job(
            self.weekly_retraining_routine,
            trigger=CronTrigger(day_of_week='sun', hour=2, minute=0, timezone=self.timezone),
            id='weekly_retrain',
            name='Weekly Model Retraining (Sunday 2 AM WIB)',
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Scheduler started successfully")
        logger.info("Daily predictions scheduled: Every day at 6:00 AM WIB")
        logger.info("Weekly retraining scheduled: Every Sunday at 2:00 AM WIB")

        # Log initial startup
        await activity_logger.log_activity(
            activity_type="system",
            message="Scheduler started - Daily predictions (6 AM WIB) and Weekly retraining (Sunday 2 AM WIB) enabled"
        )

    async def stop(self):
        """Stop the scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            logger.info("Scheduler stopped")

            await activity_logger.log_activity(
                activity_type="system",
                message="Scheduler stopped"
            )

    async def daily_prediction_routine(self):
        """
        Daily routine executed at 6 AM WIB

        Tasks:
        1. Get all stocks in user's portfolio
        2. Fetch latest hourly data for each stock
        3. Generate predictions with ensemble model
        4. Calculate BUY/HOLD/SELL signals
        5. Log activities
        """
        start_time = datetime.now(self.timezone)
        logger.info("=" * 80)
        logger.info(f"Starting daily prediction routine at {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info("=" * 80)

        try:
            # Get portfolio stocks
            portfolio_stocks = await portfolio_manager.get_portfolio_stocks()

            if not portfolio_stocks:
                logger.info("No stocks in portfolio, using default stock list")
                # Use top 5 Indonesian stocks as default
                portfolio_stocks = ["BBCA", "BMRI", "BBRI", "TLKM", "ASII"]

            logger.info(f"Processing {len(portfolio_stocks)} stocks: {', '.join(portfolio_stocks)}")

            successful = 0
            failed = 0
            predictions_summary = []

            for symbol in portfolio_stocks:
                try:
                    logger.info(f"Processing {symbol}...")

                    # Generate prediction with ensemble model
                    result = await self.predictor.predict(symbol, days=5)

                    if result:
                        successful += 1
                        predictions_summary.append({
                            "symbol": symbol,
                            "signal": result.signal,
                            "current_price": result.current_price,
                            "confidence": result.confidence
                        })

                        # Log individual prediction
                        await activity_logger.log_activity(
                            activity_type="daily_update",
                            message=f"Daily prediction for {symbol}: {result.signal} (Confidence: {result.confidence:.2%})",
                            symbol=symbol,
                            details={
                                "signal": result.signal,
                                "current_price": result.current_price,
                                "confidence": result.confidence,
                                "trend": result.trend
                            }
                        )

                        logger.info(f"✓ {symbol}: {result.signal} | Price: ${result.current_price:.2f} | Confidence: {result.confidence:.2%}")
                    else:
                        failed += 1
                        logger.error(f"✗ {symbol}: Failed to generate prediction")

                        await activity_logger.log_activity(
                            activity_type="error",
                            message=f"Daily prediction failed for {symbol}",
                            symbol=symbol
                        )

                except Exception as e:
                    failed += 1
                    logger.error(f"✗ {symbol}: Error - {str(e)}")

                    await activity_logger.log_activity(
                        activity_type="error",
                        message=f"Daily prediction error for {symbol}: {str(e)}",
                        symbol=symbol
                    )

                # Small delay between stocks to avoid rate limiting
                await asyncio.sleep(2)

            # Log summary
            end_time = datetime.now(self.timezone)
            duration = (end_time - start_time).total_seconds()

            summary_msg = f"Daily routine completed: {successful} successful, {failed} failed ({duration:.1f}s)"
            logger.info("=" * 80)
            logger.info(summary_msg)
            logger.info("=" * 80)

            await activity_logger.log_activity(
                activity_type="daily_update",
                message=summary_msg,
                details={
                    "successful": successful,
                    "failed": failed,
                    "duration_seconds": duration,
                    "predictions": predictions_summary
                }
            )

        except Exception as e:
            logger.error(f"Daily routine error: {str(e)}")

            await activity_logger.log_activity(
                activity_type="error",
                message=f"Daily routine failed: {str(e)}"
            )

    async def weekly_retraining_routine(self):
        """
        Weekly routine executed every Sunday at 2 AM WIB

        Tasks:
        1. Get all stocks in portfolio + default stocks
        2. Retrain all 3 ensemble models with 5 years of daily data
        3. Save updated models
        4. Log training metrics
        """
        start_time = datetime.now(self.timezone)
        logger.info("=" * 80)
        logger.info(f"Starting weekly retraining routine at {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info("=" * 80)

        try:
            # Get all stocks (portfolio + defaults)
            portfolio_stocks = await portfolio_manager.get_portfolio_stocks()
            default_stocks = ["BBCA", "BMRI", "BBRI", "TLKM", "ASII"]

            # Combine and deduplicate
            all_stocks = list(set(portfolio_stocks + default_stocks))

            logger.info(f"Retraining models for {len(all_stocks)} stocks: {', '.join(all_stocks)}")

            successful = 0
            failed = 0
            training_results = []

            for symbol in all_stocks:
                try:
                    logger.info(f"Training {symbol}...")

                    # Train ensemble model (trains all 3 models)
                    success = await self.predictor.train_model(symbol)

                    if success:
                        successful += 1
                        training_results.append({
                            "symbol": symbol,
                            "status": "success"
                        })

                        # Log individual training
                        await activity_logger.log_activity(
                            activity_type="weekly_retrain",
                            message=f"Weekly retrain completed for {symbol}",
                            symbol=symbol,
                            details={
                                "models": ["XGBoost", "LightGBM", "Random Forest"],
                                "training_period": "5 years",
                                "data_interval": "daily"
                            }
                        )

                        logger.info(f"✓ {symbol}: Training completed successfully")
                    else:
                        failed += 1
                        logger.error(f"✗ {symbol}: Training failed")

                        await activity_logger.log_activity(
                            activity_type="error",
                            message=f"Weekly retrain failed for {symbol}",
                            symbol=symbol
                        )

                except Exception as e:
                    failed += 1
                    logger.error(f"✗ {symbol}: Training error - {str(e)}")

                    await activity_logger.log_activity(
                        activity_type="error",
                        message=f"Weekly retrain error for {symbol}: {str(e)}",
                        symbol=symbol
                    )

                # Delay between training to avoid overload
                await asyncio.sleep(5)

            # Log summary
            end_time = datetime.now(self.timezone)
            duration = (end_time - start_time).total_seconds()

            summary_msg = f"Weekly retraining completed: {successful} successful, {failed} failed ({duration:.1f}s)"
            logger.info("=" * 80)
            logger.info(summary_msg)
            logger.info("=" * 80)

            await activity_logger.log_activity(
                activity_type="weekly_retrain",
                message=summary_msg,
                details={
                    "successful": successful,
                    "failed": failed,
                    "duration_seconds": duration,
                    "stocks_trained": training_results
                }
            )

        except Exception as e:
            logger.error(f"Weekly retraining error: {str(e)}")

            await activity_logger.log_activity(
                activity_type="error",
                message=f"Weekly retraining failed: {str(e)}"
            )

    async def trigger_daily_routine_now(self):
        """Manually trigger daily routine (for testing)"""
        logger.info("Manually triggering daily prediction routine...")
        await self.daily_prediction_routine()

    async def trigger_weekly_routine_now(self):
        """Manually trigger weekly routine (for testing)"""
        logger.info("Manually triggering weekly retraining routine...")
        await self.weekly_retraining_routine()

    def get_next_run_times(self) -> dict:
        """Get next scheduled run times"""
        if not self.scheduler:
            return {"daily": None, "weekly": None}

        jobs = {}
        for job in self.scheduler.get_jobs():
            jobs[job.id] = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S %Z') if job.next_run_time else None

        return {
            "daily_prediction": jobs.get("daily_prediction"),
            "weekly_retrain": jobs.get("weekly_retrain")
        }


# Global scheduler instance
scheduler_service = SchedulerService()

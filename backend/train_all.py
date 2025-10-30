"""
Script to train models for all Indonesian stocks
"""
import asyncio
from loguru import logger
from config import settings
from services.predictor import StockPredictor


async def train_all_stocks():
    """Train models for all Indonesian stocks"""
    predictor = StockPredictor()

    logger.info(f"Training models for {len(settings.idx_stocks)} stocks")

    for i, symbol in enumerate(settings.idx_stocks):
        logger.info(f"[{i+1}/{len(settings.idx_stocks)}] Training model for {symbol}")

        try:
            success = await predictor.train_model(symbol)
            if success:
                logger.info(f"✓ Successfully trained model for {symbol}")
            else:
                logger.error(f"✗ Failed to train model for {symbol}")

        except Exception as e:
            logger.error(f"✗ Error training {symbol}: {str(e)}")

        # Add delay to avoid rate limiting
        await asyncio.sleep(2)

    logger.info("Training completed for all stocks")


if __name__ == "__main__":
    asyncio.run(train_all_stocks())

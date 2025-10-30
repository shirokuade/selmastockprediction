"""
Simple script to test the API endpoints
"""
import asyncio
import aiohttp
from loguru import logger


BASE_URL = "http://localhost:8000"


async def test_endpoints():
    """Test all API endpoints"""
    async with aiohttp.ClientSession() as session:

        # Test root endpoint
        logger.info("Testing root endpoint...")
        async with session.get(f"{BASE_URL}/") as response:
            data = await response.json()
            logger.info(f"Root: {data}")

        # Test health check
        logger.info("Testing health check...")
        async with session.get(f"{BASE_URL}/health") as response:
            data = await response.json()
            logger.info(f"Health: {data}")

        # Test available stocks
        logger.info("Testing available stocks...")
        async with session.get(f"{BASE_URL}/api/stock/available") as response:
            data = await response.json()
            logger.info(f"Available stocks: {data['total']} stocks")

        # Test stock validation
        logger.info("Testing stock validation...")
        async with session.get(f"{BASE_URL}/api/stock/validate/BBCA") as response:
            data = await response.json()
            logger.info(f"Validation: {data}")

        # Test stock info
        logger.info("Testing stock info...")
        async with session.post(
            f"{BASE_URL}/api/stock/info",
            json={"symbol": "BBCA"}
        ) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Stock info: {data['symbol']} - ${data['current_price']}")
            else:
                logger.error(f"Stock info failed: {response.status}")

        # Test prediction
        logger.info("Testing prediction...")
        async with session.post(
            f"{BASE_URL}/api/prediction/predict",
            json={"symbol": "BBCA", "days": 5}
        ) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Prediction: {data['symbol']} - Trend: {data['trend']}")
                logger.info(f"Predictions: {len(data['predictions'])} days")
            else:
                logger.error(f"Prediction failed: {response.status}")

        # Test settings
        logger.info("Testing save settings...")
        async with session.post(
            f"{BASE_URL}/api/settings/save",
            json={
                "default_stock": "BBCA",
                "prediction_days": 5,
                "notification_enabled": False
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(f"Settings saved: {data}")
            else:
                logger.error(f"Save settings failed: {response.status}")

        logger.info("All tests completed!")


if __name__ == "__main__":
    asyncio.run(test_endpoints())

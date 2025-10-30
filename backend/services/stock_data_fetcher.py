"""
Stock data fetcher for Indonesian stocks using Yahoo Finance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
from typing import Optional, Dict
import asyncio
from functools import lru_cache

from config import settings
from api.models import StockData


class StockDataFetcher:
    """Fetch stock data from Yahoo Finance for Indonesian stocks"""

    def __init__(self):
        self.cache_duration = 300  # 5 minutes cache

    def _get_yahoo_symbol(self, symbol: str) -> str:
        """Convert stock symbol to Yahoo Finance format"""
        return settings.get_stock_symbol(symbol)

    async def get_stock_info(self, symbol: str) -> Optional[StockData]:
        """
        Get current stock information

        Args:
            symbol: Stock symbol (e.g., BBCA, BMDR)

        Returns:
            StockData object or None if not found
        """
        try:
            yahoo_symbol = self._get_yahoo_symbol(symbol)
            logger.info(f"Fetching stock info for {yahoo_symbol}")

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, yahoo_symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            hist = await loop.run_in_executor(
                None,
                lambda: ticker.history(period="5d")
            )

            if hist.empty:
                logger.warning(f"No data found for {yahoo_symbol}")
                return None

            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_close
            change_percent = (change / prev_close * 100) if prev_close else 0

            return StockData(
                symbol=symbol.upper(),
                name=info.get('longName', symbol),
                current_price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]) if 'Volume' in hist else None,
                market_cap=info.get('marketCap'),
                last_updated=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
            return None

    async def get_stock_history(
        self,
        symbol: str,
        days: int = 365,
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical stock data

        Args:
            symbol: Stock symbol
            days: Number of days of history
            interval: Data interval (1d, 1h, etc.)

        Returns:
            DataFrame with historical data or None
        """
        try:
            yahoo_symbol = self._get_yahoo_symbol(symbol)
            logger.info(f"Fetching {days} days of history for {yahoo_symbol}")

            # Calculate start and end dates
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Fetch data
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, yahoo_symbol)
            history = await loop.run_in_executor(
                None,
                lambda: ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )
            )

            if history.empty:
                logger.warning(f"No historical data found for {yahoo_symbol}")
                return None

            # Clean and format data
            history = history.reset_index()
            history['Date'] = pd.to_datetime(history['Date'])
            history = history.sort_values('Date')

            logger.info(f"Fetched {len(history)} records for {symbol}")
            return history

        except Exception as e:
            logger.error(f"Error fetching history for {symbol}: {str(e)}")
            return None

    async def get_multiple_stocks(self, symbols: list) -> Dict[str, StockData]:
        """
        Get information for multiple stocks concurrently

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary of symbol -> StockData
        """
        try:
            tasks = [self.get_stock_info(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            stock_data = {}
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {symbol}: {str(result)}")
                    continue
                if result:
                    stock_data[symbol] = result

            return stock_data

        except Exception as e:
            logger.error(f"Error fetching multiple stocks: {str(e)}")
            return {}

    async def validate_symbol_exists(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists and has data

        Args:
            symbol: Stock symbol

        Returns:
            True if symbol exists and has data
        """
        try:
            stock_data = await self.get_stock_info(symbol)
            return stock_data is not None
        except Exception:
            return False

    async def get_market_summary(self) -> Dict:
        """
        Get summary of Indonesian market

        Returns:
            Market summary data
        """
        try:
            # Get data for major stocks
            major_stocks = settings.idx_stocks[:5]  # Top 5 stocks
            stock_data = await self.get_multiple_stocks(major_stocks)

            # Calculate market metrics
            total_change = sum(
                data.change_percent
                for data in stock_data.values()
                if data.change_percent
            )
            avg_change = total_change / len(stock_data) if stock_data else 0

            return {
                "market": settings.default_market,
                "stocks_tracked": len(stock_data),
                "average_change_percent": avg_change,
                "top_stocks": [
                    {
                        "symbol": symbol,
                        "price": data.current_price,
                        "change_percent": data.change_percent
                    }
                    for symbol, data in stock_data.items()
                ],
                "timestamp": datetime.now()
            }

        except Exception as e:
            logger.error(f"Error getting market summary: {str(e)}")
            return {
                "market": settings.default_market,
                "error": str(e),
                "timestamp": datetime.now()
            }

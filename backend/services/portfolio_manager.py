"""
Portfolio management service
Tracks user's stock holdings and calculates current values
"""
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from loguru import logger
import aiofiles

from api.models import PortfolioStock, PortfolioResponse
from services.stock_data_fetcher import StockDataFetcher


class PortfolioManager:
    """Manage user portfolio"""

    def __init__(self):
        self.portfolio_dir = "./user_portfolio"
        self.portfolio_file = os.path.join(self.portfolio_dir, "portfolio.json")
        self.stock_fetcher = StockDataFetcher()
        self._ensure_portfolio_dir()

    def _ensure_portfolio_dir(self):
        """Create portfolio directory if it doesn't exist"""
        if not os.path.exists(self.portfolio_dir):
            os.makedirs(self.portfolio_dir)
            logger.info(f"Created portfolio directory: {self.portfolio_dir}")

    async def add_stock(
        self,
        symbol: str,
        shares: int,
        purchase_price: float,
        purchase_date: Optional[str] = None
    ) -> bool:
        """
        Add stock to portfolio

        Args:
            symbol: Stock symbol
            shares: Number of shares
            purchase_price: Purchase price per share
            purchase_date: Date of purchase (optional)

        Returns:
            True if successful
        """
        try:
            # Load existing portfolio
            portfolio = await self._load_portfolio()

            # Create or update stock entry
            stock_data = {
                "symbol": symbol.upper(),
                "shares": shares,
                "purchase_price": purchase_price,
                "purchase_date": purchase_date or datetime.now().strftime("%Y-%m-%d"),
                "added_at": datetime.now().isoformat()
            }

            # Check if stock already exists
            existing_index = None
            for i, stock in enumerate(portfolio):
                if stock["symbol"] == symbol.upper():
                    existing_index = i
                    break

            if existing_index is not None:
                # Update existing stock
                portfolio[existing_index] = stock_data
                logger.info(f"Updated {symbol} in portfolio")
            else:
                # Add new stock
                portfolio.append(stock_data)
                logger.info(f"Added {symbol} to portfolio")

            # Save portfolio
            await self._save_portfolio(portfolio)
            return True

        except Exception as e:
            logger.error(f"Error adding stock to portfolio: {str(e)}")
            return False

    async def remove_stock(self, symbol: str) -> bool:
        """
        Remove stock from portfolio

        Args:
            symbol: Stock symbol to remove

        Returns:
            True if successful
        """
        try:
            portfolio = await self._load_portfolio()

            # Find and remove stock
            updated_portfolio = [
                stock for stock in portfolio
                if stock["symbol"] != symbol.upper()
            ]

            if len(updated_portfolio) == len(portfolio):
                logger.warning(f"Stock {symbol} not found in portfolio")
                return False

            await self._save_portfolio(updated_portfolio)
            logger.info(f"Removed {symbol} from portfolio")
            return True

        except Exception as e:
            logger.error(f"Error removing stock from portfolio: {str(e)}")
            return False

    async def get_portfolio(self) -> PortfolioResponse:
        """
        Get portfolio with current values calculated

        Returns:
            PortfolioResponse with all calculations
        """
        try:
            portfolio = await self._load_portfolio()

            if not portfolio:
                return PortfolioResponse(
                    stocks=[],
                    total_investment=0.0,
                    current_value=0.0,
                    total_gain_loss=0.0,
                    total_gain_loss_percent=0.0,
                    last_updated=datetime.now()
                )

            # Get current prices for all stocks
            stocks_with_values = []
            total_investment = 0.0
            total_current_value = 0.0

            for stock in portfolio:
                symbol = stock["symbol"]
                shares = stock["shares"]
                purchase_price = stock["purchase_price"]
                purchase_date = stock.get("purchase_date")

                # Get current price
                stock_info = await self.stock_fetcher.get_stock_info(symbol)

                if stock_info and stock_info.current_price:
                    current_price = stock_info.current_price
                else:
                    # Fallback to purchase price if can't fetch current
                    current_price = purchase_price
                    logger.warning(f"Could not fetch current price for {symbol}, using purchase price")

                # Calculate values
                investment = shares * purchase_price
                current_value = shares * current_price
                gain_loss = current_value - investment
                gain_loss_percent = (gain_loss / investment * 100) if investment > 0 else 0

                stocks_with_values.append({
                    "symbol": symbol,
                    "shares": shares,
                    "purchase_price": purchase_price,
                    "purchase_date": purchase_date,
                    "current_price": current_price,
                    "investment": investment,
                    "current_value": current_value,
                    "gain_loss": gain_loss,
                    "gain_loss_percent": gain_loss_percent,
                    "change": stock_info.change if stock_info else 0,
                    "change_percent": stock_info.change_percent if stock_info else 0
                })

                total_investment += investment
                total_current_value += current_value

            # Calculate totals
            total_gain_loss = total_current_value - total_investment
            total_gain_loss_percent = (
                (total_gain_loss / total_investment * 100)
                if total_investment > 0 else 0
            )

            return PortfolioResponse(
                stocks=stocks_with_values,
                total_investment=round(total_investment, 2),
                current_value=round(total_current_value, 2),
                total_gain_loss=round(total_gain_loss, 2),
                total_gain_loss_percent=round(total_gain_loss_percent, 2),
                last_updated=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            # Return empty portfolio on error
            return PortfolioResponse(
                stocks=[],
                total_investment=0.0,
                current_value=0.0,
                total_gain_loss=0.0,
                total_gain_loss_percent=0.0,
                last_updated=datetime.now()
            )

    async def get_portfolio_stocks(self) -> List[str]:
        """
        Get list of stock symbols in portfolio

        Returns:
            List of stock symbols
        """
        try:
            portfolio = await self._load_portfolio()
            return [stock["symbol"] for stock in portfolio]
        except Exception as e:
            logger.error(f"Error getting portfolio stocks: {str(e)}")
            return []

    async def _load_portfolio(self) -> List[Dict]:
        """Load portfolio from file"""
        try:
            if not os.path.exists(self.portfolio_file):
                return []

            async with aiofiles.open(self.portfolio_file, mode='r') as f:
                content = await f.read()
                return json.loads(content) if content.strip() else []

        except json.JSONDecodeError:
            logger.warning("Invalid JSON in portfolio file, returning empty portfolio")
            return []
        except Exception as e:
            logger.error(f"Error loading portfolio: {str(e)}")
            return []

    async def _save_portfolio(self, portfolio: List[Dict]) -> bool:
        """Save portfolio to file"""
        try:
            async with aiofiles.open(self.portfolio_file, mode='w') as f:
                await f.write(json.dumps(portfolio, indent=2))
            logger.info("Portfolio saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving portfolio: {str(e)}")
            return False


# Global instance
portfolio_manager = PortfolioManager()

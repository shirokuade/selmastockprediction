"""
Portfolio management API routes
"""
from fastapi import APIRouter, HTTPException
from loguru import logger

from api.models import (
    AddPortfolioStockRequest,
    PortfolioResponse,
    SuccessResponse
)
from services.portfolio_manager import portfolio_manager
from services.activity_logger import activity_logger


router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.post("/add")
async def add_portfolio_stock(request: AddPortfolioStockRequest) -> SuccessResponse:
    """
    Add stock to user's portfolio

    Args:
        request: Stock details (symbol, shares, purchase_price, purchase_date)

    Returns:
        Success response
    """
    try:
        logger.info(f"Adding {request.symbol} to portfolio: {request.shares} shares @ {request.purchase_price}")

        success = await portfolio_manager.add_stock(
            symbol=request.symbol,
            shares=request.shares,
            purchase_price=request.purchase_price,
            purchase_date=request.purchase_date
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to add stock to portfolio")

        # Log activity
        await activity_logger.log_activity(
            activity_type="portfolio_update",
            message=f"Added {request.shares} shares of {request.symbol} to portfolio",
            symbol=request.symbol,
            details={
                "shares": request.shares,
                "purchase_price": request.purchase_price,
                "purchase_date": request.purchase_date
            }
        )

        return SuccessResponse(
            success=True,
            message=f"Successfully added {request.symbol} to portfolio"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding stock to portfolio: {str(e)}")

        # Log error
        await activity_logger.log_activity(
            activity_type="error",
            message=f"Failed to add {request.symbol} to portfolio: {str(e)}",
            symbol=request.symbol
        )

        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_portfolio() -> PortfolioResponse:
    """
    Get user's portfolio with current values and calculations

    Returns:
        Portfolio with all stocks, current values, gains/losses
    """
    try:
        logger.info("Fetching portfolio")

        portfolio = await portfolio_manager.get_portfolio()

        # Log activity
        await activity_logger.log_activity(
            activity_type="portfolio_view",
            message=f"Portfolio viewed: {len(portfolio.stocks)} stocks, Total: ${portfolio.current_value:.2f}"
        )

        return portfolio

    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")

        # Log error
        await activity_logger.log_activity(
            activity_type="error",
            message=f"Failed to fetch portfolio: {str(e)}"
        )

        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{symbol}")
async def remove_portfolio_stock(symbol: str) -> SuccessResponse:
    """
    Remove stock from user's portfolio

    Args:
        symbol: Stock symbol to remove

    Returns:
        Success response
    """
    try:
        logger.info(f"Removing {symbol} from portfolio")

        success = await portfolio_manager.remove_stock(symbol)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Stock {symbol} not found in portfolio"
            )

        # Log activity
        await activity_logger.log_activity(
            activity_type="portfolio_update",
            message=f"Removed {symbol} from portfolio",
            symbol=symbol
        )

        return SuccessResponse(
            success=True,
            message=f"Successfully removed {symbol} from portfolio"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing stock from portfolio: {str(e)}")

        # Log error
        await activity_logger.log_activity(
            activity_type="error",
            message=f"Failed to remove {symbol} from portfolio: {str(e)}",
            symbol=symbol
        )

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/list")
async def get_portfolio_stocks() -> dict:
    """
    Get list of stock symbols in portfolio

    Returns:
        List of stock symbols
    """
    try:
        logger.info("Fetching portfolio stock list")

        stocks = await portfolio_manager.get_portfolio_stocks()

        return {
            "symbols": stocks,
            "count": len(stocks)
        }

    except Exception as e:
        logger.error(f"Error fetching portfolio stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

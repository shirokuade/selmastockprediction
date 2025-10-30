"""
Stock-related API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from datetime import datetime

from api.models import (
    StockSymbolRequest,
    StockData,
    AvailableStocksResponse,
    ErrorResponse
)
from services.stock_data_fetcher import StockDataFetcher
from config import settings

router = APIRouter()
stock_fetcher = StockDataFetcher()


@router.get("/available", response_model=AvailableStocksResponse)
async def get_available_stocks():
    """
    Get list of available Indonesian stocks
    """
    try:
        stocks = [
            {"symbol": symbol, "name": f"{symbol} - Indonesian Stock"}
            for symbol in settings.idx_stocks
        ]

        return AvailableStocksResponse(
            stocks=stocks,
            total=len(stocks)
        )
    except Exception as e:
        logger.error(f"Error fetching available stocks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch available stocks"
        )


@router.post("/info", response_model=StockData)
async def get_stock_info(request: StockSymbolRequest):
    """
    Get current stock information
    """
    try:
        symbol = request.symbol
        logger.info(f"Fetching stock info for: {symbol}")

        # Validate stock symbol
        if not settings.validate_stock_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {symbol}. Must be a valid Indonesian stock."
            )

        # Fetch stock data
        stock_data = await stock_fetcher.get_stock_info(symbol)

        if not stock_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock data not found for: {symbol}"
            )

        return stock_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock information: {str(e)}"
        )


@router.post("/history")
async def get_stock_history(request: StockSymbolRequest, days: int = 365):
    """
    Get historical stock data
    """
    try:
        symbol = request.symbol
        logger.info(f"Fetching stock history for: {symbol}, days: {days}")

        # Validate stock symbol
        if not settings.validate_stock_symbol(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {symbol}"
            )

        # Fetch historical data
        history = await stock_fetcher.get_stock_history(symbol, days)

        if history is None or history.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for: {symbol}"
            )

        # Convert to JSON-serializable format
        history_dict = history.reset_index().to_dict(orient="records")

        return {
            "symbol": symbol,
            "data": history_dict,
            "total_records": len(history_dict)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stock history: {str(e)}"
        )


@router.get("/validate/{symbol}")
async def validate_stock_symbol(symbol: str):
    """
    Validate if a stock symbol is valid for Indonesian market
    """
    try:
        is_valid = settings.validate_stock_symbol(symbol)
        yahoo_symbol = settings.get_stock_symbol(symbol)

        return {
            "symbol": symbol.upper(),
            "is_valid": is_valid,
            "yahoo_symbol": yahoo_symbol,
            "market": settings.default_market
        }
    except Exception as e:
        logger.error(f"Error validating stock symbol: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate stock symbol"
        )

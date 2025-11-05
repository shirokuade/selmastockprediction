"""
Beta AI Engine API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List
from loguru import logger

from services.beta_predictor import beta_predictor


router = APIRouter(prefix="/api/beta", tags=["beta"])


class AnalyzeRequest(BaseModel):
    """Request model for beta analysis"""
    stocks: List[str] = Field(..., min_items=2, max_items=2, description="Exactly 2 stock symbols")
    weeks: int = Field(4, ge=1, le=12, description="Number of weeks to analyze (1-12)")


@router.post("/analyze")
async def analyze_stocks(request: AnalyzeRequest):
    """
    Deep analysis of 2 stocks using Beta AI Engine

    Combines:
    - Enhanced technical analysis (30+ indicators)
    - Sentiment analysis (news, market mood)
    - Hybrid AI prediction
    - Comparative analysis

    Args:
        request: AnalyzeRequest with 2 stocks and weeks

    Returns:
        Detailed analysis results with predictions and insights
    """
    try:
        logger.info(f"Beta analysis request: {request.stocks}, {request.weeks} weeks")

        # Validate stocks are different
        if request.stocks[0] == request.stocks[1]:
            raise HTTPException(
                status_code=400,
                detail="Please select two different stocks"
            )

        # Run analysis
        result = await beta_predictor.analyze_stocks(
            symbols=request.stocks,
            weeks=request.weeks
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Beta analysis error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for Beta engine"""
    return {
        "status": "healthy",
        "engine": "Beta AI Engine",
        "version": "1.0.0-experimental"
    }

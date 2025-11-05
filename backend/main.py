"""
Main FastAPI application for Indonesian Stock Prediction using Qlib
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from config import settings
from api.routes import stock, prediction, settings as settings_routes, portfolio, activity, scheduler, prediction_engine, beta
from services.scheduler import scheduler_service
from database.models import init_db
from services.prediction_engine import prediction_engine as pred_engine

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    level=settings.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)
logger.add(
    settings.log_file,
    rotation="10 MB",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Stock Prediction API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Model Type: {settings.model_type}")

    # Create necessary directories
    import os
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.qlib_data_dir, exist_ok=True)
    os.makedirs(settings.model_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("user_portfolio", exist_ok=True)
    os.makedirs("activity_logs", exist_ok=True)

    logger.info("Directories created successfully")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Initialize prediction engine
    logger.info("Initializing prediction engine...")
    await pred_engine.initialize_top_100_stocks()

    # Start background scheduler
    logger.info("Starting background scheduler...")
    await scheduler_service.start()

    yield

    # Stop scheduler on shutdown
    logger.info("Stopping background scheduler...")
    await scheduler_service.stop()

    logger.info("Shutting down Stock Prediction API...")


# Initialize FastAPI app
app = FastAPI(
    title="Indonesian Stock Prediction API",
    description="AI-powered stock prediction system using Microsoft Qlib for Indonesian stocks",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Indonesian Stock Prediction API",
        "version": "1.0.0",
        "status": "running",
        "market": settings.default_market
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment
    }


# Include routers
app.include_router(stock.router, prefix="/api/stock", tags=["Stock"])
app.include_router(prediction.router, prefix="/api/prediction", tags=["Prediction"])
app.include_router(settings_routes.router, prefix="/api/settings", tags=["Settings"])
app.include_router(portfolio.router, tags=["Portfolio"])
app.include_router(activity.router, tags=["Activity"])
app.include_router(scheduler.router, tags=["Scheduler"])
app.include_router(prediction_engine.router, tags=["Prediction Engine"])
app.include_router(beta.router, tags=["Beta AI Engine"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.environment == "development" else "An error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )

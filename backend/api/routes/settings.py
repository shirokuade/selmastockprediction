"""
Settings-related API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from loguru import logger
from datetime import datetime
from typing import Optional

from api.models import UserSettings, UserSettingsResponse
from services.settings_manager import SettingsManager
from config import settings as app_settings

router = APIRouter()
settings_manager = SettingsManager()


@router.post("/save", response_model=UserSettingsResponse)
async def save_settings(settings: UserSettings):
    """
    Save user settings
    """
    try:
        logger.info(f"Saving settings for stock: {settings.default_stock}")

        # Validate stock symbol
        if not app_settings.validate_stock_symbol(settings.default_stock):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {settings.default_stock}"
            )

        # Save settings
        success = await settings_manager.save_settings(settings)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save settings"
            )

        return UserSettingsResponse(
            settings=settings,
            saved_at=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save settings: {str(e)}"
        )


@router.get("/get", response_model=UserSettingsResponse)
async def get_settings(user_id: Optional[str] = "default"):
    """
    Get user settings
    """
    try:
        logger.info(f"Fetching settings for user: {user_id}")

        # Get settings
        user_settings = await settings_manager.get_settings(user_id)

        if not user_settings:
            # Return default settings
            user_settings = UserSettings(
                default_stock="BBCA",
                prediction_days=5,
                notification_enabled=False
            )

        return UserSettingsResponse(
            settings=user_settings,
            saved_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error fetching settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}"
        )


@router.put("/update", response_model=UserSettingsResponse)
async def update_settings(settings: UserSettings, user_id: Optional[str] = "default"):
    """
    Update user settings
    """
    try:
        logger.info(f"Updating settings for user: {user_id}")

        # Validate stock symbol
        if not app_settings.validate_stock_symbol(settings.default_stock):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol: {settings.default_stock}"
            )

        # Update settings
        success = await settings_manager.update_settings(user_id, settings)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings"
            )

        return UserSettingsResponse(
            settings=settings,
            saved_at=datetime.now()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.delete("/delete")
async def delete_settings(user_id: str = "default"):
    """
    Delete user settings
    """
    try:
        logger.info(f"Deleting settings for user: {user_id}")

        success = await settings_manager.delete_settings(user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete settings"
            )

        return {
            "message": "Settings deleted successfully",
            "user_id": user_id,
            "timestamp": datetime.now()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete settings: {str(e)}"
        )

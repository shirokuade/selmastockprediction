"""
User settings management
"""
import json
import os
from typing import Optional
from loguru import logger
from datetime import datetime
import aiofiles

from api.models import UserSettings
from config import settings as app_settings


class SettingsManager:
    """Manage user settings (store in JSON file for simplicity)"""

    def __init__(self):
        self.settings_dir = "./user_settings"
        self.settings_file = os.path.join(self.settings_dir, "settings.json")
        self._ensure_settings_dir()

    def _ensure_settings_dir(self):
        """Create settings directory if it doesn't exist"""
        if not os.path.exists(self.settings_dir):
            os.makedirs(self.settings_dir)
            logger.info(f"Created settings directory: {self.settings_dir}")

    async def save_settings(self, user_settings: UserSettings, user_id: str = "default") -> bool:
        """
        Save user settings

        Args:
            user_settings: UserSettings object
            user_id: User identifier

        Returns:
            True if successful
        """
        try:
            # Load existing settings
            all_settings = await self._load_all_settings()

            # Update settings for user
            all_settings[user_id] = {
                "default_stock": user_settings.default_stock,
                "prediction_days": user_settings.prediction_days,
                "notification_enabled": user_settings.notification_enabled,
                "updated_at": datetime.now().isoformat()
            }

            # Save to file
            async with aiofiles.open(self.settings_file, 'w') as f:
                await f.write(json.dumps(all_settings, indent=2))

            logger.info(f"Settings saved for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            return False

    async def get_settings(self, user_id: str = "default") -> Optional[UserSettings]:
        """
        Get user settings

        Args:
            user_id: User identifier

        Returns:
            UserSettings object or None
        """
        try:
            all_settings = await self._load_all_settings()

            if user_id not in all_settings:
                logger.info(f"No settings found for user: {user_id}")
                return None

            user_data = all_settings[user_id]
            return UserSettings(
                default_stock=user_data.get("default_stock", "BBCA"),
                prediction_days=user_data.get("prediction_days", 5),
                notification_enabled=user_data.get("notification_enabled", False)
            )

        except Exception as e:
            logger.error(f"Error getting settings: {str(e)}")
            return None

    async def update_settings(self, user_id: str, user_settings: UserSettings) -> bool:
        """
        Update user settings

        Args:
            user_id: User identifier
            user_settings: New settings

        Returns:
            True if successful
        """
        return await self.save_settings(user_settings, user_id)

    async def delete_settings(self, user_id: str) -> bool:
        """
        Delete user settings

        Args:
            user_id: User identifier

        Returns:
            True if successful
        """
        try:
            all_settings = await self._load_all_settings()

            if user_id in all_settings:
                del all_settings[user_id]

                async with aiofiles.open(self.settings_file, 'w') as f:
                    await f.write(json.dumps(all_settings, indent=2))

                logger.info(f"Settings deleted for user: {user_id}")

            return True

        except Exception as e:
            logger.error(f"Error deleting settings: {str(e)}")
            return False

    async def _load_all_settings(self) -> dict:
        """
        Load all settings from file

        Returns:
            Dictionary of all settings
        """
        try:
            if not os.path.exists(self.settings_file):
                return {}

            async with aiofiles.open(self.settings_file, 'r') as f:
                content = await f.read()
                return json.loads(content)

        except json.JSONDecodeError:
            logger.warning("Invalid JSON in settings file, returning empty dict")
            return {}
        except Exception as e:
            logger.error(f"Error loading settings: {str(e)}")
            return {}

    async def get_all_users(self) -> list:
        """
        Get list of all users with saved settings

        Returns:
            List of user IDs
        """
        try:
            all_settings = await self._load_all_settings()
            return list(all_settings.keys())
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            return []

    async def export_settings(self, user_id: str) -> Optional[dict]:
        """
        Export settings for a user

        Args:
            user_id: User identifier

        Returns:
            Settings dictionary or None
        """
        try:
            all_settings = await self._load_all_settings()
            return all_settings.get(user_id)
        except Exception as e:
            logger.error(f"Error exporting settings: {str(e)}")
            return None

    async def import_settings(self, user_id: str, settings_data: dict) -> bool:
        """
        Import settings for a user

        Args:
            user_id: User identifier
            settings_data: Settings dictionary

        Returns:
            True if successful
        """
        try:
            user_settings = UserSettings(**settings_data)
            return await self.save_settings(user_settings, user_id)
        except Exception as e:
            logger.error(f"Error importing settings: {str(e)}")
            return False

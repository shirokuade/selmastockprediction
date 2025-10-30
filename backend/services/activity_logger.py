"""
Activity logging service for tracking all system activities
Logs predictions, training, updates, and errors
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from loguru import logger
import aiofiles

from api.models import ActivityLog


class ActivityLogger:
    """Manage activity logs for system monitoring"""

    def __init__(self):
        self.log_dir = "./activity_logs"
        self.log_file = os.path.join(self.log_dir, "activities.jsonl")
        self._ensure_log_dir()

    def _ensure_log_dir(self):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            logger.info(f"Created activity log directory: {self.log_dir}")

    async def log_activity(
        self,
        activity_type: str,
        message: str,
        symbol: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """
        Log an activity

        Args:
            activity_type: Type of activity (prediction, training, daily_update, etc.)
            message: Human-readable message
            symbol: Stock symbol (if applicable)
            details: Additional details dictionary
        """
        try:
            activity = ActivityLog(
                timestamp=datetime.now(),
                activity_type=activity_type,
                symbol=symbol,
                message=message,
                details=details
            )

            # Write to file (JSONL format - one JSON per line)
            async with aiofiles.open(self.log_file, mode='a') as f:
                await f.write(activity.model_dump_json() + '\n')

            logger.info(f"Activity logged: {activity_type} - {message}")

        except Exception as e:
            logger.error(f"Error logging activity: {str(e)}")

    async def get_recent_logs(self, limit: int = 100) -> List[ActivityLog]:
        """
        Get recent activity logs

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of ActivityLog objects (newest first)
        """
        try:
            if not os.path.exists(self.log_file):
                return []

            logs = []
            async with aiofiles.open(self.log_file, mode='r') as f:
                content = await f.read()
                lines = content.strip().split('\n')

                # Get last N lines (newest)
                recent_lines = lines[-limit:] if len(lines) > limit else lines

                # Parse each line
                for line in reversed(recent_lines):  # Reverse to get newest first
                    if line.strip():
                        try:
                            log_dict = json.loads(line)
                            logs.append(ActivityLog(**log_dict))
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse log line: {line}")

            return logs

        except Exception as e:
            logger.error(f"Error getting recent logs: {str(e)}")
            return []

    async def get_logs_by_type(
        self,
        activity_type: str,
        limit: int = 50
    ) -> List[ActivityLog]:
        """Get logs filtered by activity type"""
        try:
            all_logs = await self.get_recent_logs(limit=500)  # Get more to filter
            filtered = [log for log in all_logs if log.activity_type == activity_type]
            return filtered[:limit]
        except Exception as e:
            logger.error(f"Error getting logs by type: {str(e)}")
            return []

    async def get_logs_by_symbol(
        self,
        symbol: str,
        limit: int = 50
    ) -> List[ActivityLog]:
        """Get logs filtered by stock symbol"""
        try:
            all_logs = await self.get_recent_logs(limit=500)
            filtered = [log for log in all_logs if log.symbol == symbol]
            return filtered[:limit]
        except Exception as e:
            logger.error(f"Error getting logs by symbol: {str(e)}")
            return []

    async def clear_old_logs(self, days: int = 30):
        """
        Clear logs older than specified days

        Args:
            days: Number of days to keep
        """
        try:
            if not os.path.exists(self.log_file):
                return

            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            kept_logs = []

            async with aiofiles.open(self.log_file, mode='r') as f:
                content = await f.read()
                lines = content.strip().split('\n')

                for line in lines:
                    if line.strip():
                        try:
                            log_dict = json.loads(line)
                            log_date = datetime.fromisoformat(log_dict['timestamp'].replace('Z', '+00:00'))
                            if log_date.timestamp() >= cutoff_date:
                                kept_logs.append(line)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue

            # Write back kept logs
            async with aiofiles.open(self.log_file, mode='w') as f:
                await f.write('\n'.join(kept_logs) + '\n')

            logger.info(f"Cleared logs older than {days} days")

        except Exception as e:
            logger.error(f"Error clearing old logs: {str(e)}")


# Global instance
activity_logger = ActivityLogger()

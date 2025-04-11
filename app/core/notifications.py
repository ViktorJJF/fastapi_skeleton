import asyncio
import traceback
from typing import Optional, Any
from loguru import logger

# Removed direct import to avoid circular dependency
# Will import telegram_service at function call time
from app.core.config import settings


class TelegramNotifier:
    """
    Class to handle sending notifications via Telegram.
    Uses the telegram_service for actual message delivery.
    """
    def __init__(self):
        self.enabled = settings.TELEGRAM_NOTIFICATIONS_ENABLED
        
        # Log initialization
        if self.enabled:
            logger.info("TelegramNotifier initialized and enabled")
        else:
            logger.info("TelegramNotifier initialized but disabled")
    
    def _format_error_message(self, error: Any, traceback_info: Optional[str] = None) -> str:
        """
        Format error message for Telegram notification.
        """
        # Use context to track error type
        with logger.contextualize(error_type=type(error).__name__):
            logger.debug(f"Formatting error message: {error}")
            
            message = f"🚨 ERROR: {error}"
            
            if traceback_info:
                # Limit traceback length to avoid hitting Telegram message size limits
                original_length = len(traceback_info)
                if original_length > 3000:
                    traceback_info = traceback_info[:3000] + "...[truncated]"
                    logger.debug(f"Traceback truncated from {original_length} to 3000 chars")
                    
                message += f"\n\n🔍 Traceback:\n```\n{traceback_info}\n```"
            
            return message
    
    def send_notification(self, message: str) -> None:
        """
        Send a notification message asynchronously.
        This method creates a task and doesn't block the execution.
        """
        if not self.enabled:
            logger.debug("Telegram notifications are disabled")
            return
        
        # Import telegram_service at runtime to avoid circular imports
        from app.services.telegram_service import telegram_service
        
        with logger.contextualize(notification_type="general", message_length=len(message)):
            logger.debug(f"Sending notification: {message[:50]}...")
            telegram_service.send_async_message(message, parse_mode="Markdown")
    
    def send_error_notification(self, error: Any, traceback_info: Optional[str] = None) -> None:
        """
        Send an error notification asynchronously.
        If traceback_info is not provided, it will attempt to capture the current traceback.
        """
        if not self.enabled:
            logger.debug("Telegram notifications are disabled")
            return
        
        # Import telegram_service at runtime to avoid circular imports
        from app.services.telegram_service import telegram_service
            
        # Capture traceback if not provided
        if traceback_info is None:
            traceback_info = "".join(traceback.format_exc())
            logger.debug("Auto-captured traceback for error notification")
        
        # Track the error context
        with logger.contextualize(
            notification_type="error",
            error_type=type(error).__name__
        ):
            logger.debug(f"Sending error notification: {error}")
            formatted_message = self._format_error_message(error, traceback_info)
            telegram_service.send_async_message(formatted_message, parse_mode="Markdown")


# Create a singleton instance
telegram_notifier = TelegramNotifier() 
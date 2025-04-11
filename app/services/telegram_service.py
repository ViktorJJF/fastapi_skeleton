import os
import asyncio
from typing import Optional
from loguru import logger

from telegram import Bot
from telegram.error import TelegramError
from app.core.config import config


class TelegramService:
    """
    Service for sending messages through Telegram using python-telegram-bot.
    Basic message delivery service - error formatting handled by notifications.py.
    """
    def __init__(self):
        self.token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.enabled = config.TELEGRAM_NOTIFICATIONS_ENABLED
        self._bot = None
        
        # Log initialization
        if self.enabled:
            logger.info("TelegramService initialized")
            if not self.token:
                logger.warning("Telegram bot token not configured")
            if not self.chat_id:
                logger.warning("Telegram chat ID not configured")
        else:
            logger.info("TelegramService disabled")

    @property
    def bot(self) -> Optional[Bot]:
        """
        Lazy initialization of Telegram Bot instance.
        """
        if self._bot is None and self.token:
            self._bot = Bot(token=self.token)
            logger.debug("Telegram Bot instance created")
        return self._bot
    
    async def _send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Internal method to send a message to the configured Telegram chat.
        
        Args:
            message: The message to send
            parse_mode: The parse mode for Telegram (HTML, Markdown, MarkdownV2)
            
        Returns:
            bool: Whether the message was sent successfully
        """
        # Use contextual logging to track message details
        with logger.contextualize(
            telegram_chat_id=self.chat_id,
            parse_mode=parse_mode,
            message_length=len(message) if message else 0
        ):
            if not self.enabled:
                logger.debug("Telegram notifications are disabled")
                return False
                
            if not self.bot or not self.chat_id:
                logger.warning("Telegram token or chat ID not configured")
                return False
                
            try:
                logger.debug(f"Sending Telegram message (length: {len(message)} chars)")
                
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=message,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True
                )
                
                logger.debug("Message sent to Telegram successfully")
                return True
            except TelegramError as e:
                logger.error(f"Failed to send message to Telegram: {e}")
                return False
            except Exception as e:
                logger.exception(f"Unexpected error sending message to Telegram: {e}")
                return False
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> None:
        """
        Send a message to the configured Telegram chat.
        This method runs synchronously.
        
        Args:
            message: The message to send
            parse_mode: The parse mode for Telegram (HTML, Markdown, MarkdownV2)
        """
        if not self.enabled:
            logger.debug("Telegram notifications are disabled")
            return
            
        self._send_message(message, parse_mode)
        
    def send_async_message(self, message: str, parse_mode: str = "HTML") -> None:
        """
        Send a message to the configured Telegram chat asynchronously.
        This method creates a task and doesn't block the execution.
        
        Args:
            message: The message to send
            parse_mode: The parse mode for Telegram (HTML, Markdown, MarkdownV2)
        """
        if not self.enabled:
            logger.debug("Telegram notifications are disabled")
            return
            
        task = asyncio.create_task(self._send_message(message, parse_mode))
        task.add_done_callback(lambda t: logger.debug(
            "Async Telegram notification completed" if not t.exception() else 
            f"Async Telegram notification failed: {t.exception()}"
        ))


# Create singleton instance
telegram_service = TelegramService() 
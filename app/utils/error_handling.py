from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union
import os
import sys
import logging
import traceback
import asyncio
from loguru import logger

from app.core.notifications import telegram_notifier


def build_error_object(code: int, message: Union[str, Dict]) -> HTTPException:
    """
    Build an HTTPException with the given code and message.
    
    Args:
        code: HTTP status code for the error
        message: Error message or object with error details
        
    Returns:
        HTTPException: Exception object with status code and detail
    """
    return HTTPException(status_code=code, detail=message)


def item_not_found(error: Optional[Exception], item: Any, message: str = "Item not found") -> None:
    """
    Throw an error if item is not found.
    """
    if error:
        raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(error))
    
    if not item:
        raise build_error_object(status.HTTP_404_NOT_FOUND, message)


def item_already_exists(error: Optional[Exception], item: Any, message: str = "Item already exists") -> None:
    """
    Throw an error if item already exists.
    """
    if error:
        raise build_error_object(status.HTTP_500_INTERNAL_SERVER_ERROR, str(error))
    
    if item:
        raise build_error_object(status.HTTP_409_CONFLICT, message)


def handle_error(response_or_error: Any, error: Any = None) -> JSONResponse:
    """
    Handle error and return appropriate response.
    Logs error in development environments and builds and sends an error response.
    
    Args:
        response_or_error: Either a Response object (for backward compatibility) or the error itself
        error: Error object to be handled (optional, for backward compatibility)
    
    Returns:
        JSONResponse: A formatted JSON response with error details
    """
    # Handle both new and old calling conventions
    if error is None:
        # New style: handle_error(error)
        actual_error = response_or_error
    else:
        # Old style: handle_error(response, error)
        actual_error = error
    
    # Log the error message and the full traceback for detailed debugging
    error_message = f"Error: {str(actual_error)}"
    traceback_info = traceback.format_exc()
    
    # Use loguru instead of standard logging
    logger.opt(exception=True).error(f"{error_message}")
    
    # Send notification to Telegram asynchronously in background
    # This won't block response generation
    telegram_notifier.send_error_notification(str(actual_error), traceback_info)
    
    # Format the error response
    if isinstance(actual_error, HTTPException):
        return JSONResponse(
            status_code=actual_error.status_code,
            content={
                "ok": False, 
                "errors": {
                    "msg": actual_error.detail
                }
            }
        )
    
    # Default to 500 error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False, 
            "errors": {
                "msg": str(actual_error)
            }
        }
    )


def is_id_valid(id: Any) -> int:
    """
    Check if ID is valid.
    """
    try:
        id_int = int(id)
        return id_int
    except (ValueError, TypeError):
        raise build_error_object(status.HTTP_400_BAD_REQUEST, "Invalid ID format")


# Global exception handler for uncaught exceptions
def setup_global_exception_handler():
    """
    Set up a global exception handler for uncaught exceptions.
    This will log the exception and notify via Telegram.
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        # Don't catch KeyboardInterrupt or SystemExit
        if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Format the exception
        error_message = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
        traceback_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Log the exception using loguru
        logger.opt(exception=True).critical(error_message)
        
        # Send Telegram notification without blocking
        telegram_notifier.send_error_notification(str(exc_value), traceback_text)

    # Set the exception hook
    sys.excepthook = handle_exception 
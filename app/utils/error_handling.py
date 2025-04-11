from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union
import os
import sys
import logging
import traceback
import asyncio

from app.services.telegram_service import telegram_service


logger = logging.getLogger(__name__)


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


async def handle_error(response: JSONResponse, error: Any) -> JSONResponse:
    """
    Handle error and return appropriate response.
    Logs error in development environments and builds and sends an error response.
    
    Args:
        response: JSONResponse class to create the response
        error: Error object to be handled
    
    Returns:
        JSONResponse: A formatted JSON response with error details
    """
    # Log the error message and the full traceback for detailed debugging
    error_message = f"Error: {str(error)}"
    traceback_info = traceback.format_exc()
    
    logger.error(f"{error_message}\nTraceback:\n{traceback_info}")
    
    # Send notification to Telegram
    asyncio.create_task(
        telegram_service.send_error_notification(str(error), traceback_info)
    )
    
    # Format the error response
    if isinstance(error, HTTPException):
        return JSONResponse(
            status_code=error.status_code,
            content={
                "ok": False, 
                "errors": {
                    "msg": error.detail
                }
            }
        )
    
    # Default to 500 error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "ok": False, 
            "errors": {
                "msg": str(error)
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
        
        # Log the exception
        logger.critical(f"{error_message}\n{traceback_text}")
        
        # Send Telegram notification (need to create a new event loop for async)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                telegram_service.send_error_notification(str(exc_value), traceback_text)
            )
            loop.close()
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

    # Set the exception hook
    sys.excepthook = handle_exception 
from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union
import os
import sys
import logging
import traceback
import asyncio
from loguru import logger
import json

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


def safe_serialize(obj):
    """Converts bytes to string representation for JSON serialization."""
    if isinstance(obj, bytes):
        try:
            return obj.decode('utf-8', errors='replace') # Try decoding
        except Exception:
            return repr(obj) # Fallback to repr if decoding fails
    elif isinstance(obj, list):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_serialize(value) for key, value in obj.items()}
    # Add handling for other non-serializable types if needed
    return obj


async def handle_error(arg1: Any, error: Optional[Exception] = None) -> JSONResponse:
    """
    Handle error and return appropriate response.
    Logs error, sends notification, and builds the JSON response.
    
    Args:
        arg1: Either the error itself (if error=None) or the Request object.
        error: The actual exception (if arg1 is the Request object).
    
    Returns:
        JSONResponse: A formatted JSON response with error details.
    """
    actual_error: Exception
    request: Optional[Request] = None

    if error is None:
        # Calling convention: handle_error(actual_error)
        if isinstance(arg1, Exception):
            actual_error = arg1
        else:
            # Fallback if called incorrectly, treat arg1 as the error message
            actual_error = Exception(str(arg1))
            logger.warning(f"handle_error called with one argument, but it wasn't an Exception: {arg1}")
    else:
        # Calling convention: handle_error(request, actual_error)
        actual_error = error
        if isinstance(arg1, Request):
            request = arg1
        else:
            logger.warning("handle_error called with two arguments, but the first was not a FastAPI Request object.")
            # Attempt to proceed without request details

    # Log the error message and the full traceback for detailed debugging
    error_message = f"Error: {type(actual_error).__name__}: {str(actual_error)}"
    traceback_info = traceback.format_exc()
    
    # Use loguru for logging
    logger.opt(exception=actual_error).error(f"Handling error: {error_message}")
    
    # Prepare details for notification
    notification_error_message = str(actual_error)
    notification_traceback = traceback_info

    # Extract HTTP-specific information if it's an HTTPException and we have a request
    http_info = ""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR # Default

    if isinstance(actual_error, HTTPException):
        status_code = actual_error.status_code # Use HTTPException's status code
        if request:
            headers = {}
            endpoint = "Unknown"
            body = "Unavailable"
            method = "Unknown"
            
            # Extract information from request
            if hasattr(request, 'headers'):
                # Sanitize headers
                headers = {k: ('******' if k.lower() in ['authorization', 'api-key', 'x-api-key', 'secret'] else v) 
                           for k, v in request.headers.items()}
            
            if hasattr(request, 'url') and request.url:
                endpoint = str(request.url)
            
            if hasattr(request, 'method'):
                method = request.method
            
            # Safely try to read request body asynchronously
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8', errors='replace')
                else:
                    body = "(Empty body)"
            except Exception as body_exc:
                logger.warning(f"Could not read request body asynchronously: {body_exc}")
                body = f"(Error reading body: {body_exc})"

            http_info = (
                f"HTTP Details:\n"
                f"Method: {method}\n"
                f"Endpoint: {endpoint}\n"
                f"Status Code: {status_code}\n"
                f"Headers: {headers}\n"
                f"Body: {body}\n\n"
            )
            notification_traceback = http_info + traceback_info
        else:
             # HTTPException but no request object available
             http_info = f"HTTP Status Code: {status_code}\n(No request details available)\n\n"
             notification_traceback = http_info + traceback_info

    elif isinstance(actual_error, RequestValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        validation_errors = actual_error.errors()
        
        # Preprocess errors to handle non-serializable types like bytes
        safe_validation_errors = safe_serialize(validation_errors)

        # Format validation errors for the notification using the safe version
        try:
            error_details_str = json.dumps(safe_validation_errors, indent=2)
        except Exception as json_exc:
            logger.error(f"Could not serialize validation errors to JSON: {json_exc}")
            error_details_str = repr(safe_validation_errors) # Fallback to repr

        http_info = (
            f"Validation Error Details:\n{error_details_str}\n\n"
        )
        # Prepend HTTP info if request is available
        if request:
            headers = {}
            endpoint = "Unknown"
            body = "Unavailable"
            method = "Unknown"
            
            # Extract information from request
            if hasattr(request, 'headers'):
                # Sanitize headers
                headers = {k: ('******' if k.lower() in ['authorization', 'api-key', 'x-api-key', 'secret'] else v) 
                           for k, v in request.headers.items()}
            
            if hasattr(request, 'url') and request.url:
                endpoint = str(request.url)
            
            if hasattr(request, 'method'):
                method = request.method
            
            # Safely try to read request body asynchronously
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = body_bytes.decode('utf-8', errors='replace')
                else:
                    body = "(Empty body)"
            except Exception as body_exc:
                logger.warning(f"Could not read request body asynchronously: {body_exc}")
                body = f"(Error reading body: {body_exc})"

            http_info = (
                f"HTTP Details:\n"
                f"Method: {method}\n"
                f"Endpoint: {endpoint}\n"
                f"Status Code: {status_code}\n"
                f"Headers: {headers}\n"
                f"Body: {body}\n\n"
                f"\nValidation Error Details:\n{error_details_str}\n\n"
            )
            notification_traceback = http_info + traceback_info
        notification_error_message = "Request Validation Error"

    # Send notification
    try:
        telegram_notifier.send_error_notification(notification_error_message, notification_traceback)
    except Exception as send_error:
        logger.error(f"Failed to send Telegram notification: {send_error}")

    # Format the JSON response
    response_content = {
        "ok": False, 
        "errors": {
            "msg": str(actual_error.detail) if isinstance(actual_error, HTTPException) else 
                   (safe_serialize(actual_error.errors()) if isinstance(actual_error, RequestValidationError) else str(actual_error))
        }
    }
    
    return JSONResponse(
        status_code=status_code,
        content=response_content
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
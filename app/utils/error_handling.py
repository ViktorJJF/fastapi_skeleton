from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union
import os
import logging

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


def handle_error(response: JSONResponse, error: Any) -> JSONResponse:
    """
    Handle error and return appropriate response.
    Logs error in development environments and builds and sends an error response.
    
    Args:
        response: JSONResponse class to create the response
        error: Error object to be handled
    
    Returns:
        JSONResponse: A formatted JSON response with error details
    """
    # Print error in console for development environments
    env = os.getenv("ENV", "production")
    if env in ["local", "development"]:
        if isinstance(error, HTTPException):
            logger.error(f"Error {error.status_code}: {error.detail}")
        else:
            logger.error(f"Error: {str(error)}")
    
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
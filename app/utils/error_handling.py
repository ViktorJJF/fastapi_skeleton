from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional


def build_error_object(code: int, message: str) -> HTTPException:
    """
    Build an HTTPException with the given code and message.
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
    """
    if isinstance(error, HTTPException):
        return JSONResponse(
            status_code=error.status_code,
            content={"ok": False, "error": error.detail}
        )
    
    # Default to 500 error
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"ok": False, "error": str(error)}
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
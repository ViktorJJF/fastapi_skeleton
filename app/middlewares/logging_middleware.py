import time
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger
from typing import Optional
import uuid

from app.utils.error_handling import handle_error
from app.core.notifications import telegram_notifier


async def logging_middleware(request: Request, call_next):
    """
    Middleware for logging request information and handling exceptions.
    Provides consistent error handling and logging across the application.
    """
    # Generate a unique request ID for tracing
    request_id = str(uuid.uuid4())
    
    # Start timing the request
    start_time = time.time()
    
    # Get IP address
    client_host = request.client.host if request.client else "unknown"
    
    # Set up logging context
    with logger.contextualize(
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=client_host
    ):
        # Log incoming request details
        logger.info(
            f"Request: {request.method} {request.url.path} from {client_host}"
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log successful response
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Time: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as exc:
            # Calculate processing time for failed request
            process_time = time.time() - start_time
            
            # Log exception with traceback
            logger.opt(exception=True).error(
                f"Error processing request: {request.method} {request.url.path} - "
                f"Time: {process_time:.4f}s - Error: {str(exc)}"
            )
            
            # Send notification for server errors
            if not isinstance(exc, JSONResponse):
                # Capture traceback for notification
                tb = traceback.format_exc()
                telegram_notifier.send_error_notification(str(exc), tb)
            
            # Return a proper error response (use only the error parameter)
            # Note: We don't have the request object readily available here 
            # in the way handle_error expects for detailed reporting. 
            # It will log the error and traceback, but HTTP details might be limited.
            return await handle_error(exc) 
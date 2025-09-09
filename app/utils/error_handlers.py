import traceback
import inspect
import functools
from loguru import logger

from app.core.notifications import telegram_notifier


def handle_errors(func):
    """
    Decorator to handle errors and send notifications for async functions.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Get function details for better logging
        func_name = func.__name__
        func_module = func.__module__

        # Create a context for all logs in this function
        with logger.contextualize(
            function=func_name, module=func_module, is_async=True
        ):
            try:
                logger.debug(f"Executing async function {func_module}.{func_name}")
                return await func(*args, **kwargs)
            except Exception as e:
                # Get traceback info
                tb_info = traceback.format_exc()

                # Get caller information for better context
                frame = inspect.currentframe().f_back
                caller_info = ""
                if frame:
                    caller_file = frame.f_code.co_filename
                    caller_line = frame.f_lineno
                    caller_func = frame.f_code.co_name
                    caller_info = (
                        f" called from {caller_file}:{caller_line} in {caller_func}()"
                    )

                # Log the error with enhanced context
                logger.opt(exception=True).error(
                    f"Error in {func_module}.{func_name}{caller_info}: {str(e)}"
                )

                # Send error notification via Telegram asynchronously
                telegram_notifier.send_error_notification(str(e), tb_info)

                # Re-raise the exception
                raise

    return wrapper


def sync_handle_errors(func):
    """
    Decorator to handle errors and send notifications for sync functions.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get function details for better logging
        func_name = func.__name__
        func_module = func.__module__

        # Create a context for all logs in this function
        with logger.contextualize(
            function=func_name, module=func_module, is_async=False
        ):
            try:
                logger.debug(f"Executing sync function {func_module}.{func_name}")
                return func(*args, **kwargs)
            except Exception as e:
                # Get traceback info
                tb_info = traceback.format_exc()

                # Get caller information for better context
                frame = inspect.currentframe().f_back
                caller_info = ""
                if frame:
                    caller_file = frame.f_code.co_filename
                    caller_line = frame.f_lineno
                    caller_func = frame.f_code.co_name
                    caller_info = (
                        f" called from {caller_file}:{caller_line} in {caller_func}()"
                    )

                # Log the error with enhanced context
                logger.opt(exception=True).error(
                    f"Error in {func_module}.{func_name}{caller_info}: {str(e)}"
                )

                # Send error notification via Telegram asynchronously
                telegram_notifier.send_error_notification(str(e), tb_info)

                # Re-raise the exception
                raise

    return wrapper


# Example usage:
#
# @handle_errors
# async def some_async_function():
#     # Your code here
#     pass
#
# @sync_handle_errors
# def some_sync_function():
#     # Your code here
#     pass

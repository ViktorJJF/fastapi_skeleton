# Logging in Albedo API

This document explains how logging is configured in the Albedo API application and provides examples of how to use it.

## Overview

The Albedo API uses [Loguru](https://github.com/Delgan/loguru) for logging, which provides a simple yet powerful logging interface. The logging system is configured in `app/core/logger.py` and automatically sets up multiple log outputs:

1. **Console output** - For development and debugging
2. **File-based logging** - For production environments
3. **External services integration** - For centralized logging and monitoring (Google Cloud Logging and Azure Monitor)

## Log Levels

The following log levels are used in the application:

- `TRACE` - Detailed information, typically only used when diagnosing issues
- `DEBUG` - Information useful for debugging
- `INFO` - General information about system operation
- `SUCCESS` - Successful operations
- `WARNING` - Indicates potential issues that don't prevent the application from working
- `ERROR` - Error conditions that should be investigated
- `CRITICAL` - Critical conditions that require immediate attention

## File-Based Logging

Logs are written to several files in the `logs/` directory:

- `app.log` - Contains all logs at the configured level (INFO or DEBUG)
- `error.log` - Contains only ERROR and higher level logs
- `json.log` - Contains logs in JSON format for machine processing

These log files are automatically rotated (when they reach a certain size) and have retention policies (logs older than a specified time are deleted).

## External Services Integration

### Google Cloud Logging

To enable Google Cloud Logging:

1. Uncomment the `google-cloud-logging>=3.6.0` line in `requirements.txt` and install it.
2. Set the following environment variables:
   - `GOOGLE_CLOUD_LOGGING_ENABLED=true`
   - `GOOGLE_CLOUD_PROJECT_ID=your-project-id` (optional if running on GCP)
   - `GOOGLE_CLOUD_LOG_NAME=your-log-name` (optional, defaults to "albedo_api")

### Azure Monitor

To enable Azure Monitor (Application Insights):

1. Uncomment the `opencensus-ext-azure>=1.1.9` and `opencensus>=0.11.0` lines in `requirements.txt` and install them.
2. Set the following environment variables:
   - `AZURE_MONITOR_ENABLED=true`
   - `AZURE_APPINSIGHTS_CONNECTION_STRING=your-connection-string`

## How to Use Logging in Your Code

### Basic Usage

```python
from loguru import logger

# Simple logging
logger.info("Processing item")
logger.warning("Resource is running low")
logger.error("Failed to process item")

# Logging with structured data
logger.info(f"User {user_id} logged in from {ip_address}")

# Logging exceptions
try:
    # Some code that might raise an exception
    result = perform_operation()
except Exception as e:
    logger.exception(f"Operation failed: {e}")
    # The exception traceback is automatically included
```

### Logging with Context

You can add context to your logs to help with filtering and analysis:

```python
# Adding context to all subsequent logs in this scope
with logger.contextualize(user_id=user.id, request_id=request.id):
    logger.info("Processing user request")
    # ... more code and logs
    logger.info("Request processed")
    # All these logs will include user_id and request_id
```

### Logging Function Calls

You can use the provided error handlers to automatically log exceptions from your functions:

```python
from app.utils.error_handlers import handle_errors, sync_handle_errors

@handle_errors
async def async_operation():
    # This function's exceptions will be logged and sent via Telegram
    # ...

@sync_handle_errors
def sync_operation():
    # This function's exceptions will be logged and sent via Telegram
    # ...
```

## Configuration

Logging configuration can be adjusted through environment variables:

- `LOG_LEVEL` - The minimum log level to record (default: "INFO")
- `LOG_FILE_PATH` - Where to store log files (default: "logs/app.log")
- `PYTHON_ENV` - Environment name (development, staging, production)

## Best Practices

1. **Use appropriate log levels** - Don't log everything as INFO or ERROR
2. **Include relevant context** - Add IDs and important values to help with debugging
3. **Structure your messages** - Make them clear and consistent
4. **Don't log sensitive data** - Never log passwords, tokens, or personal information
5. **Use JSON logging for machine processing** - When integrating with log analysis tools

## Telegram Notifications

Critical errors can be sent as Telegram notifications. This is configured in `app/core/notifications.py` and uses the settings from `app/core/config.py`.

To enable Telegram notifications:

1. Create a Telegram bot using BotFather and get the token
2. Find your chat ID
3. Set the following environment variables:
   - `TELEGRAM_BOT_TOKEN=your-bot-token`
   - `TELEGRAM_CHAT_ID=your-chat-id`
   - `TELEGRAM_NOTIFICATIONS_ENABLED=true`

See the `app/examples/telegram_notifications_example.py` file for examples of how to use Telegram notifications. 
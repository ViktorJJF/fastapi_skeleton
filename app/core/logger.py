import sys
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union
import socket
from loguru import logger
import atexit

from app.core.config import config


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    See https://loguru.readthedocs.io/en/stable/overview.html
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class GoogleCloudLoggingSink:
    """
    Custom sink for Google Cloud Logging.
    Requires google-cloud-logging package to be installed.
    """
    def __init__(self, log_name: str = "albedo_api", project_id: Optional[str] = None):
        """
        Initialize Google Cloud Logging client.
        
        Args:
            log_name: Name of the log in Google Cloud
            project_id: Google Cloud project ID (if None, will be autodetected)
        """
        try:
            from google.cloud import logging as google_logging
            self.client = google_logging.Client(project=project_id)
            self.logger = self.client.logger(log_name)
            self.enabled = True
        except ImportError:
            logger.warning("google-cloud-logging not installed, Google Cloud Logging disabled")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Failed to initialize Google Cloud Logging: {e}")
            self.enabled = False
            
    def __call__(self, message):
        """
        Write a log entry to Google Cloud Logging.
        """
        if not self.enabled:
            return
            
        record = message.record
        try:
            # Convert to dict format expected by Google Cloud Logging
            severity = record["level"].name
            payload = {
                "message": record["message"],
                "timestamp": record["time"].isoformat(),
                "severity": severity,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "file": record["file"].name,
                "environment": os.getenv("PYTHON_ENV", "development"),
                "service": config.PROJECT_NAME,
                "host": socket.gethostname()
            }
            
            # Add exception info if present
            if record["exception"] is not None:
                payload["exception"] = str(record["exception"])
                
            # Write to Google Cloud Logging
            self.logger.log_struct(payload, severity=severity)
        except Exception as e:
            # Avoid recursion by not using logger here
            print(f"Error sending to Google Cloud Logging: {e}", file=sys.stderr)


class AzureMonitorSink:
    """
    Custom sink for Azure Application Insights.
    Requires opencensus-ext-azure package to be installed.
    """
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize Azure Application Insights client.
        
        Args:
            connection_string: Azure Application Insights connection string
        """
        self.connection_string = connection_string or config.AZURE_APPINSIGHTS_CONNECTION_STRING
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            self.handler = AzureLogHandler(connection_string=self.connection_string)
            self.enabled = True
        except ImportError:
            logger.warning("opencensus-ext-azure not installed, Azure Monitor logging disabled")
            self.enabled = False
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Monitor logging: {e}")
            self.enabled = False
    
    def __call__(self, message):
        """
        Write a log entry to Azure Application Insights.
        """
        if not self.enabled:
            return
            
        record = message.record
        try:
            # Create a Python standard logging record
            log_record = logging.LogRecord(
                name=record["name"],
                level=getattr(logging, record["level"].name),
                pathname=str(record["file"]),
                lineno=record["line"],
                msg=record["message"],
                args=(),
                exc_info=record["exception"],
            )
            
            # Add custom properties
            log_record.custom_dimensions = {
                "environment": os.getenv("PYTHON_ENV", "development"),
                "service": config.PROJECT_NAME,
                "host": socket.gethostname(),
                "function": record["function"]
            }
            
            # Emit to Azure
            self.handler.emit(log_record)
        except Exception as e:
            # Avoid recursion by not using logger here
            print(f"Error sending to Azure Monitor: {e}", file=sys.stderr)


def setup_logging():
    """
    Configure logging with loguru.
    """
    # Remove default handlers
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.INFO)

    # Remove every other logger's handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Configure loguru
    log_level = "DEBUG" if config.DEBUG else "INFO"
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Define handlers
    handlers = [
        # Console handler
        {
            "sink": sys.stdout,
            "level": log_level,
            "colorize": True,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        },
        # Main log file - includes all logs
        {
            "sink": logs_dir / "app.log",
            "rotation": "20 MB",
            "retention": "1 week",
            "compression": "zip",
            "level": log_level,
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,
        },
        # Error log file - only ERROR and higher
        {
            "sink": logs_dir / "error.log",
            "rotation": "10 MB",
            "retention": "1 month",
            "compression": "zip",
            "level": "ERROR",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            "backtrace": True,
            "diagnose": True,
            "enqueue": True,
        },
        # JSON log file for machine processing
        {
            "sink": logs_dir / "json.log",
            "rotation": "20 MB",
            "retention": "1 week",
            "compression": "zip",
            "format": lambda record: json.dumps({
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "message": record["message"],
                "name": record["name"],
                "function": record["function"],
                "line": record["line"],
                "file": record["file"].name,
                "thread_id": record["thread"].id,
                "process_id": record["process"].id,
                "exception": str(record["exception"]) if record["exception"] else None,
                "environment": os.getenv("PYTHON_ENV", "development"),
                "service": config.PROJECT_NAME,
                "host": socket.gethostname()
            }) + "\n",
            "level": log_level,
            "enqueue": True,
        }
    ]
    
    # Add Google Cloud Logging if configured
    if getattr(config, "GOOGLE_CLOUD_LOGGING_ENABLED", False):
        handlers.append({
            "sink": GoogleCloudLoggingSink(
                log_name=getattr(config, "GOOGLE_CLOUD_LOG_NAME", "albedo_api"),
                project_id=getattr(config, "GOOGLE_CLOUD_PROJECT_ID", None)
            ),
            "level": "INFO",
            "format": "{message}",  # The sink handles formatting
            "serialize": False,
        })
    
    # Add Azure Monitor if configured
    if getattr(config, "AZURE_MONITOR_ENABLED", False):
        handlers.append({
            "sink": AzureMonitorSink(
                connection_string=getattr(config, "AZURE_APPINSIGHTS_CONNECTION_STRING", None)
            ),
            "level": "INFO",
            "format": "{message}",  # The sink handles formatting
            "serialize": False,
        })
    
    # Configure loguru with all handlers
    logger.configure(handlers=handlers)
    
    # Log startup information
    logger.info(f"Logging initialized: level={log_level}, logs_dir={logs_dir.absolute()}")
    logger.info(f"Environment: {os.getenv('PYTHON_ENV', 'development')}")
    logger.info(f"Service: {config.PROJECT_NAME}")
    
    # Register atexit handler to flush logs
    def _flush_logs():
        logger.info("Application shutting down, flushing logs")
    
    atexit.register(_flush_logs)


# Setup logging when module is imported
setup_logging() 
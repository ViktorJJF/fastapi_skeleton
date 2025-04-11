import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.backend_pre_start import init, main


class TestBackendPreStart:
    """Tests for the backend_pre_start module."""

    def test_init_success(self):
        """Test that init function works correctly when DB is available."""
        # Mock AsyncSession and engine
        with patch("app.backend_pre_start.asyncio.run") as mock_run, \
             patch("app.backend_pre_start.engine") as mock_engine, \
             patch("app.backend_pre_start.init") as mock_init:
            
            # Call main
            main()
            
            # Verify mock_init was called with mock_engine
            mock_init.assert_called_once_with(mock_engine)
            
            # Verify asyncio.run was called once
            mock_run.assert_called_once()

    def test_init_failure(self):
        """Test that init function raises exception when DB is not available."""
        # Mock AsyncSession
        with patch("app.backend_pre_start.asyncio.run") as mock_run, \
             patch("app.backend_pre_start.init") as mock_init, \
             patch("app.backend_pre_start.engine") as mock_engine:
            
            # Make asyncio.run raise the exception
            mock_run.side_effect = SQLAlchemyError("Database not available")
            
            # Call main which should call asyncio.run(init())
            with pytest.raises(SQLAlchemyError):
                main()
            
            # Verify asyncio.run was called with init
            mock_run.assert_called_once()

    def test_main(self):
        """Test that main function initializes service correctly."""
        # Mock dependencies
        with patch("app.backend_pre_start.asyncio.run") as mock_run, \
             patch("app.backend_pre_start.init") as mock_init, \
             patch("app.backend_pre_start.engine") as mock_engine, \
             patch("app.backend_pre_start.logger") as mock_logger:
            
            # Call main
            main()
            
            # Verify logger was called correctly
            assert mock_logger.info.call_count == 2
            mock_logger.info.assert_has_calls([
                call("Initializing service"),
                call("Service finished initializing")
            ])
            
            # Verify init was called with engine
            mock_init.assert_called_once_with(mock_engine)
            
            # Verify asyncio.run was called once
            mock_run.assert_called_once()

    def test_init_retry_logic(self):
        """Test that init function has correct retry logic."""
        # Set up mock retry decorator
        with patch("tenacity.retry") as mock_retry:
            mock_retry.return_value = lambda f: f
            
            # Force reimport to trigger decorator
            import importlib
            import app.backend_pre_start
            importlib.reload(app.backend_pre_start)
            
            # Verify retry was called with correct arguments
            mock_retry.assert_called_once()
            args, kwargs = mock_retry.call_args
            
            # Check that stop, wait, before, and after are provided
            assert "stop" in kwargs
            assert "wait" in kwargs
            assert "before" in kwargs
            assert "after" in kwargs
            
            # Restore original module (cleanup)
            importlib.reload(app.backend_pre_start) 
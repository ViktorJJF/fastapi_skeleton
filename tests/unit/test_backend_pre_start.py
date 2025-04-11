import pytest
from unittest.mock import patch, MagicMock, call
import logging
from sqlalchemy.exc import SQLAlchemyError

from app.backend_pre_start import init, main


class TestBackendPreStart:
    """Tests for the backend_pre_start module."""

    @pytest.mark.asyncio
    @patch("app.backend_pre_start.AsyncSession")
    async def test_init_success(self, mock_session):
        """Test that init function works correctly when DB is available."""
        # Set up mock session
        mock_session_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Mock engine
        mock_engine = MagicMock()
        
        # Call init
        init(mock_engine)
        
        # Verify session was created with engine
        mock_session.assert_called_once_with(mock_engine)
        # Verify select query was executed
        mock_session_instance.execute.assert_called_once()
        mock_session_instance.commit.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.backend_pre_start.AsyncSession")
    async def test_init_failure(self, mock_session):
        """Test that init function raises exception when DB is not available."""
        # Set up mock session to raise exception
        mock_session_instance = MagicMock()
        mock_session_instance.execute.side_effect = SQLAlchemyError("Database not available")
        mock_session.return_value.__enter__.return_value = mock_session_instance
        
        # Mock engine
        mock_engine = MagicMock()
        
        # Call init and expect exception
        with pytest.raises(SQLAlchemyError):
            init(mock_engine)
        
        # Verify session was created with engine
        mock_session.assert_called_once_with(mock_engine)
        # Verify select query was executed
        mock_session_instance.execute.assert_called_once()
        # Commit should not be called if execute fails
        mock_session_instance.commit.assert_not_called()

    @pytest.mark.asyncio
    @patch("app.backend_pre_start.init")
    @patch("app.backend_pre_start.engine")
    @patch("app.backend_pre_start.logger")
    async def test_main(self, mock_logger, mock_engine, mock_init):
        """Test that main function initializes service correctly."""
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

    @pytest.mark.asyncio
    @patch("app.backend_pre_start.retry")
    async def test_init_retry_logic(self, mock_retry):
        """Test that init function has correct retry logic."""
        # Set up mock retry decorator
        mock_retry.return_value = lambda f: f
        
        # Import init again to trigger decorator
        from app.backend_pre_start import init
        
        # Verify retry was called with correct arguments
        mock_retry.assert_called_once()
        args, kwargs = mock_retry.call_args
        
        # Check that stop, wait, before, and after are provided
        assert "stop" in kwargs
        assert "wait" in kwargs
        assert "before" in kwargs
        assert "after" in kwargs 
import pytest
import subprocess
import sys
import os
import time
import logging
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.mark.e2e
def test_backend_pre_start_script_execution():
    """
    End-to-end test that runs the backend_pre_start script as a subprocess.
    
    This test verifies that the script can be executed successfully in a real
    environment. It requires that the database is actually running and configured
    correctly in the environment.
    
    Note: This test should be run in an environment that has access to the
    database specified in the configuration.
    """
    # Get the path to the backend_pre_start.py script
    script_path = Path(__file__).parent.parent.parent / "app" / "backend_pre_start.py"
    
    # Check that the script exists
    assert script_path.exists(), f"Script not found at {script_path}"
    
    # Log the test execution
    logger.info(f"Running backend_pre_start.py script from {script_path}")
    
    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
            timeout=30,   # Timeout after 30 seconds
        )
        
        # Log the output
        logger.info(f"Script stdout: {result.stdout}")
        if result.stderr:
            logger.warning(f"Script stderr: {result.stderr}")
        
        # Check that the script executed successfully
        assert result.returncode == 0, f"Script failed with return code {result.returncode}"
        
        # Check for expected output messages
        assert "Initializing service" in result.stdout
        assert "Service finished initializing" in result.stdout
        
    except subprocess.TimeoutExpired:
        pytest.fail("Script execution timed out")
    except Exception as e:
        pytest.fail(f"Error running script: {e}")


@pytest.mark.e2e
def test_backend_pre_start_retry_behavior():
    """
    End-to-end test that verifies the retry behavior of the backend_pre_start script.
    
    This test temporarily sets an invalid database URL to force the script to retry,
    then restores the original URL. It verifies that the retry mechanism works as expected.
    
    Note: This test modifies environment variables, so it should be run in isolation.
    """
    # Get the path to the backend_pre_start.py script
    script_path = Path(__file__).parent.parent.parent / "app" / "backend_pre_start.py"
    
    # Save the original database URL
    original_db_url = os.environ.get("DATABASE_URL")
    
    try:
        # Set an invalid database URL to force retry
        os.environ["DATABASE_URL"] = "postgresql://invalid:invalid@localhost:5432/nonexistent"
        
        # Start a timer
        start_time = time.time()
        
        # Run the script with a short timeout to capture just the first retry
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,  # Short timeout to capture just the first retry
            )
            
            # This should not execute because the script should time out
            pytest.fail("Script should have timed out due to retries")
            
        except subprocess.TimeoutExpired as e:
            # This is expected - the script should be retrying
            elapsed_time = time.time() - start_time
            
            # Check that it retried at least once (should take at least 1 second)
            assert elapsed_time >= 1, "Script did not retry as expected"
            
            # Check stdout for retry messages
            if hasattr(e, "stdout") and e.stdout:
                stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else e.stdout
                assert "Retrying" in stdout, "Retry message not found in output"
                
            logger.info("Retry behavior verified successfully")
            
    finally:
        # Restore the original database URL
        if original_db_url:
            os.environ["DATABASE_URL"] = original_db_url
        else:
            os.environ.pop("DATABASE_URL", None) 
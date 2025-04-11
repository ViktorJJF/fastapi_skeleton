# Testing Strategy

This directory contains tests for the AlbedoAI project. The tests are organized into several categories:

## Directory Structure

- `tests/api/`: API integration tests that validate the endpoints function correctly
- `tests/unit/`: Unit tests for individual components (controllers, models, etc.)
- `tests/integration/`: Integration tests that validate interactions between components
- `tests/e2e/`: End-to-end tests that validate complete system functionality

## Test Components

### 1. Pytest Configuration

- `pytest.ini`: Contains pytest configuration for the project
- `conftest.py`: Contains shared fixtures for testing

### 2. Fixtures

Our tests use the following key fixtures:

- `event_loop`: Creates an event loop for async tests
- `db_session`: Provides a database session for tests
- `client`: Provides an AsyncClient for making HTTP requests to the test app

### 3. Test Categories

#### API Tests

API tests validate that the endpoints work correctly from an external perspective. They:
- Test all CRUD operations
- Verify error handling
- Check response formats and status codes

#### Unit Tests

Unit tests focus on testing individual components in isolation. They:
- Mock database interactions
- Test controller functions
- Verify error handling logic

#### Integration Tests

Integration tests verify that components work correctly together. They:
- Test database operations
- Validate data transformations
- Check complex behaviors across multiple components

#### End-to-End Tests

E2E tests validate the complete system functionality:
- Run actual scripts as subprocesses
- Test startup and initialization procedures
- Verify system behavior in real-world scenarios

## Running Tests

To run the tests, execute:

```bash
# Run all tests
pytest

# Run specific test category
pytest tests/api/
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run a specific test file
pytest tests/api/assistants/test_assistants_crud.py

# Run with coverage
pytest --cov=app

# Skip end-to-end tests (which may be slower)
pytest -k "not e2e"

# Run only end-to-end tests
pytest -m e2e
```

## Test Database

The tests use a separate test database to avoid affecting production data. The test database is created and destroyed dynamically during the test session.

## Pre-start Script Testing

We have specific tests for the database initialization and pre-start script:

1. Unit tests in `tests/unit/test_backend_pre_start.py` that test the core logic with mocks
2. Integration tests in `tests/integration/test_backend_initialization.py` that test with a real database
3. E2E tests in `tests/e2e/test_backend_pre_start_e2e.py` that test the actual script execution 
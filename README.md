# Albedo API

A scalable FastAPI project with MVC patterns, PostgreSQL, Redis, and logging.

## Run this project

```bash
# Ensure Docker and Docker Compose are running
docker-compose up -d --build 
# Run migrations
make db-migrate 

# Start the server
make dev

uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

## Features

- FastAPI with async support
- PostgreSQL database with SQLAlchemy ORM
- Redis for caching (optional, needs setup)
- **JWT Authentication** with role-based access control (`USER`, `ADMIN`, `SUPERADMIN`)
- **User Management** (CRUD, Registration, Login, Password Reset)
- Alembic for database migrations (with Makefile shortcuts)
- Loguru for structured logging
- Docker and Docker Compose for containerization
- MVC-like architecture
- Generic database helper functions for CRUD operations
- Pagination and filtering utilities

## Project Structure

```
.
├── alembic.ini           # Alembic configuration
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for the application
├── Makefile              # Makefile for common commands
├── migrations/           # Database migrations
│   ├── versions/         # Migration script files
│   ├── env.py            # Alembic environment setup
│   └── script.py.mako    # Alembic migration template
├── poetry.lock           # Poetry lock file
├── pyproject.toml        # Python project configuration (Poetry)
├── README.md             # This file
└── app/
    ├── __init__.py
    ├── backend_pre_start.py # Script to run before app starts (e.g., wait for DB)
    ├── main.py             # FastAPI application entrypoint
    ├── core/               # Core settings and utilities
    │   └── config.py       # Application configuration (Pydantic settings)
    ├── controllers/        # Request handlers and business logic
    │   ├── assistant_controller.py
    │   ├── auth_controller.py
    │   └── user_controller.py
    ├── database/           # Database connection and session management
    │   ├── connection.py
    │   └── redis.py 
    ├── db/                 # Base class for models (consider merging with database/)
    │   └── base_class.py   
    ├── dependencies/       # FastAPI dependencies
    │   └── security.py     # Authentication and authorization dependencies
    ├── middlewares/        # Custom FastAPI middlewares
    │   └── logging_middleware.py
    ├── models/             # SQLAlchemy ORM models
    │   ├── __init__.py
    │   ├── assistant.py
    │   ├── auth.py
    │   └── user.py
    ├── routes/             # API endpoint definitions
    │   └── v1/             # API version 1
    │       ├── __init__.py
    │       ├── api.py      # Main v1 router aggregation
    │       ├── assistants.py
    │       ├── auth.py
    │       ├── messages.py # (Example, assuming it exists)
    │       ├── threads.py  # (Example, assuming it exists)
    │       └── users.py
    ├── schemas/            # Pydantic schemas (data validation & serialization)
    │   ├── __init__.py
    │   ├── assistant.py
    │   ├── auth.py
    │   ├── core/           # Core schema components
    │   │   ├── paginations.py
    │   │   └── responses.py
    │   └── user.py
    ├── tests/              # Unit and integration tests (placeholder)
    └── utils/              # Utility functions
        ├── db_helpers.py   # Database helper functions
        ├── error_handling.py # Error handling utilities
        ├── pagination.py   # Pagination utilities
        └── security.py     # Security utilities (JWT, passwords)

```

## Getting Started

### Prerequisites

- Python 3.11+
- Poetry
- Docker and Docker Compose (Recommended)
- PostgreSQL Database
- Redis (Optional)

### Running the Application (Docker - Recommended)

1.  Clone the repository
2.  Ensure Docker Desktop or Docker Engine with Compose plugin is running.
3.  Copy `.env.example` to `.env` and configure necessary variables (like `SECRET_KEY`, database connection if not using default Docker Compose setup).
4.  Run the application:
    ```bash
    docker-compose up -d --build
    ```
5.  Access the API documentation at http://localhost:4000/docs

### Running the Application (Locally)

1.  Clone the repository.
2.  Install dependencies: `poetry install`
3.  Set up a PostgreSQL database and optionally Redis.
4.  Create a `.env` file from `.env.example` and update `DATABASE_URL`, `REDIS_URL` (if needed), `SECRET_KEY`, etc.
5.  Ensure the database specified in `DATABASE_URL` exists. You might need to create it manually (e.g., `createdb your_db_name`).
6.  Apply database migrations: `make db-migrate` (or `poetry run alembic upgrade head`)
7.  Start the server: `make run` (or `poetry run uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload`)

### Database Migrations

This project uses Alembic for database migrations. Common commands are available via Makefile shortcuts (recommended) or directly using `poetry run alembic`.

**Using Makefile:**

```bash
# Creating Migrations
make db-create NAME="create users table"          # Create migration based on model changes
make db-create-empty NAME="add custom function"   # Create empty migration for custom SQL
make db-create-branch NAME="fix" PARENT="abc123"  # Create branch from specific parent

# Running Migrations
make db-migrate                # Apply all pending migrations
make db-migrate REVISION="abc" # Migrate to specific revision
make db-rollback               # Rollback one migration
make db-rollback STEP=3        # Rollback three migrations
make db-reset                  # Reset database (down to base, up to head)

# Information Commands
make db-status                 # Show current migration status
make db-history                # Show migration history
make db-history RANGE="abc:xyz" # Show specific migration range
make db-show REVISION="abc123" # Show details of a specific revision
make db-heads                  # Show current branch heads
make db-branches               # Show branch points

# Advanced Operations
make db-stamp REVISION="abc123" # Mark revision as applied without running
make db-sql                    # Generate SQL without executing
make db-sql REVISION="abc" OUTPUT="migration.sql" # Generate SQL to file
make db-verify                 # Verify migration setup
```

### Migration Architecture

The migration system consists of the following components:

- `alembic.ini` - Configuration file at project root
- `migrations/` - Main directory containing migration files
  - `env.py` - Environment configuration with SQLAlchemy setup
  - `script.py.mako` - Template for new migration files
  - `versions/` - Directory containing the actual migrations
  - `README.md` - Detailed documentation on the migration system

### Key Features

Our migration system includes several advanced features:

1. **Consistent naming conventions** for constraints and indexes
2. **Automatic retries** with exponential backoff for database connections
3. **Transaction-per-migration** for safer migration application
4. **Comprehensive error handling** during migration runs
5. **Support for branched migrations** for complex development workflows
6. **Cross-database compatibility** with SQLite batch operations

### Typical Workflow

1. Modify your SQLAlchemy models in `app/models/`
2. Run `make db-create NAME="describe your changes"`
3. Review the auto-generated migration in `migrations/versions/`
4. Apply with `make db-migrate`

For more information, see `migrations/README.md` for detailed guidelines.

## API Documentation

- Swagger UI: http://localhost:4000/docs
- ReDoc: http://localhost:4000/redoc

## API Endpoints

All API endpoints are prefixed with `/api/v1`. Key endpoints include:

- `/api/v1/health` - Health check
- `/api/v1/auth/register` - User registration (POST)
- `/api/v1/auth/login` - User login (POST, returns JWT)
- `/api/v1/auth/verify` - Email verification (POST)
- `/api/v1/auth/forgot-password` - Request password reset (POST)
- `/api/v1/auth/reset-password` - Reset password with token (POST)
- `/api/v1/users/` - User management (GET list, POST create) - Requires Admin/Superadmin
- `/api/v1/users/me` - Get current user's info (GET) - Requires logged-in user
- `/api/v1/users/{user_id}` - User details, update, delete (GET, PUT, DELETE) - Requires Admin/Superadmin
- `/api/v1/assistants/` - Assistant management (GET list, POST create) - Requires Admin/Superadmin
- `/api/v1/assistants/{assistant_id}` - Assistant details, update, delete (GET, PUT, DELETE) - Requires Admin/Superadmin

*(Note: Access control based on current implementation, subject to change)*

## Architecture

The project follows a layered architecture inspired by MVC, aiming for separation of concerns:

- **Routes (`app/routes/v1/`)**: Define API endpoints, handle request/response validation (using schemas), call controllers, and manage dependencies (like authentication).
- **Controllers (`app/controllers/`)**: Orchestrate the business logic for specific features. They interact with database helpers/services and format responses.
- **Models (`app/models/`)**: Define the database structure using SQLAlchemy ORM.
- **Schemas (`app/schemas/`)**: Define data shapes for request validation and response serialization using Pydantic.
- **Dependencies (`app/dependencies/`)**: Provide reusable logic for routes, particularly for security (authentication, authorization).
- **Utilities (`app/utils/`)**: Contain helper functions for common tasks like database operations (`db_helpers.py`), security (`security.py`), pagination, and error handling.
- **Core (`app/core/`)**: Holds application-wide configuration.
- **Database (`app/database/`)**: Manages database connections and sessions.

### Database Helpers

The `app/utils/db_helpers.py` file provides generic utilities for common database operations like fetching, creating, updating, and deleting single or multiple items, along with pagination and filtering logic. Controllers utilize these helpers to interact with the database.

### Authentication Flow

1.  User registers via `/auth/register`.
2.  User logs in via `/auth/login` (providing email/password).
3.  Server verifies credentials, checks for blocks/verification status.
4.  If successful, server generates a JWT access token containing user ID, role, email, and expiration.
5.  Server returns the access token to the client.
6.  Client sends the access token in the `Authorization: Bearer <token>` header for subsequent requests to protected endpoints.
7.  FastAPI, using security dependencies (`app/dependencies/security.py`), decodes and validates the token on incoming requests.
8.  Dependencies check if the user has the required role (scopes) for the specific endpoint.
9.  If the token is valid and the user has permissions, the request proceeds to the controller logic.

### Table Naming Convention

All database tables use plural names (e.g., `assistants` instead of `assistant`). The base model automatically handles pluralization of table names.

### Working with Migrations

We provide several commands to manage database migrations:

```bash
# Creating migrations
make db-create NAME="create users table"          # Auto-generate migration from model changes
make db-create-empty NAME="add custom function"   # Create empty migration for manual edits

# Running migrations
make db-migrate                                   # Apply all pending migrations 
make db-migrate REVISION="abc123"                 # Migrate to specific revision

# Rolling back
make db-rollback                                  # Rollback one migration
make db-rollback STEP=3                           # Rollback multiple migrations

# Information
make db-status                                    # Show current migration status
make db-history                                   # Show migration history
```

For a complete list of database commands, run:

```bash
make help
``` 
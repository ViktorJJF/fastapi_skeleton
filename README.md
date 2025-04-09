# Albedo API

A scalable FastAPI project with MVC patterns, PostgreSQL, Redis, and logging.

## Features

- FastAPI with async support
- PostgreSQL database with SQLAlchemy ORM
- Redis for caching
- JWT authentication
- Alembic for database migrations
- Loguru for logging
- Docker and Docker Compose for containerization
- MVC architecture (Models, Views/Controllers, Services)
- Generic base controller for CRUD operations
- Pagination and filtering utilities

## Project Structure

```
app/
├── controllers/        # Controllers for handling business logic
│   ├── base_controller.py  # Generic base controller
│   └── ...             # Specific controllers
├── core/               # Core functionality (config, security, etc.)
├── db/                 # Database related code
│   └── migrations/     # Alembic migrations
├── middlewares/        # Custom middlewares
├── models/             # SQLAlchemy models
├── repositories/       # Data access layer
├── routes/             # API routes
│   └── v1/             # API version 1 routes
├── schemas/            # Pydantic schemas
├── services/           # Business logic
├── tests/              # Tests
└── utils/              # Utility functions
    ├── db_helpers.py   # Database helper functions
    ├── error_handling.py  # Error handling utilities
    └── pagination.py   # Pagination utilities
```

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the Application

1. Clone the repository
2. Run the application with Docker Compose:

```bash
docker-compose up -d
```

3. Access the API documentation at http://localhost:4000/docs

### Database Migrations

This project uses Alembic for database migrations, following best practices from the official documentation:

- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto-generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Naming Conventions](https://alembic.sqlalchemy.org/en/latest/naming.html)
- [Cookbook Recipes](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

Our migration system provides a Rails-like experience with a comprehensive set of commands:

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

All API endpoints are prefixed with `/api`. For example:

- `/api/health` - Health check endpoint
- `/api/v1/assistants` - Cities endpoints

## Architecture

The project follows a clean architecture pattern with separation of concerns:

- **Routes**: Handle HTTP requests and responses in the `app/routes` directory
- **Controllers**: Contain business logic in the `app/controllers` directory
- **Models**: SQLAlchemy models in the `app/models` directory
- **Schemas**: Pydantic schemas for validation in the `app/schemas` directory
- **Services**: Business logic in the `app/services` directory
- **Repositories**: Data access in the `app/repositories` directory

### Base Controller

The `BaseController` class provides generic CRUD operations for any model:

```python
class CityController(BaseController):
    def __init__(self):
        super().__init__(
            model=City,
            create_schema=CityCreate,
            update_schema=CityUpdate,
            get_schema=CitySchema,
            prefix="/cities",
            tags=["cities"],
            unique_fields=["name"]
        )
```

### Nested Routes Example

The project supports nested routes, such as entities under assistants:

```python
@router.get("/{assistant_id}/entities", response_model=dict)
async def entities_list(
    assistant_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    List all entities for a specific assistant.
    """
    return await entities_controller.lists(request, assistant_id, db)
```

### Database Helpers

The `db_helpers.py` file provides utilities for database operations:

- `get_all_items`: Get all items from a model
- `get_items`: Get paginated items with filtering
- `get_item`: Get a single item by ID
- `create_item`: Create a new item
- `update_item`: Update an existing item
- `delete_item`: Delete an item

### Pagination

The `pagination.py` file provides utilities for pagination:

```python
# Example usage in a controller
@router.get("/", response_model=PaginatedResponse[MySchema])
async def get_items(
    page: int = Depends(pagination_params),
    size: int = Depends(pagination_params),
    db: AsyncSession = Depends(get_db)
):
    items = await get_items(db, MyModel, page, size)
    return paginate(items, total, page, size)
```

## License

This project is licensed under the MIT License.

## Database Setup

### Initial Setup

To set up the database for the first time:

```bash
# One-step setup (creates database and runs migrations)
make db-setup

# Reset tables and re-run migrations (useful for table name changes)
make db-setup-reset

# Or step by step:
make db-create-database  # Creates the albedo_db database
make db-reset-tables     # Optional: Drop existing tables and reset migration state
make db-migrate          # Runs all pending migrations
```

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
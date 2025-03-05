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

To create a new migration:

```bash
docker-compose exec albedo alembic revision --autogenerate -m "Description"
```

To apply migrations:

```bash
docker-compose exec albedo alembic upgrade head
```

## API Documentation

- Swagger UI: http://localhost:4000/docs
- ReDoc: http://localhost:4000/redoc

## API Endpoints

All API endpoints are prefixed with `/api`. For example:

- `/api/health` - Health check endpoint
- `/api/v1/cities` - Cities endpoints
- `/api/v1/users` - Users endpoints
- `/api/v1/assistants/{assistant_id}/entities` - Entities endpoints for a specific assistant

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
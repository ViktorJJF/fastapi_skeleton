# Database Migrations

This directory contains database migrations for the Albedo API using Alembic.

## Migration Architecture

We use Alembic to manage database schema changes in a versioned and automated way, following the best practices outlined in the Alembic documentation:

- [Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto Generating Migrations](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Naming Conventions](https://alembic.sqlalchemy.org/en/latest/naming.html)
- [Cookbook Recipes](https://alembic.sqlalchemy.org/en/latest/cookbook.html)

## Key Components

- `env.py` - The migration environment configuration
- `versions/` - Directory containing migration scripts
- `script.py.mako` - Template for new migration files
- `alembic.ini` - Alembic configuration file (at project root)

## Migration Workflow

The typical migration workflow follows these steps:

1. Update SQLAlchemy models in `app/models/`
2. Generate a migration: `make db-create NAME="describe your changes"`
3. Review the auto-generated migration in `migrations/versions/`
4. Apply the migration: `make db-migrate`
5. (If needed) Roll back: `make db-rollback`

## Creating Migrations

There are two ways to create migrations:

### Auto-generated migrations

When you modify SQLAlchemy models, you can auto-generate a migration:

```bash
# Using the script
python scripts/db.py create "your migration message"

# Or using make
make db-create NAME="your migration message"
```

### Manual migrations

For complex operations (e.g., data migrations, custom triggers), create an empty migration:

```bash
# Using the script
python scripts/db.py create-empty "your migration message"

# Or using make
make db-create-empty NAME="your migration message"
```

## Applying Migrations

To apply migrations:

```bash
# Using the script
python scripts/db.py migrate

# Or using make
make db-migrate
```

## Rolling Back Migrations

To roll back the most recent migration:

```bash
# Using the script
python scripts/db.py rollback

# Or using make
make db-rollback
```

To roll back multiple migrations:

```bash
# Using the script
python scripts/db.py rollback 3  # Roll back 3 migrations

# Or using make
make db-rollback-to STEP=3
```

## Advanced Features

### Relative Migration Identifiers

Alembic supports relative migration identifiers:

- `+2` - Upgrade 2 revisions from current
- `-1` - Downgrade 1 revision from current
- `ae10+2` - Upgrade 2 revisions from revision ae10

### Partial Revision Identifiers

You can use partial revision identifiers as long as they're unique:

```bash
# Instead of alembic upgrade ae1027a6acf
alembic upgrade ae10
```

### Generating SQL Scripts

To generate SQL without executing (offline mode):

```bash
alembic upgrade head --sql > migration.sql
```

## Best Practices

1. **One logical change per migration**: Each migration should make one coherent change.
2. **Use consistent naming conventions**: We use the SQLAlchemy naming convention for constraints.
3. **Always review auto-generated migrations**: Auto-generation can miss subtleties.
4. **Include data migrations in schema changes**: When changing schema, handle existing data.
5. **Transactions**: Use transaction-safe operations where possible.
6. **Test migrations thoroughly**: Especially test downgrade operations.
7. **Use bulk operations for large tables**: For large data sets, use bulk operations.
8. **Use post-write hooks**: We use hooks to format migration files.

## Common Issues & Solutions

### Migration Dependencies

If working on multiple branches, you might need to manage migration dependencies:

```python
# In your migration file:
depends_on = ('previous_revision_id',)
```

### Batch Migrations

For databases with limited ALTER TABLE support (e.g., SQLite), use batch migrations:

```python
# Example from cookbook
with op.batch_alter_table('table_name') as batch_op:
    batch_op.add_column(sa.Column('new_col', sa.Integer()))
```

### Constraint Naming

We follow SQLAlchemy naming conventions for constraints to ensure consistent naming across environments.

### Database Connection Retries

Our migration environment includes connection retry logic with exponential backoff, which is useful in containerized environments where the database might not be immediately available. 
# Database Migrations

This directory contains database migrations for the plugin system. We use Alembic for managing PostgreSQL database schema changes.

## Setup

1. Install required packages:
```bash
pip install alembic psycopg2-binary
```

2. Configure your PostgreSQL connection in `alembic.ini`:
```ini
sqlalchemy.url = postgresql://user:password@localhost:5432/dbname
```

Replace the following with your actual PostgreSQL credentials:
- `user`: Database username
- `password`: Database password
- `localhost`: Database host
- ``: PostgreSQL port (default)
- `dbname`: Database name

## Usage

### Creating a New Migration

To create a new migration:

```bash
alembic revision -m "description of changes"
```

This will create a new migration file in the `versions` directory.

### Running Migrations

To apply all pending migrations:

```bash
alembic upgrade head
```

To apply migrations up to a specific version:

```bash
alembic upgrade <revision_id>
```

### Rolling Back Migrations

To rollback the last migration:

```bash
alembic downgrade -1
```

To rollback to a specific version:

```bash
alembic downgrade <revision_id>
```

### Viewing Migration Status

To see the current migration status:

```bash
alembic current
```

To see migration history:

```bash
alembic history
```

## Migration Structure

Each migration file contains:
- `upgrade()`: Function to apply the migration
- `downgrade()`: Function to revert the migration
- Metadata about the migration (revision ID, dependencies, etc.)

## PostgreSQL-Specific Features

The migrations use PostgreSQL-specific features:
- Indexes for performance optimization
- Views for data abstraction
- Text columns for large string data
- DateTime columns for timestamps
- Primary key constraints
- Composite indexes

## Best Practices

1. Always include both `upgrade()` and `downgrade()` methods
2. Test migrations before applying to production
3. Keep migrations atomic and focused
4. Use meaningful descriptions in migration messages
5. Back up data before running migrations
6. Test downgrade paths to ensure rollback works
7. Use appropriate PostgreSQL data types
8. Create indexes for frequently queried columns
9. Consider partitioning for large tables
10. Use transactions for data consistency 
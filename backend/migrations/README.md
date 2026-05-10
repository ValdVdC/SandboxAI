# Alembic Migrations Guide

## Overview

Alembic is used for database schema versioning and migrations. All database changes are tracked and can be applied/reverted.

## Files Structure

```
alembic/
├── versions/          # Migration scripts
│   ├── 001_initial.py      # Initial schema creation
│   └── __init__.py
├── env.py            # Alembic runtime configuration
├── script.py.mako    # Template for new migration files
└── __init__.py
```

## How to Use

### 1. Initialize Database (On First Run)

When the API starts, it automatically runs migrations via the startup event in `app/main.py`.

Alternatively, run manually:
```bash
cd backend
python -m alembic upgrade head
```

### 2. Create a New Migration

When you modify models in `app/models/`, create a migration:

```bash
cd backend
python -m alembic revision --autogenerate -m "Add new column to users"
```

This creates a new file in `alembic/versions/` with the schema changes.

### 3. Review Migration

Before applying, check the generated migration file:
```bash
cat alembic/versions/XXX_add_new_column_to_users.py
```

Make sure the `upgrade()` and `downgrade()` functions are correct.

### 4. Apply Migration

```bash
cd backend
python -m alembic upgrade head
```

### 5. Rollback Migration

```bash
cd backend
python -m alembic downgrade -1   # Rollback the last migration
python -m alembic downgrade 001_initial  # Rollback to specific revision
```

### 6. Check Migration Status

```bash
cd backend
python -m alembic current     # Current database revision
python -m alembic history    # All applied migrations
```

## Environment Variables

The migrations use the `DATABASE_URL` environment variable:
```
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/sandboxai
```

For Alembic to connect, it converts this to a sync URL:
```
postgresql://user:pass@postgres:5432/sandboxai
```

## Important Notes

1. **Always** create migrations after changing models
2. Alembic only tracks what's in models - manual database changes won't be detected
3. Test migrations in development before running in production
4. Keep migrations small and focused on one change
5. Never edit migration files after they've been applied to production

## Troubleshooting

### Migration fails with "table already exists"
- Database tables were created directly, not through migrations
- Run: `python -m alembic stamp head` to mark current schema as migrated

### asyncpg import error in env.py
- Install asyncpg: `pip install asyncpg`
- Alembic uses sync connections even with async database

### Python path issues
- Ensure `backend/` is the working directory when running Alembic
- Or set `PYTHONPATH=. alembic upgrade head`

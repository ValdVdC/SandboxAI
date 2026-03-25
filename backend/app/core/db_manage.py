"""Database management utilities."""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

from app.core.database import dispose_engine, engine
from app.models import Base


async def init_database():
    """
    Initialize database with Alembic migrations.

    This should be called on application startup.
    """
    # Run Alembic upgrade to latest revision
    backend_dir = Path(__file__).parent.parent.parent
    alembic_dir = backend_dir / "alembic"

    # Prepare environment for Alembic
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir.parent)

    # Run Alembic upgrade
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(backend_dir),
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Alembic upgrade failed: {result.stderr}")
        # Fallback: create all tables if Alembic fails
        print("Creating tables with SQLAlchemy...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        print("Database migration completed successfully")

    await dispose_engine()


async def create_migration(message: str) -> None:
    """
    Create a new migration file.

    Args:
        message: Description of the migration
    """
    backend_dir = Path(__file__).parent.parent.parent

    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir.parent)

    result = subprocess.run(
        [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message],
        cwd=str(backend_dir),
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Failed to create migration: {result.stderr}")
    else:
        print(f"Migration created: {result.stdout}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.core.db_manage <command> [args]")
        print("Commands:")
        print("  init           - Initialize database")
        print("  migrate <msg>  - Create new migration")
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        asyncio.run(init_database())
    elif command == "migrate" and len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
        asyncio.run(create_migration(message))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

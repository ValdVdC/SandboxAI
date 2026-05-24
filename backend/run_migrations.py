#!/usr/bin/env python
"""Script to run Alembic migrations programmatically"""

import os
import sys

from alembic import command
from alembic.config import Config


def run_migrations():
    """Execute pending Alembic migrations"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Create Alembic config
    alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL environment variable is required", file=sys.stderr)
        return 1

    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Run migrations
    print("🔄 Running database migrations...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return 0
    except Exception as e:
        print(f"❌ Migration failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(run_migrations())

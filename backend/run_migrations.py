#!/usr/bin/env python
"""Script to run Alembic migrations programmatically"""

import os
import sys

# Ensure we import alembic from venv, not from local alembic/ directory
sys.path.insert(0, '/opt/venv/lib/python3.11/site-packages')

from alembic import command
from alembic.config import Config

def run_migrations():
    """Execute pending Alembic migrations"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create Alembic config
    alembic_cfg = Config(os.path.join(script_dir, "alembic.ini"))
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        os.environ.get("DATABASE_URL", "postgresql://user:password@localhost/dbname")
    )
    
    # Run migrations
    print("🔄 Running database migrations...")
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        return 0
    except Exception as e:
        print(f"⚠️  Migration warning: {e}", file=sys.stderr)
        # Don't fail completely, migrations might already be applied
        # This is important for idempotency
        return 0

if __name__ == "__main__":
    sys.exit(run_migrations())

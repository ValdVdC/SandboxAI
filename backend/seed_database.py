#!/usr/bin/env python
"""
Seed script to populate database with test data
Run this after migrations to ensure database has default test users
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import User
from app.core.security import hash_password


async def seed_database():
    """Create test users for development"""
    
    # Get database URL from environment
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://sandboxai:sandboxai@postgres:5432/sandboxai"
    )
    
    # Create async engine
    engine = create_async_engine(database_url, echo=False)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if test user already exists
            from sqlalchemy import select
            stmt = select(User).where(User.email == "test@example.com")
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print("✅ Test user already exists, skipping seed")
                return
            
            # Create test user
            test_user = User(
                email="test@example.com",
                hashed_password=hash_password("test123456"),
                full_name="Test User",
                is_active=True,
            )
            
            session.add(test_user)
            await session.commit()
            
            print("✅ Test user created successfully!")
            print("   Email: test@example.com")
            print("   Password: test123456")
            
        except Exception as e:
            print(f"❌ Seed failed: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())

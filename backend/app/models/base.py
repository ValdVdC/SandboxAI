"""Base model class for SQLAlchemy ORM models."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base

# Create declarative base for all models
Base = declarative_base()


class BaseModel(Base):
    """Base class for all models with common fields."""

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

"""Base model class for SQLAlchemy ORM models."""

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

# Create declarative base for all models
Base = declarative_base()


class BaseModel(Base):
    """Base class for all models with common fields."""

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        default=datetime.utcnow,
    )

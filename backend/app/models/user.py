"""User model."""

from sqlalchemy import Column, String, UUID, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
import uuid
from .base import BaseModel


class User(BaseModel):
    """User model representing application users."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False)

    # Relationships
    prompts = relationship(
        "Prompt",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Prompt.user_id",
    )

    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"

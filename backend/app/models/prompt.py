"""Prompt model."""

from sqlalchemy import Column, String, Text, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid
from .base import BaseModel


class Prompt(BaseModel):
    """Prompt model representing AI prompt templates."""

    __tablename__ = "prompts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    version_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User", back_populates="prompts", foreign_keys=[user_id])
    versions = relationship(
        "PromptVersion",
        back_populates="prompt",
        cascade="all, delete-orphan",
        foreign_keys="PromptVersion.prompt_id",
    )

    def __repr__(self) -> str:
        return f"<Prompt(id={self.id}, name={self.name}, user_id={self.user_id})>"

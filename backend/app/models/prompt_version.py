"""Prompt Version model."""

from sqlalchemy import Column, String, Text, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid
from .base import BaseModel


class PromptVersion(BaseModel):
    """PromptVersion model representing versions of prompts."""

    __tablename__ = "prompt_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=False)  # "ollama", "groq", "openai", "anthropic"
    model = Column(String(100), nullable=False)  # "llama2:7b", "gpt-4", etc
    change_description = Column(Text, nullable=True)  # Description of changes in this version

    # Relationships
    prompt = relationship("Prompt", back_populates="versions", foreign_keys=[prompt_id])
    test_results = relationship(
        "TestResult",
        back_populates="prompt_version",
        cascade="all, delete-orphan",
        foreign_keys="TestResult.version_id",
    )

    __table_args__ = (
        # Unique constraint: each prompt can have only one version number
        # We'll add this via migration for better control
    )

    def __repr__(self) -> str:
        return f"<PromptVersion(id={self.id}, prompt_id={self.prompt_id}, version={self.version}, provider={self.provider}, model={self.model})>"

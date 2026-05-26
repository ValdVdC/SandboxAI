"""Test Result model."""

import uuid
from decimal import Decimal

from sqlalchemy import (
    UUID,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import relationship

from .base import BaseModel


class TestResult(BaseModel):
    """TestResult model representing results of prompt tests."""

    __tablename__ = "test_results"

    __table_args__ = (CheckConstraint("score >= 0.0 AND score <= 1.0", name="check_score_range"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("prompt_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # To group bulk tests
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=True)
    expected = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)  # Response time in milliseconds
    tokens_used = Column(Integer, nullable=True)  # Number of tokens consumed
    cost_usd = Column(Numeric(10, 6), nullable=True, default=Decimal("0.0"))  # Cost in USD
    score = Column(Numeric(3, 2), nullable=True)  # Validation score (0.0 to 1.0)
    is_correct = Column(Boolean, nullable=True)  # Whether the output matches expected
    is_human_overridden = Column(
        Boolean, default=False, nullable=False, server_default=text("false")
    )  # Whether a human has overridden the result
    status = Column(
        String(50), nullable=False, default="pending"
    )  # "pending", "completed", "failed"
    error_message = Column(Text, nullable=True)  # Error details if status is "failed"

    # Relationships
    prompt_version = relationship(
        "PromptVersion", back_populates="test_results", foreign_keys=[version_id]
    )

    def __repr__(self) -> str:
        return f"<TestResult(id={self.id}, version_id={self.version_id}, status={self.status}, latency_ms={self.latency_ms})>"

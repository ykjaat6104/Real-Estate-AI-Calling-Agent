"""Lead model for captured sales leads."""
import uuid

from sqlalchemy import String, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Lead(Base, TimestampMixin):
    """Represents a captured sales lead from a call."""

    __tablename__ = "leads"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    call_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    # Status tracking
    status: Mapped[str] = mapped_column(String(50), default="in_progress")
    # in_progress | qualified | unqualified | converted | lost

    # Lead details (from conversation)
    language: Mapped[str | None] = mapped_column(String(20))
    name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    purpose: Mapped[str | None] = mapped_column(String(100))  # buy | invest
    property_type: Mapped[str | None] = mapped_column(String(100))
    configuration: Mapped[str | None] = mapped_column(String(50))
    preferred_location: Mapped[str | None] = mapped_column(String(500))
    budget_min: Mapped[str | None] = mapped_column(String(50))
    budget_max: Mapped[str | None] = mapped_column(String(50))
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    timeline: Mapped[str | None] = mapped_column(String(100))
    questions_asked: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    # Call metadata
    call_summary: Mapped[str | None] = mapped_column(Text)
    transcript: Mapped[list] = mapped_column(JSONB, default=list)
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    # Sentiment & analytics
    sentiment_score: Mapped[float | None] = mapped_column(Float)
    sentiment_label: Mapped[str | None] = mapped_column(String(20))
    intent: Mapped[str | None] = mapped_column(String(50))  # hot_lead | warm_lead | cold_lead
    qualification_score: Mapped[float | None] = mapped_column(Float)

    # CRM integration
    crm_synced: Mapped[bool] = mapped_column(default=False)
    crm_synced_at: Mapped[str | None] = mapped_column(String(255))
    external_id: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    project = relationship("Project", back_populates="leads", lazy="selectin")
    call_records = relationship("CallRecord", back_populates="lead", lazy="selectin")

    def __repr__(self):
        return f"<Lead {self.name or self.call_id}>"

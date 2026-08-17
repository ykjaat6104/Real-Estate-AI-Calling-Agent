"""Call record model for tracking call analytics."""
import uuid

from sqlalchemy import String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CallRecord(Base, TimestampMixin):
    """Represents a call record with analytics."""

    __tablename__ = "call_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL")
    )

    call_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    call_type: Mapped[str | None] = mapped_column(String(20))  # web | inbound | outbound

    # Call details
    started_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[str | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int | None] = mapped_column(Integer)

    # Audio
    recording_url: Mapped[str | None] = mapped_column(String(500))
    recording_path: Mapped[str | None] = mapped_column(String(500))

    # Analytics
    sentiment_scores: Mapped[list] = mapped_column(JSONB, default=list)
    interruptions_count: Mapped[int] = mapped_column(Integer, default=0)
    turn_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_response_time_ms: Mapped[float | None] = mapped_column(Float)

    # Quality metrics
    audio_quality_score: Mapped[float | None] = mapped_column(Float)
    connection_quality: Mapped[str | None] = mapped_column(String(20))

    # Phone specific
    phone_number: Mapped[str | None] = mapped_column(String(50))
    sip_trunk: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    lead = relationship("Lead", back_populates="call_records", lazy="selectin")

    def __repr__(self):
        return f"<CallRecord {self.call_id}>"

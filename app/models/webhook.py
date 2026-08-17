"""Webhook model for CRM integration."""
import uuid

from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Webhook(Base, TimestampMixin):
    """Represents a webhook endpoint for CRM integration."""

    __tablename__ = "webhooks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    events: Mapped[list] = mapped_column(JSONB, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    deliveries = relationship("WebhookDelivery", back_populates="webhook", lazy="selectin")

    def __repr__(self):
        return f"<Webhook {self.url}>"


class WebhookDelivery(Base, TimestampMixin):
    """Tracks webhook delivery attempts."""

    __tablename__ = "webhook_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    webhook_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    response_code: Mapped[int | None] = mapped_column()
    response_body: Mapped[str | None] = mapped_column()
    error_message: Mapped[str | None] = mapped_column()
    attempts: Mapped[int] = mapped_column(default=0)

    # Relationships
    webhook = relationship("Webhook", back_populates="deliveries", lazy="selectin")

    def __repr__(self):
        return f"<WebhookDelivery {self.event_type} - {self.status}>"

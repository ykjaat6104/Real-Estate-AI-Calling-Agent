"""Tenant model for multi-tenant isolation."""
import uuid

from sqlalchemy import String, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    """Represents an organization/company using the platform."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)

    # Rate limits
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    max_concurrent_calls: Mapped[int] = mapped_column(Integer, default=5)

    # Relationships
    users = relationship("User", back_populates="tenant", lazy="selectin")
    projects = relationship("Project", back_populates="tenant", lazy="selectin")

    def __repr__(self):
        return f"<Tenant {self.name}>"

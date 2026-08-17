"""User model with role-based access control."""
import uuid

from sqlalchemy import String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """Represents a user within a tenant."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(50), default="agent")  # admin | manager | agent
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[str | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    tenant = relationship("Tenant", back_populates="users", lazy="selectin")

    def __repr__(self):
        return f"<User {self.email}>"

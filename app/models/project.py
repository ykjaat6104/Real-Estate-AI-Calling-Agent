"""Project model for real estate projects."""
import uuid

from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    """Represents a real estate project within a tenant."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    # Project details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    builder_name: Mapped[str | None] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(500))
    rera_number: Mapped[str | None] = mapped_column(String(100))

    # Flexible JSON fields
    configurations: Mapped[dict] = mapped_column(JSONB, default=dict)
    amenities: Mapped[list] = mapped_column(JSONB, default=list)
    location_advantages: Mapped[list] = mapped_column(JSONB, default=list)
    possession: Mapped[dict] = mapped_column(JSONB, default=dict)
    payment_plan: Mapped[str | None] = mapped_column(Text)

    # Agent persona
    agent_name: Mapped[str] = mapped_column(String(100), default="Priya")
    agent_persona: Mapped[str | None] = mapped_column(Text)
    language_mode: Mapped[str] = mapped_column(String(20), default="auto")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="projects", lazy="selectin")
    leads = relationship("Lead", back_populates="project", lazy="selectin")

    def __repr__(self):
        return f"<Project {self.name}>"

    def to_dict(self) -> dict:
        """Convert project to dictionary for prompt generation."""
        return {
            "name": self.name,
            "builder_name": self.builder_name,
            "location": self.location,
            "rera_number": self.rera_number,
            "configurations": self.configurations or {},
            "amenities": self.amenities or [],
            "location_advantages": self.location_advantages or [],
            "possession": self.possession or {},
            "payment_plan": self.payment_plan,
            "agent_name": self.agent_name,
            "language_mode": self.language_mode,
        }

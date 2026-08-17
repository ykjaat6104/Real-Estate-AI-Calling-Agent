"""Project schemas for request/response validation."""
from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID


class ProjectCreateSchema(BaseModel):
    """Schema for creating a project."""
    name: str
    slug: str
    builder_name: Optional[str] = None
    location: Optional[str] = None
    rera_number: Optional[str] = None
    configurations: Optional[dict[str, Any]] = None
    amenities: Optional[list[str]] = None
    location_advantages: Optional[list[str]] = None
    possession: Optional[dict[str, str]] = None
    payment_plan: Optional[str] = None
    agent_name: Optional[str] = "Priya"
    agent_persona: Optional[str] = None
    language_mode: Optional[str] = "auto"


class ProjectUpdateSchema(BaseModel):
    """Schema for updating a project."""
    name: Optional[str] = None
    builder_name: Optional[str] = None
    location: Optional[str] = None
    rera_number: Optional[str] = None
    configurations: Optional[dict[str, Any]] = None
    amenities: Optional[list[str]] = None
    location_advantages: Optional[list[str]] = None
    possession: Optional[dict[str, str]] = None
    payment_plan: Optional[str] = None
    agent_name: Optional[str] = None
    agent_persona: Optional[str] = None
    language_mode: Optional[str] = None
    is_active: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""
    id: UUID
    tenant_id: UUID
    name: str
    slug: str
    builder_name: Optional[str]
    location: Optional[str]
    rera_number: Optional[str]
    configurations: Optional[dict]
    amenities: Optional[list]
    location_advantages: Optional[list]
    possession: Optional[dict]
    payment_plan: Optional[str]
    agent_name: str
    language_mode: str
    is_active: bool

    class Config:
        from_attributes = True

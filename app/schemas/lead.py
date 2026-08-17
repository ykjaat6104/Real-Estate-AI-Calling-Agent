"""Lead schemas for request/response validation."""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class LeadCreateSchema(BaseModel):
    """Schema for creating a lead."""
    project_id: UUID
    call_id: str
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = None
    purpose: Optional[str] = None
    property_type: Optional[str] = None
    configuration: Optional[str] = None
    preferred_location: Optional[str] = None
    budget_min: Optional[str] = None
    budget_max: Optional[str] = None
    currency: Optional[str] = "INR"
    timeline: Optional[str] = None
    questions_asked: Optional[str] = None
    notes: Optional[str] = None


class LeadUpdateSchema(BaseModel):
    """Schema for updating a lead."""
    status: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    purpose: Optional[str] = None
    property_type: Optional[str] = None
    configuration: Optional[str] = None
    preferred_location: Optional[str] = None
    budget_min: Optional[str] = None
    budget_max: Optional[str] = None
    timeline: Optional[str] = None
    notes: Optional[str] = None
    call_summary: Optional[str] = None


class LeadResponse(BaseModel):
    """Schema for lead response."""
    id: UUID
    tenant_id: UUID
    project_id: UUID
    call_id: str
    status: str
    language: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    purpose: Optional[str]
    property_type: Optional[str]
    configuration: Optional[str]
    preferred_location: Optional[str]
    budget_min: Optional[str]
    budget_max: Optional[str]
    currency: str
    timeline: Optional[str]
    questions_asked: Optional[str]
    notes: Optional[str]
    call_summary: Optional[str]
    transcript: Optional[list]
    duration_seconds: Optional[int]
    sentiment_score: Optional[float]
    sentiment_label: Optional[str]
    intent: Optional[str]
    qualification_score: Optional[float]
    created_at: str

    class Config:
        from_attributes = True

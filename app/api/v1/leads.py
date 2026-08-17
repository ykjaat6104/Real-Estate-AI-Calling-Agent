"""Lead API endpoints."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.core.security import get_current_user
from app.core.rate_limit import rate_limit_dependency
from app.schemas.lead import LeadCreateSchema, LeadUpdateSchema, LeadResponse
from app.services.lead import (
    create_lead,
    get_lead_by_call_id,
    get_lead_by_id,
    list_leads,
    update_lead,
    analyze_sentiment,
    score_lead_quality,
)

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadResponse, status_code=201)
async def create_new_lead(
    data: LeadCreateSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _rate_limit: None = Depends(rate_limit_dependency),
):
    """Create a new lead."""
    # Check if lead already exists for this call
    existing = await get_lead_by_call_id(db, data.call_id, user.tenant_id)
    if existing:
        raise HTTPException(status_code=400, detail="Lead already exists for this call")

    lead = await create_lead(
        db,
        tenant_id=user.tenant_id,
        project_id=data.project_id,
        call_id=data.call_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        language=data.language,
        purpose=data.purpose,
        property_type=data.property_type,
        configuration=data.configuration,
        preferred_location=data.preferred_location,
        budget_min=data.budget_min,
        budget_max=data.budget_max,
        currency=data.currency,
        timeline=data.timeline,
        questions_asked=data.questions_asked,
        notes=data.notes,
    )

    return LeadResponse.from_orm(lead)


@router.get("/", response_model=list[LeadResponse])
async def list_all_leads(
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 100,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all leads for the current tenant."""
    leads = await list_leads(
        db,
        tenant_id=user.tenant_id,
        project_id=project_id,
        status=status,
        limit=limit,
    )
    return [LeadResponse.from_orm(l) for l in leads]


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a lead by ID."""
    lead = await get_lead_by_id(db, lead_id, user.tenant_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_existing_lead(
    lead_id: UUID,
    data: LeadUpdateSchema,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a lead."""
    lead = await update_lead(
        db,
        lead_id,
        user.tenant_id,
        **data.dict(exclude_unset=True),
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)


@router.get("/call/{call_id}", response_model=LeadResponse)
async def get_lead_by_call(
    call_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a lead by call ID (for live polling during calls)."""
    lead = await get_lead_by_call_id(db, call_id, user.tenant_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.from_orm(lead)

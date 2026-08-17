"""Authentication API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.schemas.auth import (
    RegisterSchema,
    LoginSchema,
    AuthResponse,
    UserResponse,
    TenantResponse,
)
from app.services.auth import (
    create_user,
    authenticate_user,
    create_tenant,
    get_tenant_by_slug,
    generate_tokens,
)
from app.core.security import get_current_user, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: RegisterSchema, db: AsyncSession = Depends(get_db)):
    """Register a new user and tenant."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create or get tenant
    if data.tenant_slug:
        tenant = await get_tenant_by_slug(db, data.tenant_slug)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
    else:
        # Create new tenant from company name
        slug = data.company_name.lower().replace(" ", "-") if data.company_name else data.email.split("@")[0]
        tenant = await create_tenant(db, name=data.company_name or slug, slug=slug)

    # Create user
    user = await create_user(
        db,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        tenant_id=tenant.id,
        role="admin" if not data.tenant_slug else "agent",
    )

    # Generate tokens
    tokens = await generate_tokens(user)

    return AuthResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.from_orm(user),
        tenant=TenantResponse.from_orm(tenant),
    )


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginSchema, db: AsyncSession = Depends(get_db)):
    """Login with email and password."""
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Get tenant
    result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = result.scalar_one_one()

    # Generate tokens
    tokens = await generate_tokens(user)

    return AuthResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        user=UserResponse.from_orm(user),
        tenant=TenantResponse.from_orm(tenant),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.from_orm(user)

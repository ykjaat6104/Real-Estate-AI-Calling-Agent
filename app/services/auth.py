"""Authentication service."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    role: str = "agent",
) -> User:
    """Create a new user."""
    user = User(
        tenant_id=tenant_id,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=role,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate a user by email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        return None

    return user


async def create_tenant(
    db: AsyncSession,
    name: str,
    slug: str,
    plan: str = "free",
) -> Tenant:
    """Create a new tenant."""
    tenant = Tenant(name=name, slug=slug, plan=plan)
    db.add(tenant)
    await db.flush()
    return tenant


async def get_tenant_by_slug(
    db: AsyncSession,
    slug: str,
) -> Optional[Tenant]:
    """Get a tenant by slug."""
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return result.scalar_one_or_none()


async def generate_tokens(user: User) -> dict:
    """Generate access and refresh tokens for a user."""
    access_token = create_access_token(
        {"sub": str(user.id), "tenant": str(user.tenant_id), "role": user.role}
    )
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

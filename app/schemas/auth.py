"""Auth schemas for request/response validation."""
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class RegisterSchema(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    tenant_slug: Optional[str] = None


class LoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class RefreshSchema(BaseModel):
    """Schema for token refresh."""
    refresh_token: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    email: str
    full_name: Optional[str]
    role: str
    tenant_id: UUID

    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    """Schema for tenant response."""
    id: UUID
    name: str
    slug: str
    plan: str
    is_active: bool

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for auth response with user and tenant."""
    access_token: str
    refresh_token: str
    user: UserResponse
    tenant: TenantResponse

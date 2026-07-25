from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from .models import Role, LeadStatus


# ---------- Auth / Users ----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: Role = Role.member


class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: Role
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Notes ----------

class NoteCreate(BaseModel):
    content: str = Field(min_length=1)


class NoteOut(BaseModel):
    id: str
    content: str
    author_id: str
    author_email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Activity ----------

class ActivityOut(BaseModel):
    id: str
    action: str
    detail: Optional[str] = None
    actor_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Leads ----------

class LeadPublicCreate(BaseModel):
    """Public capture form — no auth required."""
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=40)
    company: Optional[str] = Field(default=None, max_length=200)
    message: Optional[str] = Field(default=None, max_length=2000)


class LeadUpdate(BaseModel):
    status: Optional[LeadStatus] = None
    assigned_to_id: Optional[str] = None


class LeadOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    message: Optional[str] = None
    status: LeadStatus
    assigned_to_id: Optional[str] = None
    assigned_to_email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadDetailOut(LeadOut):
    notes: List[NoteOut] = []
    activities: List[ActivityOut] = []


class PaginatedLeads(BaseModel):
    items: List[LeadOut]
    total: int
    page: int
    page_size: int
    pages: int

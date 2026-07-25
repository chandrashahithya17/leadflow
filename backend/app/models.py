import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Enum, ForeignKey, Text, Integer
)
from sqlalchemy.orm import relationship

from .database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    admin = "admin"
    member = "member"


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    won = "won"
    lost = "lost"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False, default=Role.member)
    created_at = Column(DateTime, default=datetime.utcnow)

    assigned_leads = relationship("Lead", back_populates="assigned_to", foreign_keys="Lead.assigned_to_id")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    status = Column(Enum(LeadStatus), nullable=False, default=LeadStatus.new, index=True)

    assigned_to_id = Column(String, ForeignKey("users.id"), nullable=True)
    assigned_to = relationship("User", back_populates="assigned_leads", foreign_keys=[assigned_to_id])

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    notes = relationship("Note", back_populates="lead", cascade="all, delete-orphan", order_by="Note.created_at.desc()")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan", order_by="Activity.created_at.desc()")


class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=gen_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="notes")
    author = relationship("User")


class Activity(Base):
    """Audit trail: every meaningful change to a lead gets an entry here."""
    __tablename__ = "activities"

    id = Column(String, primary_key=True, default=gen_uuid)
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    actor_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g. "status_changed", "assigned", "note_added", "created"
    detail = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    lead = relationship("Lead", back_populates="activities")
    actor = relationship("User")

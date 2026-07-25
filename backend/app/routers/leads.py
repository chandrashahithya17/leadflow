import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from ..database import get_db
from ..models import Lead, LeadStatus, Note, Activity, User, Role
from ..schemas import (
    LeadPublicCreate, LeadOut, LeadDetailOut, LeadUpdate,
    NoteCreate, NoteOut, PaginatedLeads,
)
from ..deps import get_current_user

router = APIRouter(prefix="/api/leads", tags=["leads"])


def _lead_out(lead: Lead) -> LeadOut:
    data = LeadOut.model_validate(lead)
    data.assigned_to_email = lead.assigned_to.email if lead.assigned_to else None
    return data


def _log(db: Session, lead: Lead, actor: Optional[User], action: str, detail: Optional[str] = None):
    db.add(Activity(lead_id=lead.id, actor_id=actor.id if actor else None, action=action, detail=detail))


# ---------- Public: lead capture form ----------

@router.post("/public", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def submit_lead(payload: LeadPublicCreate, db: Session = Depends(get_db)):
    """No authentication required — this is the public-facing capture form."""
    lead = Lead(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        message=payload.message,
        status=LeadStatus.new,
    )
    db.add(lead)
    db.flush()
    _log(db, lead, actor=None, action="created", detail="Submitted via public capture form")
    db.commit()
    db.refresh(lead)
    return _lead_out(lead)


# ---------- Authenticated: list with pagination + filtering ----------

@router.get("", response_model=PaginatedLeads)
def list_leads(
    status_filter: Optional[LeadStatus] = Query(default=None, alias="status"),
    assigned_to_id: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None, description="Matches name, email, or company"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Lead).options(joinedload(Lead.assigned_to))

    if status_filter:
        q = q.filter(Lead.status == status_filter)
    if assigned_to_id:
        q = q.filter(Lead.assigned_to_id == assigned_to_id)
    if search:
        like = f"%{search}%"
        q = q.filter(or_(Lead.name.ilike(like), Lead.email.ilike(like), Lead.company.ilike(like)))

    total = q.count()
    pages = max(1, math.ceil(total / page_size))
    items = (
        q.order_by(Lead.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedLeads(
        items=[_lead_out(l) for l in items],
        total=total, page=page, page_size=page_size, pages=pages,
    )


@router.get("/{lead_id}", response_model=LeadDetailOut)
def get_lead(lead_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).options(joinedload(Lead.assigned_to)).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    notes_out = []
    for n in lead.notes:
        notes_out.append(NoteOut(
            id=n.id, content=n.content, author_id=n.author_id,
            author_email=n.author.email if n.author else None, created_at=n.created_at,
        ))

    base = _lead_out(lead)
    return LeadDetailOut(**base.model_dump(), notes=notes_out, activities=lead.activities)


# ---------- Authenticated: update (status pipeline + assignment) ----------

@router.patch("/{lead_id}", response_model=LeadOut)
def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    is_admin = current_user.role == Role.admin
    is_owner = lead.assigned_to_id == current_user.id

    # --- Permission rules (server-side; the UI mirrors these but this is the real gate) ---
    # Assignment: admins may assign any lead to anyone. Members may only claim an
    # unassigned lead for themselves — they cannot reassign someone else's lead.
    if payload.assigned_to_id is not None:
        if not is_admin:
            if payload.assigned_to_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Members can only assign leads to themselves",
                )
            if lead.assigned_to_id and lead.assigned_to_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This lead is already assigned to someone else",
                )
        target = db.query(User).filter(User.id == payload.assigned_to_id).first()
        if not target:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignee not found")
        old = lead.assigned_to.email if lead.assigned_to else "unassigned"
        lead.assigned_to_id = target.id
        _log(db, lead, current_user, "assigned", f"{old} -> {target.email}")

    # Status: admins can change status on any lead. Members can only change status
    # on leads currently assigned to them.
    if payload.status is not None:
        if not is_admin and not is_owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned member (or an admin) can update this lead's status",
            )
        old_status = lead.status.value
        lead.status = payload.status
        _log(db, lead, current_user, "status_changed", f"{old_status} -> {payload.status.value}")

    db.commit()
    db.refresh(lead)
    return _lead_out(lead)


# ---------- Notes ----------

@router.post("/{lead_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def add_note(
    lead_id: str,
    payload: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    note = Note(lead_id=lead.id, author_id=current_user.id, content=payload.content)
    db.add(note)
    _log(db, lead, current_user, "note_added")
    db.commit()
    db.refresh(note)
    return NoteOut(
        id=note.id, content=note.content, author_id=note.author_id,
        author_email=current_user.email, created_at=note.created_at,
    )

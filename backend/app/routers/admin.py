import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Role
from ..auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])

SEED_KEY = os.getenv("SEED_KEY", "")

DEMO_ACCOUNTS = [
    {"email": "admin@leadflow.demo", "password": "AdminPass123!", "role": Role.admin},
    {"email": "member@leadflow.demo", "password": "MemberPass123!", "role": Role.member},
]


@router.get("/seed")
def seed_demo_accounts(key: str = Query(...), db: Session = Depends(get_db)):
    if not SEED_KEY or key != SEED_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing seed key")

    created = []
    for acc in DEMO_ACCOUNTS:
        existing = db.query(User).filter(User.email == acc["email"]).first()
        if existing:
            continue
        user = User(
            email=acc["email"],
            hashed_password=hash_password(acc["password"]),
            role=acc["role"],
        )
        db.add(user)
        created.append(acc["email"])

    db.commit()
    return {
        "created": created,
        "message": "Demo accounts ready" if created else "Demo accounts already existed",
    }

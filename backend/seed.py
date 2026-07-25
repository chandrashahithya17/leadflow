"""Run once (locally or via Render's shell) to create the two evaluator
accounts referenced in the README: an admin and a member.

    python seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, Base, engine
from app.models import User, Role
from app.auth import hash_password

Base.metadata.create_all(bind=engine)

ACCOUNTS = [
    {"email": "admin@leadflow.demo", "password": "AdminPass123!", "role": Role.admin},
    {"email": "member@leadflow.demo", "password": "MemberPass123!", "role": Role.member},
]


def seed():
    db = SessionLocal()
    try:
        for acc in ACCOUNTS:
            existing = db.query(User).filter(User.email == acc["email"]).first()
            if existing:
                print(f"skip (exists): {acc['email']}")
                continue
            user = User(
                email=acc["email"],
                hashed_password=hash_password(acc["password"]),
                role=acc["role"],
            )
            db.add(user)
            print(f"created: {acc['email']} ({acc['role'].value})")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()

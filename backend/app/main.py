import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import auth, leads, users, admin
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeadFlow API",
    description="Lead management API for a small sales team — public capture, "
                 "role-based authenticated access, lead lifecycle, and an activity trail.",
    version="1.0.0",
)

allowed_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(leads.router)
app.include_router(admin.router


@app.get("/api/health")
def health():
    return {"status": "ok"}

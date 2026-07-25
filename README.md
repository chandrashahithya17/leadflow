# LeadFlow

A lead management app for a small sales team: a public capture form feeds an
authenticated pipeline where reps claim leads, move them through stages, leave
notes, and see a full activity trail.

**Live app:** `TODO — add your deployed frontend URL here`
**API:** `TODO — add your deployed backend URL here`

## Demo credentials

Created by `backend/seed.py`:

| Role   | Email               | Password         |
|--------|---------------------|-------------------|
| Admin  | admin@leadflow.demo | AdminPass123!     |
| Member | member@leadflow.demo| MemberPass123!    |

## Stack

- **Backend:** FastAPI + SQLAlchemy, SQLite locally / Postgres in production, JWT auth, pytest
- **Frontend:** React (Vite), React Router, plain fetch — no state library needed at this size

## Architecture & data model

```
User        (id, email, hashed_password, role[admin|member])
Lead        (id, name, email, phone, company, message, status, assigned_to_id, created_at, updated_at)
Note        (id, lead_id, author_id, content, created_at)
Activity    (id, lead_id, actor_id, action, detail, created_at)   -- audit trail
```

A `Lead` has many `Note`s and many `Activity` entries. Every state-changing
action on a lead (created, assigned, status changed, note added) writes an
`Activity` row — that's the audit trail the task calls for.

**Status pipeline:** `new → contacted → qualified → won` (or `lost` at any point).

**Permission model** (enforced server-side in `backend/app/routers/leads.py`,
mirrored in the UI for a good experience — the UI checks are never the real gate):

- Anyone (no auth) can submit a lead via the public form.
- Any authenticated user (admin or member) can view all leads and add notes.
- **Assignment:** admins can assign any lead to anyone. Members can only claim
  an *unassigned* lead for themselves — they cannot reassign a lead someone
  else already owns.
- **Status changes:** admins can change the status of any lead. Members can
  only change the status of leads currently assigned to them.
- **User management:** only admins can create new team accounts (`POST /api/users`).

## Running locally

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # defaults are fine for local dev
python seed.py                # creates the two demo accounts
uvicorn app.main:app --reload --port 8000
```

API docs (Swagger UI) are then live at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # VITE_API_URL=http://localhost:8000
npm run dev
```

Visit `http://localhost:5173`.

### Tests

```bash
cd backend
pytest -v
```

Covers: login success/failure, unauthenticated access rejection, admin-only
endpoint enforcement, the public-capture-to-visible-lead flow, and the full
lead lifecycle flow (claim → status change → note → activity trail), plus the
assignment/status permission rules for members vs. admins, pagination, and
filtering.

## Deploying (free tier)

**Backend → Render**

1. Push this repo to GitHub.
2. In Render, "New +" → "Blueprint", point it at the repo — `render.yaml` at
   the root defines the web service and a free Postgres database.
3. After the first deploy, open the Render shell for the service and run
   `python seed.py` to create the demo accounts against the real database.
4. Note the backend's `.onrender.com` URL.

**Frontend → Vercel**

1. Import the repo in Vercel, set the root directory to `frontend`.
2. Add an environment variable `VITE_API_URL` = your Render backend URL.
3. Deploy. Then go back to the Render service and update `FRONTEND_ORIGIN` to
   the Vercel URL so CORS allows it.

## API reference

Base path: `/api`. All authenticated endpoints expect
`Authorization: Bearer <token>`. Interactive docs (always up to date with the
code) are served at `/docs`.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/login` | none | `{ email, password }` → `{ access_token, user }`. `401` on bad credentials. |
| GET | `/api/auth/me` | required | Returns the current user. `401` if token missing/invalid. |

### Users

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/users` | required | List team members (used to populate assignment dropdowns). |
| POST | `/api/users` | admin | Create a new team member. `409` if email is taken, `403` if caller isn't admin. |

### Leads

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/api/leads/public` | none | Public capture form submission. `422` on invalid payload (e.g. bad email). |
| GET | `/api/leads` | required | Paginated, filterable list. Query params: `status`, `assigned_to_id`, `search`, `page` (default 1), `page_size` (default 20, max 100). Returns `{ items, total, page, page_size, pages }`. |
| GET | `/api/leads/{id}` | required | Full lead detail including notes and activity trail. `404` if not found. |
| PATCH | `/api/leads/{id}` | required | Update `status` and/or `assigned_to_id`. `403` if the caller's role doesn't permit the change (see permission model above). `404` if lead doesn't exist. |
| POST | `/api/leads/{id}/notes` | required | Add a timestamped note. `404` if lead doesn't exist. |

### Status codes used throughout

`200` success · `201` created · `400` bad input reference (e.g. assigning to a
nonexistent user) · `401` missing/invalid auth · `403` authenticated but not
permitted · `404` not found · `409` conflict (duplicate email) · `422`
validation error (FastAPI/Pydantic, e.g. malformed email or missing field).

---

Built for [Digital Heroes Training Task](https://digitalheroesco.com).

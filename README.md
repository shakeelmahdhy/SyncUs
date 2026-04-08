SyncUs is a skill-matching platform with a React frontend and a FastAPI backend.

## Technologies used

- Frontend: React, Vite, TypeScript
- Styling/UI: Tailwind CSS, shadcn/ui
- Backend: FastAPI, Pydantic, SQLAlchemy
- Platform/DB: Supabase (Postgres + Auth)
- Caching (planned): Redis
- Resume ingestion (planned): PDF/OCR parser service

## Project structure

```txt
SyncUs/
├── frontend/          # React + Vite app (talks to backend APIs)
│   └── src/
│       └── features/
│           ├── matching/{components,hooks}
│           ├── profile/{components,hooks}
│           └── jd/{components,hooks}
├── backend/           # FastAPI app (owns business logic + Supabase access)
│   └── app/
│       ├── api/       # HTTP routes (auth, users, jobs, matches)
│       ├── engine/    # 60/30/10 matching logic
│       │   ├── vectorizer.py   # Converts profiles/JDs into comparable vectors
│       │   ├── scorer.py       # Applies weighted scoring (Skill 60, Edu 30, Exp 10)
│       │   ├── ranker.py       # Produces Top-K matches (SQL LIMIT or heap strategy)
│       │   └── normalizer.py   # Maps synonyms/taxonomy terms into canonical skills
│       ├── services/
│       │   ├── resume_parser/  # Extracts skills/text from uploaded resumes (PDF/OCR)
│       │   └── cache/          # Redis cache helpers for fast match dashboard refresh
│       ├── models.py           # SQLAlchemy ORM models for tables/relationships
│       └── schemas.py          # Pydantic request/response models for API contracts
├── infra/             # Supabase migrations/config + Docker files
├── node_modules/
└── README.md
```

Supabase should be integrated through the backend (server-to-server), while the frontend consumes backend endpoints.

## Prerequisites

- Node.js 18+ and npm
- Python 3.11+ (recommended for FastAPI)

## Run frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Default Vite URL is usually `http://localhost:5173`.

## Run backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

Backend health check: `http://localhost:8000/health`  
API docs: `http://localhost:8000/docs`

## Suggested next setup

- Add backend dependency management (`requirements.txt` or `pyproject.toml`)
- Add `docker-compose.yml` for local PostgreSQL + Redis
- Add `.env.example` files for `frontend` and `backend`

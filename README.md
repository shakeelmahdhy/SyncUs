# SyncUs

SyncUs is an intelligent job matching platform with a FastAPI backend, a Supabase database/auth backend, and a Vite React frontend prototype.

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm
- A Supabase project, or a local Supabase instance with the project schema applied

## 1. Clone And Install

```bash
git clone https://github.com/shakeelmahdhy/SyncUs.git
cd SyncUs
```

Create a Python virtual environment and install backend dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

## 2. Configure Environment Variables

Create `backend/.env` locally. Do not commit this file.

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
FRONTEND_URL=http://localhost:5173
DEBUG=true
```

Notes:

- `SUPABASE_URL` and `SUPABASE_KEY` are required by the backend.
- Use a key appropriate for your local development setup.
- If a secret key was ever committed, rotate it in Supabase.
- `.env`, `node_modules`, `dist`, and Python cache files are ignored by Git.

## 3. Prepare Supabase

Apply the database schema/migrations in your Supabase project before using backend endpoints that read or write data.

Relevant schema files are in:

```bash
backend/app/modules/jobs/schema.sql
```

The backend expects Supabase tables for jobs, users/profiles, matching, and tracking depending on which module you use.

## 4. Run The Backend

From the repository root:

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

Check that the backend is running:

```bash
curl http://localhost:8000/health
```

API docs are available at:

```text
http://localhost:8000/api/docs
```

Current backend main app route note:

- `backend/app/main.py` currently includes the jobs router.
- Jobs endpoints are mounted under `/skill-sync/v1/jobs`.

Example:

```text
GET http://localhost:8000/skill-sync/v1/jobs
```

## 5. Run The Frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```text
http://localhost:5173
```

Build the frontend for production:

```bash
cd frontend
npm run build
```

Preview a production build:

```bash
cd frontend
npm run preview
```

## 6. Matching Module

The matching module has its own standalone FastAPI entrypoint:

```bash
cd backend/app
PYTHONPATH=. uvicorn modules.matching.main:app --reload --port 8001
```

Matching routes are mounted under:

```text
/sync-us/v1/matching
```

Examples:

```text
GET  http://localhost:8001/sync-us/v1/matching/recommendations?user_id=<candidate-id>
GET  http://localhost:8001/sync-us/v1/matching/jobs/<job-id>/candidates
POST http://localhost:8001/sync-us/v1/matching/recompute?user_id=<candidate-id>
```

## 7. Verification Commands

Backend syntax check:

```bash
cd backend
python -m compileall app
```

Backend tests, if test files are present in your branch:

```bash
cd backend
python -m pytest
```

Frontend typecheck and build:

```bash
cd frontend
npm run build
```

## 8. Common Issues

### Backend says Supabase configuration is missing

Check that `backend/.env` exists and contains `SUPABASE_URL` and `SUPABASE_KEY`. Restart the backend after changing `.env`.

### Frontend opens but data is empty

The prototype can render without live data. Backend-backed workflows require Supabase tables and rows such as employers, job seekers, jobs, applications, and matches.

### GitHub blocks push because of a secret

Removing a secret from the current file is not enough if it exists in commit history. Rewrite the unpushed commit history to remove the secret, add/confirm `.gitignore`, then rotate the exposed key in Supabase.

### Do not commit generated files

Do not commit:

- `backend/.env`
- `.venv/`
- `__pycache__/`
- `frontend/node_modules/`
- `frontend/dist/`
- `.DS_Store`

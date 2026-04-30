# Python virtual environment (backend)

Create and use a virtual environment from the repo root (`SyncUs/`) before installing Python dependencies.

## 1) Create the env (if it doesn't exist)

```bash
cd backend
python -m venv .venv
```

## 2) Activate it

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

## 3) Install dependencies (example)

```bash
pip install --upgrade pip
pip install fastapi uvicorn supabase
```

If you added a pinned dependency list for the project, prefer:

```bash
pip install -r requirements.txt
```

Your repo includes `backend/requirements.txt`.

Official FastAPI install guide:
- https://fastapi.tiangolo.com/installation/


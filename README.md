# Cooking Agent

A simple cooking assistant prototype: the user enters a dish name or ingredients, the backend searches for recipe sources, and the frontend displays the dish information and steps.

## Structure

- backend: FastAPI backend
- frontend: Vite + React frontend

## Backend startup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend startup

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

## Access

- Backend: http://127.0.0.1:8000/health
- Frontend: http://127.0.0.1:5173

## Current status

This is an MVP skeleton with a demo data path by default. You can later connect real third-party recipe APIs and AI services.

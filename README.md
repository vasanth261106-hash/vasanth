# PocketSmart AI

A complete FastAPI + Jinja2 + SQLite + Gemini implementation based on the supplied PocketSmart AI project document.

## Features
- PocketSmart branded landing page
- Register / Login / Logout
- User dashboard and recommendation history
- Home Interior Budget Planner
- Party Budget Planner
- Jewelry Budget Planner with optional outfit image upload
- Recommendation result pages
- Testimonials page
- FastAPI routes: /generate-home, /generate-party, /generate-jewelry, /register, /login, /logout, /token, /session-info, /session-data, /history, /startup
- SQLite storage
- Gemini integration when GEMINI_API_KEY is configured
- Built-in fallback recommendations so the application can be tested without Gemini

## Run on Windows PowerShell
```powershell
cd C:\PocketSmartAI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn backend.app:app --reload
```
Open http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

## Gemini
Open `.env` and set `GEMINI_API_KEY=...`. The default model is `gemini-1.5-flash`; change `GEMINI_MODEL` if your Google AI account exposes a different model.

## Important
Do not type the PowerShell prompt itself. If the terminal displays `(.venv) PS C:\PocketSmartAI>`, type only the command after `>`.

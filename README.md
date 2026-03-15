# JOB-Verse

JOB-Verse is a job simulation and preparation platform with role-play workflows, task simulations, interview prep, and now a dedicated AI-powered job search module.

## What is integrated

- Main experience (HTML/CSS/JS): `JOB-Verse/12-45 backup with motion detection py/Job-simulator`
- Agentic module (Streamlit): `Agentic_Job_Search-main`
- Dashboard integration: Clicking **Job Finder** in the main dashboard now opens the Streamlit app at `http://localhost:8501`.

## Seamless integration flow

1. User logs into JOB-Verse dashboard.
2. User clicks **Job Finder** from the sidebar.
3. Browser redirects directly to the Agentic Streamlit app (`http://localhost:8501`).
4. User continues advanced AI job discovery and career tooling there.

## Run instructions

### 1) Start JOB-Verse (main web app)

Open and run from:
- `JOB-Verse/12-45 backup with motion detection py/Job-simulator`

Use your existing workflow to host/open `index.html` and reach the dashboard.

### 2) Start Agentic Job Search module (Streamlit)

From PowerShell inside `JOB-Verse` root, run:

```powershell
.\launch_agentic_job_search.ps1
```

This launcher starts:

```powershell
streamlit run app.py
```

inside `Agentic_Job_Search-main`.

## First-time setup for Streamlit module

From `Agentic_Job_Search-main`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then run:

```powershell
streamlit run app.py
```

## Tech stack

- Frontend: HTML, CSS, JavaScript
- Backend services: Firebase
- AI module: Python, Streamlit, LangChain, Groq/Gemini integrations

## Notes

- If clicking **Job Finder** does not open the module, confirm Streamlit is running on `http://localhost:8501`.
- You can change the integration URL in `dashboard.js` if you host Streamlit on a different port.

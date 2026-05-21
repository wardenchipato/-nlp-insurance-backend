# System Insurance — running the app

The project has three runnable pieces:

| Part | Role | Default URL |
|------|------|-------------|
| **Backend API** | FastAPI (`uvicorn`), REST + WebSockets | [http://localhost:8000](http://localhost:8000) |
| **KB admin UI** | Vite + React for knowledge-base admin (dev server proxies to the API) | [http://localhost:3002/admin/](http://localhost:3002/admin/) |
| **Main frontend** | Create React App — policyholder assessment UI | [http://localhost:3000](http://localhost:3000) |

The main app calls the API at `http://127.0.0.1:8000` unless you set `REACT_APP_API_URL`.

---

## First-time setup

**Backend (Python)**

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Node (both UIs)**

```powershell
cd frontend
npm install

cd ..\backend\kb-admin
npm install
```

---

## Launch everything (recommended on Windows)

**Terminal 1 — API + KB admin (network stack script)**

From the repo root:

```powershell
cd backend
.\run_stack.ps1
```

This script:

1. Starts the API with **uvicorn** on **port 8000** (`app.api_main:app`, `--reload`, `--host 0.0.0.0`).
2. After a short pause, starts the KB admin dev server with **`npm run dev`** in `backend\kb-admin` (**port 3002**).

Requirements: `backend\venv` must exist with dependencies installed; `kb-admin` must have `npm install` done.

**Terminal 2 — main UI**

```powershell
cd frontend
npm start
```

Open [http://localhost:3000](http://localhost:3000) for the assessment UI. Keep the API running on 8000 so requests succeed.

---

## Launch each part manually

Use separate terminals if you prefer not to use `run_stack.ps1`.

1. **Backend API**

   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   uvicorn app.api_main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **KB admin UI**

   ```powershell
   cd backend\kb-admin
   npm run dev
   ```

   Dev server: [http://localhost:3002/admin/](http://localhost:3002/admin/) (Vite proxies `/api` and `/ws` to port 8000).

3. **Main frontend**

   ```powershell
   cd frontend
   npm start
   ```

---

## KB admin served from the API (production-style)

After `npm run build` in `backend\kb-admin`, the API can serve the built admin at **[/admin/](http://localhost:8000/admin/)** when `kb-admin/dist` exists. You do not need the Vite dev server on 3002 for that.

---

## Troubleshooting

- **“Could not reach the API”** in the main UI: start uvicorn on port **8000** first.
- **`run_stack.ps1` errors on venv**: create and populate `backend\venv` as in first-time setup.
- **Port already in use**: stop other apps on 3000, 3002, or 8000, or change ports in `frontend` (e.g. `set PORT=3001` before `npm start`), `kb-admin/package.json` / `vite.config.js`, and uvicorn `--port`.

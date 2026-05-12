# Starts API (port 8000) and knowledge-base admin Vite dev server (port 3002) together.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$uvicorn = Join-Path $here "venv\Scripts\uvicorn.exe"
if (-not (Test-Path $uvicorn)) {
    Write-Error "venv not found. Create venv and pip install -r requirements.txt"
    exit 1
}

Start-Process -WorkingDirectory $here -FilePath $uvicorn -ArgumentList @(
    "app.api_main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
)

Start-Sleep -Seconds 2
$kb = Join-Path $here "kb-admin"
if (Test-Path (Join-Path $kb "package.json")) {
    Start-Process -WorkingDirectory $kb -FilePath "npm" -ArgumentList @("run", "dev")
}

Write-Host "API: http://localhost:8000  (knowledge-base UI build: http://localhost:8000/admin/ after npm run build in kb-admin)"
Write-Host "KB admin dev (proxy): http://localhost:3002/admin/"

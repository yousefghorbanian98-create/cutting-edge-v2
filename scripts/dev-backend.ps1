# Cutting Edge v2 — start the AI engine backend on Windows.
#
# Boots the FastAPI app as the installed `ai_engine` package:
#     python -m uvicorn ai_engine.main:app
#
# Env overrides (set before invoking):
#   $env:CE_VENV_DIR   venv directory        (default: ai-engine\.venv)
#   $env:CE_HOST       bind host             (default: 127.0.0.1)
#   $env:CE_PORT       bind port             (default: 8001)
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir
$AiDir     = Join-Path $RepoRoot "ai-engine"
$VenvDir   = if ($env:CE_VENV_DIR) { $env:CE_VENV_DIR } else { Join-Path $AiDir ".venv" }
$Host      = if ($env:CE_HOST) { $env:CE_HOST } else { "127.0.0.1" }
$Port      = if ($env:CE_PORT) { $env:CE_PORT } else { "8001" }

Set-Location $AiDir

# 1. Create the venv if needed.
if (-not (Test-Path (Join-Path $VenvDir "Scripts\python.exe"))) {
    Write-Host "[dev-backend] Creating virtualenv at $VenvDir"
    python -m venv $VenvDir
}

$Python = Join-Path $VenvDir "Scripts\python.exe"

# 2. Bootstrapping: make sure the package and its web deps are importable.
$ImportCheck = & $Python -c "import ai_engine.main, uvicorn, fastapi, psutil, requests" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[dev-backend] Installing web deps + editable package into $VenvDir"
    & $Python -m pip install --quiet --upgrade pip
    & $Python -m pip install --quiet `
        "fastapi==0.115.6" "uvicorn[standard]==0.32.1" "python-multipart==0.0.18" `
        "pydantic==2.10.4" "python-dotenv==1.0.1" "psutil==6.1.0" "requests==2.32.3"
    & $Python -m pip install --quiet --no-deps -e .
}

# 3. Run.
Write-Host "[dev-backend] Starting backend on $Host`:$Port"
& $Python -m uvicorn ai_engine.main:app --host $Host --port $Port

# Astro — start the local server.
#   .\run.ps1            start on http://127.0.0.1:8600
#   .\run.ps1 -Port 9000 start on another port

param(
    [int]$Port = 8600,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "Virtual environment missing. Creating it now..." -ForegroundColor Yellow
    python -m venv (Join-Path $root ".venv")
    & $python -m pip install --upgrade pip
    & $python -m pip install -r (Join-Path $root "requirements.txt")
}

Write-Host ""
Write-Host "  Astro  ->  http://127.0.0.1:$Port" -ForegroundColor Cyan
Write-Host "  Everything runs locally. Ctrl+C to stop." -ForegroundColor DarkGray
Write-Host ""

if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 3
        Start-Process "http://127.0.0.1:$using:Port"
    } | Out-Null
}

Set-Location $root
& $python -m uvicorn app.main:app --host 127.0.0.1 --port $Port

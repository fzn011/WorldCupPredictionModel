<#
.SYNOPSIS
    Clear Python bytecode caches and launch the Streamlit app.

.DESCRIPTION
    Removes all __pycache__ directories and .pyc/.pyo files under the project
    root, then starts the Streamlit app.  Run this instead of calling Streamlit
    directly whenever you hit a stale-cache import error.

.EXAMPLE
    .\run.ps1
#>

Set-Location $PSScriptRoot

# ----- 1. Find the virtual-environment Python --------------------------------
$PythonCandidates = @(
    ".\.venv\Scripts\python.exe",
    "python"
)
$Python = $null
foreach ($candidate in $PythonCandidates) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $Python = $candidate
        break
    }
}
if (-not $Python) {
    Write-Error "Python not found. Activate your virtual environment first."
    exit 1
}

# ----- 2. Clear stale bytecode cache ----------------------------------------
Write-Host "Clearing __pycache__ and .pyc files..." -ForegroundColor Cyan

Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory `
    | Where-Object { $_.FullName -notmatch "\\.venv\\" } `
    | Remove-Item -Recurse -Force

Get-ChildItem -Path . -Recurse -Include "*.pyc", "*.pyo" `
    | Where-Object { $_.FullName -notmatch "\\.venv\\" } `
    | Remove-Item -Force

Write-Host "Cache cleared." -ForegroundColor Green

# ----- 3. Start Streamlit ----------------------------------------------------
Write-Host "Starting Streamlit app..." -ForegroundColor Cyan
& $Python -m streamlit run app/streamlit_app.py

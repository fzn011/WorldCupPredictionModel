# Reset local repo to match GitHub main (Windows).
# Run from project root in PowerShell:
#   powershell -ExecutionPolicy Bypass -File scripts/sync_from_github.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "Stashing local changes (backup)..."
git stash push -u -m "sync backup $(Get-Date -Format 'yyyy-MM-dd HH:mm')"

Write-Host "Fetching origin/main..."
git fetch origin main
git checkout main
git reset --hard origin/main

Write-Host "Running tests..."
python -m pytest tests/test_streamlit_paths.py tests/test_player_awards.py -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Done. Start Streamlit with:"
Write-Host "  python -m streamlit run app/streamlit_app.py"

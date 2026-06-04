param(
    [string]$ApiHost = "127.0.0.1",
    [int]$Port = 8000,
    [bool]$Reload = $true,
    [switch]$NoRun
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = "e:\World Cup prediction model\.venv\Scripts\python.exe"

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found at '$PythonExe'. Make sure the .venv exists."
}

Set-Location $ProjectRoot

$UvicornArgs = @("-m", "uvicorn", "api.main:app", "--host", $ApiHost, "--port", "$Port")
if ($Reload) {
    $UvicornArgs += "--reload"
}

Write-Host "Starting API from: $ProjectRoot"
Write-Host "Command: $PythonExe $($UvicornArgs -join ' ')"

if ($NoRun) {
    Write-Host "NoRun enabled; command not executed."
    exit 0
}

& $PythonExe @UvicornArgs

# Run API with auto-reload (APP_ENV=development → app.main enables uvicorn reload).
$ErrorActionPreference = "Stop"
$env:APP_ENV = "development"
Set-Location (Join-Path $PSScriptRoot "..")
python -m app.main

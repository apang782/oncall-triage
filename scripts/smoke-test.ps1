# Quick local checks (no API). From plugin root:
#   powershell -File scripts/smoke-test.ps1

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

Write-Host "== oncall-triage smoke test ==" -ForegroundColor Cyan
Write-Host "Plugin root: $root"

python -m py_compile (Join-Path $root "mcp-servers\mock-observability\server.py")
python -m py_compile (Join-Path $root "scripts\pre_tool_guard.py")
Write-Host "[ok] Python syntax" -ForegroundColor Green

$blockIn = '{"tool_input":{"command":"kubectl delete pod test"}}'
$blockIn | python (Join-Path $root "scripts\pre_tool_guard.py")
if ($LASTEXITCODE -ne 2) { throw "Expected exit 2 for kubectl delete, got $LASTEXITCODE" }
Write-Host "[ok] Hook blocks kubectl delete" -ForegroundColor Green

$allowIn = '{"tool_input":{"command":"kubectl get pods -n prod-acme"}}'
$allowIn | python (Join-Path $root "scripts\pre_tool_guard.py")
if ($LASTEXITCODE -gt 1) { throw "Expected exit 0 or 1 for kubectl get, got $LASTEXITCODE" }
Write-Host "[ok] Hook allows kubectl get" -ForegroundColor Green

$claude = Join-Path $env:USERPROFILE ".local\bin\claude.exe"
if (-not (Test-Path $claude)) { $claude = "claude" }
Push-Location $root
& $claude plugin validate . --strict
if ($LASTEXITCODE -ne 0) { throw "plugin validate failed" }
Pop-Location
Write-Host "[ok] claude plugin validate --strict" -ForegroundColor Green

Write-Host ""
Write-Host "Next (requires: claude login):" -ForegroundColor Yellow
Write-Host "  claude --plugin-dir `"$root`""
Write-Host "  /oncall-triage:incident-triage"

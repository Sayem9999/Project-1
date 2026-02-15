# Full-Stack Workspace Sync Script (Hardcoded)
# This script mirrors the entire ProEdit Suite codebase across workspaces.
$ErrorActionPreference = "Continue"

$Source = "C:\Users\Sayem\Downloads\New folder\Project-1-1"
$Dest = "C:\pinokio\api\editstudio"

Write-Host "🚀 FULL-STACK SYNC: MIRRORING CODEBASE..." -ForegroundColor Cyan

# Define Exclusions (Directories and Files that should NOT be mirrored)
$ExcludeDirs = @(
    ".git", 
    "node_modules", 
    ".venv", 
    "storage", 
    "logs", 
    "tmp", 
    ".next", 
    ".ruff_cache", 
    ".mypy_cache",
    "__pycache__"
)

$ExcludeFiles = @(
    "*.log",
    "edit_ai.db",   # Don't overwrite the active database
    "*.pyc",
    "*.pyo"
)

# Robocopy Command:
# /MIR  - Mirror directory tree (Delete files in dest that don't exist in source)
# /XD   - Exclude Directories
# /XF   - Exclude Files
# /R:1  - Retry once
# /W:1  - Wait 1 sec
# /V    - Verbose (useful for logging)
# /NFL  - No File List (keep output clean)
# /NDL  - No Directory List

$robocopyArgs = @(
    "$Source",
    "$Dest",
    "/MIR",
    "/XD"
) + $ExcludeDirs + @("/XF") + $ExcludeFiles + @("/R:1", "/W:1", "/NFL", "/NDL", "/NJH", "/NJS")

Write-Host "  > Source: $Source" -ForegroundColor Gray
Write-Host "  > Target: $Dest" -ForegroundColor Gray

# Execute Robocopy
& robocopy @robocopyArgs

if ($LASTEXITCODE -lt 8) {
    Write-Host "✅ FULL-STACK SYNC COMPLETE: Codebase, Frontend, and Backend aligned." -ForegroundColor Green
}
else {
    Write-Host "⚠️ Warning: Sync encountered some locked files. Check if the app is running." -ForegroundColor Yellow
}

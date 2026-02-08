$ROOT_DIR = Resolve-Path "$PSScriptRoot\.."
$PID_DIR = "$ROOT_DIR\.runtime\pids"

foreach ($svc in @("backend", "frontend")) {
    $pidFile = "$PID_DIR\$svc.pid"
    if (Test-Path $pidFile) {
        $id = Get-Content $pidFile
        try {
            Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped $svc ($id)"
        } catch {
            Write-Host "Could not stop $svc ($id) - might be already stopped"
        }
        Remove-Item $pidFile -ErrorAction SilentlyContinue
    }
}

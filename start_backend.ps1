$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$Port = 8010
$ExistingListeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

foreach ($Listener in $ExistingListeners) {
    $Process = Get-CimInstance Win32_Process -Filter "ProcessId = $($Listener.OwningProcess)" -ErrorAction SilentlyContinue
    if ($Process -and $Process.CommandLine -like "*uvicorn*api:app*") {
        Write-Host "Stopping old backend process $($Listener.OwningProcess) on port $Port..."
        Stop-Process -Id $Listener.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

& "$ProjectRoot\.venv\Scripts\python.exe" -m uvicorn api:app --host 127.0.0.1 --port $Port

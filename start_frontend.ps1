$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$FrontendRoot = Join-Path $ProjectRoot "frontend"

$env:Path = "C:\Program Files\nodejs;$env:Path"
$env:VITE_API_BASE = "http://127.0.0.1:8010"
Set-Location $FrontendRoot

npm run dev

$ErrorActionPreference = 'Stop'
$backend = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$recordPath = Join-Path $backend '.local/api.process.json'
if (-not (Test-Path -LiteralPath $recordPath)) { Write-Output 'No managed API record.'; exit 0 }
$record = Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
$process = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
if (-not $process) { Write-Output 'Managed API is already stopped.'; exit 0 }
if ($process.StartTime.ToUniversalTime().Ticks.ToString() -ne $record.startedTicks) {
    throw 'The recorded process ID was reused; refusing to stop anything.'
}
$details = Get-CimInstance Win32_Process -Filter "ProcessId=$($record.pid)"
if (-not $details.CommandLine.Contains($backend) -or -not $details.CommandLine.Contains('uvicorn')) {
    throw 'Process identity does not match this backend; refusing to stop anything.'
}
& taskkill.exe /PID $record.pid /T /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not stop the managed API.' }
Write-Output 'Stopped this backend API. PostgreSQL remains running.'

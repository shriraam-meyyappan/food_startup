[CmdletBinding()]
param([ValidateRange(1024, 65535)][int]$Port = 8000)
$ErrorActionPreference = 'Stop'
$backend = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$python = Join-Path $backend '.venv/Scripts/python.exe'
$local = Join-Path $backend '.local'
$recordPath = Join-Path $local 'api.process.json'
if (-not (Test-Path -LiteralPath $python)) { throw 'Install the backend virtual environment first.' }
New-Item -ItemType Directory -Force -Path $local | Out-Null
if (Test-Path -LiteralPath $recordPath) {
    $record = Get-Content -Raw -LiteralPath $recordPath | ConvertFrom-Json
    $existing = Get-Process -Id $record.pid -ErrorAction SilentlyContinue
    if ($existing -and $existing.StartTime.ToUniversalTime().Ticks.ToString() -eq $record.startedTicks) {
        Write-Output "Managed API already running at http://127.0.0.1:$($record.port)/docs"
        exit 0
    }
}
$listener = [Net.Sockets.TcpClient]::new()
try {
    try { $listener.Connect('127.0.0.1', $Port) } catch { }
    if ($listener.Connected) { throw "Port $Port is already in use. No existing process was stopped. Choose another -Port." }
} finally { $listener.Dispose() }
$stamp = Get-Date -Format 'yyyyMMdd-HHmmssfff'
$stdout = Join-Path $local "api-$stamp.stdout.log"
$stderr = Join-Path $local "api-$stamp.stderr.log"
$process = Start-Process -FilePath $python -ArgumentList @(
    '-m', 'uvicorn', 'app.main:app', '--app-dir', ('"' + $backend + '"'),
    '--host', '127.0.0.1', '--port', $Port.ToString(), '--no-proxy-headers'
) -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
@{ pid = $process.Id; port = $Port; startedTicks = $process.StartTime.ToUniversalTime().Ticks.ToString(); stdout = $stdout; stderr = $stderr } |
    ConvertTo-Json | Set-Content -LiteralPath $recordPath -Encoding utf8
$watch = [Diagnostics.Stopwatch]::StartNew()
while ($watch.Elapsed.TotalSeconds -lt 30) {
    $process.Refresh()
    if ($process.HasExited) { throw "API exited. Check $stderr" }
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/v1/health" -TimeoutSec 1
        if ($health.status -eq 'ok') {
            Write-Output "API started at http://127.0.0.1:$Port/docs"
            exit 0
        }
    } catch { }
    Start-Sleep -Milliseconds 250
}
throw "API startup timed out. Check $stderr"

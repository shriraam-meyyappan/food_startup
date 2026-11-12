# Local portable installation created during Phase 4; no Windows service.
$ErrorActionPreference = 'Stop'
$pgBin = Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql-17/pgsql/bin'
$pgData = Join-Path $env:LOCALAPPDATA 'DailyDabba/pgdata17'
if (-not (Test-Path (Join-Path $pgBin 'pg_ctl.exe'))) {
    throw 'Portable PostgreSQL is not installed here. See docs/database-setup.md for Docker or installer setup.'
}
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData status
if ($LASTEXITCODE -eq 0) { exit 0 }
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -l (Join-Path $pgData 'server.log') -w start
exit $LASTEXITCODE

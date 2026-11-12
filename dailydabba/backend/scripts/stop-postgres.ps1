$ErrorActionPreference = 'Stop'
$pgBin = Join-Path $env:LOCALAPPDATA 'DailyDabba/postgresql-17/pgsql/bin'
$pgData = Join-Path $env:LOCALAPPDATA 'DailyDabba/pgdata17'
& (Join-Path $pgBin 'pg_ctl.exe') -D $pgData -m fast -w stop
exit $LASTEXITCODE

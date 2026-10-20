param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$taskLocal = Join-Path $taskRoot '.local'
New-Item -ItemType Directory -Force -Path $taskLocal | Out-Null
$taskPython = Join-Path $taskRoot 'backend\.venv\Scripts\python.exe'
$taskVite = Join-Path $taskRoot 'frontend\node_modules\vite\bin\vite.js'
if (!(Test-Path -LiteralPath $taskPython) -or !(Test-Path -LiteralPath $taskVite)) {
    throw 'Faltan dependencias. Sigue la instalación del README antes de iniciar.'
}
function Test-LocalPort([int]$Port) {
    $taskSocket = [System.Net.Sockets.TcpClient]::new()
    try { return $taskSocket.ConnectAsync('127.0.0.1', $Port).Wait(700) -and $taskSocket.Connected }
    catch { return $false }
    finally { $taskSocket.Dispose() }
}
$taskPgCtl = Join-Path $taskLocal 'postgresql\pgsql\bin\pg_ctl.exe'
$taskPgData = Join-Path $taskLocal 'pgdata'
if (!(Test-LocalPort 5432) -and (Test-Path -LiteralPath $taskPgCtl) -and
    (Test-Path -LiteralPath (Join-Path $taskPgData 'PG_VERSION'))) {
    Start-Process -FilePath $taskPgCtl -ArgumentList @('-D', ('"' + $taskPgData + '"'),
        '-l', ('"' + (Join-Path $taskLocal 'postgresql.log') + '"'),
        '-o', '"-h 127.0.0.1 -p 5432"', '-w', 'start') -WindowStyle Hidden -Wait
}
if (!(Test-LocalPort 5432)) { throw 'Inicia PostgreSQL (docker compose up -d postgres) y configura backend/.env.' }
if (!(Test-Path -LiteralPath (Join-Path $taskRoot 'backend\.env'))) { throw 'Configura backend/.env siguiendo el README.' }
Push-Location (Join-Path $taskRoot 'backend')
try {
    & $taskPython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar las migraciones.' }
    & $taskPython -m app.infrastructure.seed_catalog
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo cargar el catálogo.' }
} finally { Pop-Location }
$env:DATA_MODE = 'postgres'
if (!(Test-LocalPort 8000)) {
    Start-Process -FilePath $taskPython -ArgumentList @('-m', 'uvicorn', 'app.infrastructure.main:app',
        '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $taskRoot 'backend') `
        -RedirectStandardOutput (Join-Path $taskLocal 'api.out.log') `
        -RedirectStandardError (Join-Path $taskLocal 'api.err.log') -WindowStyle Hidden
}
if (!(Test-LocalPort 5173)) {
    Start-Process -FilePath 'node' -ArgumentList @(('"' + $taskVite + '"'), '--host', '127.0.0.1', '--port', '5173') `
        -WorkingDirectory (Join-Path $taskRoot 'frontend') `
        -RedirectStandardOutput (Join-Path $taskLocal 'frontend.out.log') `
        -RedirectStandardError (Join-Path $taskLocal 'frontend.err.log') -WindowStyle Hidden
}
Write-Host 'ORIENTA: http://127.0.0.1:5173 | API: http://127.0.0.1:8000/docs'
Write-Host 'Logs locales: .local/api.err.log y .local/frontend.err.log'
if (!$NoBrowser) { Start-Process 'http://127.0.0.1:5173' }

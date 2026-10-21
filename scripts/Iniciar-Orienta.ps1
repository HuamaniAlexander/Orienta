param([switch]$SinNavegador)
$ErrorActionPreference = 'Stop'
$raizProyecto = Split-Path $PSScriptRoot -Parent
$directorioLocal = Join-Path $raizProyecto '.local'
New-Item -ItemType Directory -Force -Path $directorioLocal | Out-Null
$ejecutablePython = Join-Path $raizProyecto 'backend\.venv\Scripts\python.exe'
$ejecutableVite = Join-Path $raizProyecto 'frontend\node_modules\vite\bin\vite.js'
if (!(Test-Path -LiteralPath $ejecutablePython) -or !(Test-Path -LiteralPath $ejecutableVite)) {
    throw 'Faltan dependencias. Sigue la instalación del README antes de iniciar.'
}
function Probar-PuertoLocal([int]$Puerto) {
    $conexionPuerto = [System.Net.Sockets.TcpClient]::new()
    try { return $conexionPuerto.ConnectAsync('127.0.0.1', $Puerto).Wait(700) -and $conexionPuerto.Connected }
    catch { return $false }
    finally { $conexionPuerto.Dispose() }
}
if (!(Test-Path -LiteralPath (Join-Path $raizProyecto 'backend\.env'))) { throw 'Configura backend/.env siguiendo el README.' }
Push-Location (Join-Path $raizProyecto 'backend')
try {
    $usaPostgresLocal = & $ejecutablePython -c "from sqlalchemy.engine import make_url; from app.infrastructure.configuracion import Configuracion; print(str(make_url(Configuracion().url_base_datos).host in ('localhost', '127.0.0.1', '::1')).lower())"
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo leer la configuración de PostgreSQL.' }
} finally { Pop-Location }
$controlPostgres = Join-Path $directorioLocal 'postgresql\pgsql\bin\pg_ctl.exe'
$datosPostgres = Join-Path $directorioLocal 'pgdata'
if ($usaPostgresLocal -eq 'true' -and !(Probar-PuertoLocal 5432) -and (Test-Path -LiteralPath $controlPostgres) -and
    (Test-Path -LiteralPath (Join-Path $datosPostgres 'PG_VERSION'))) {
    Start-Process -FilePath $controlPostgres -ArgumentList @('-D', ('"' + $datosPostgres + '"'),
        '-l', ('"' + (Join-Path $directorioLocal 'postgresql.log') + '"'),
        '-o', '"-h 127.0.0.1 -p 5432"', '-w', 'start') -WindowStyle Hidden -Wait
}
if ($usaPostgresLocal -eq 'true' -and !(Probar-PuertoLocal 5432)) { throw 'Inicia PostgreSQL (docker compose up -d postgres) y configura backend/.env.' }
Push-Location (Join-Path $raizProyecto 'backend')
try {
    & $ejecutablePython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'No se pudieron aplicar las migraciones.' }
    & $ejecutablePython -m app.infrastructure.cargar_catalogo
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo cargar el catálogo.' }
} finally { Pop-Location }
$env:DATA_MODE = 'postgres'
if (!(Probar-PuertoLocal 8000)) {
    Start-Process -FilePath $ejecutablePython -ArgumentList @('-m', 'uvicorn', 'app.infrastructure.principal:app',
        '--host', '127.0.0.1', '--port', '8000') -WorkingDirectory (Join-Path $raizProyecto 'backend') `
        -RedirectStandardOutput (Join-Path $directorioLocal 'api.out.log') `
        -RedirectStandardError (Join-Path $directorioLocal 'api.err.log') -WindowStyle Hidden
}
if (!(Probar-PuertoLocal 5173)) {
    Start-Process -FilePath 'node' -ArgumentList @(('"' + $ejecutableVite + '"'), '--host', '127.0.0.1', '--port', '5173') `
        -WorkingDirectory (Join-Path $raizProyecto 'frontend') `
        -RedirectStandardOutput (Join-Path $directorioLocal 'frontend.out.log') `
        -RedirectStandardError (Join-Path $directorioLocal 'frontend.err.log') -WindowStyle Hidden
}
Write-Host 'ORIENTA: http://127.0.0.1:5173 | API: http://127.0.0.1:8000/docs'
Write-Host 'Logs locales: .local/api.err.log y .local/frontend.err.log'
if (!$SinNavegador) { Start-Process 'http://127.0.0.1:5173' }

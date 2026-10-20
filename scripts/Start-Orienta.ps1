# Compatibilidad con el comando de inicio anterior.
param([switch]$NoBrowser)
& (Join-Path $PSScriptRoot 'Iniciar-Orienta.ps1') -SinNavegador:$NoBrowser

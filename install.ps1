# Dream Server Root Installer (Windows)
# Delegates to dream-server/install.ps1

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Dream Server Installer" -ForegroundColor Cyan
Write-Host ""

# Check if dream-server directory exists
$DreamServerDir = Join-Path $ScriptDir "dream-server"
if (-not (Test-Path $DreamServerDir)) {
    Write-Host "Error: dream-server directory not found" -ForegroundColor Red
    Write-Host "Expected: $DreamServerDir" -ForegroundColor Red
    exit 1
}

# Delegate to dream-server installer
$DreamServerInstaller = Join-Path $DreamServerDir "install.ps1"
if (-not (Test-Path $DreamServerInstaller)) {
    Write-Host "Error: dream-server installer not found" -ForegroundColor Red
    Write-Host "Expected: $DreamServerInstaller" -ForegroundColor Red
    exit 1
}

# Execute dream-server installer with all passed arguments
& $DreamServerInstaller @RemainingArgs

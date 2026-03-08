# Dream Server Windows Installer (v2.0)
# Main entry point for Windows installations
# Uses native PowerShell installer with full hardware detection

param(
    [switch]$DryRun,
    [switch]$Force,
    [switch]$NonInteractive,
    [string]$Tier = "",
    [switch]$Voice,
    [switch]$Workflows,
    [switch]$Rag,
    [switch]$OpenClaw,
    [switch]$All,
    [switch]$Cloud,
    [string]$SummaryJsonPath = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Source library
. (Join-Path $ScriptDir "installers" "windows" "install-windows.ps1")

# Execute with all passed arguments
& (Join-Path $ScriptDir "installers" "windows" "install-windows.ps1") @PSBoundParameters

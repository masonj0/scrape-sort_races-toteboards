<#
.SYNOPSIS
    Launches the Fortuna Faucet System Tray application.
#>

Write-Host "🚀 Launching Fortuna Faucet in System Tray..." -ForegroundColor Cyan

$VenvPath = ".\\.venv\\Scripts\\pythonw.exe"
$TrayAppPath = ".\\fortuna_tray.py"

if (-not (Test-Path $VenvPath)) {
    Write-Host "❌ ERROR: Virtual environment not found at $VenvPath" -ForegroundColor Red
    Write-Host "Please run INSTALL_FORTUNA.bat first."
    Read-Host "Press Enter to exit"
    exit 1
}

Start-Process -FilePath $VenvPath -ArgumentList $TrayAppPath -WindowStyle Hidden

Write-Host "✅ Fortuna Faucet is now running in your system tray." -ForegroundColor Green
Write-Host "Right-click the icon for options."
Start-Sleep -Seconds 5

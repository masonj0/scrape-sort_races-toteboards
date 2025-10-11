# launcher.ps1
# Enhanced PowerShell launcher for Fortuna Faucet

# --- Configuration ---
$backendPort = 8000
$frontendPort = 3000
$backendDir = "python_service"
$frontendDir = "web_platform\\frontend"

# --- Helper Functions for Color Output ---
function Write-Header {
    param([string]$text)
    Write-Host ("=" * 60) -ForegroundColor Cyan
    Write-Host $text -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Write-Step {
    param([string]$text)
    Write-Host "\\n>> $($text)" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$text)
    Write-Host "   -> $($text)" -ForegroundColor White
}

function Write-Success {
    param([string]$text)
    Write-Host "\\n$($text)" -ForegroundColor Green -BackgroundColor Black
}

function Write-Error {
    param([string]$text)
    Write-Host "[ERROR] $($text)" -ForegroundColor Red
}

# --- Main Logic ---
Clear-Host
Write-Header "Fortuna Faucet Enhanced Launcher (PowerShell Edition)"

# 1. Check Backend Port
Write-Step "Step 1: Checking backend port ($backendPort)..."
$backendConnection = Get-NetTCPConnection -LocalPort $backendPort -ErrorAction SilentlyContinue
if ($backendConnection) {
    Write-Error "Port $backendPort is already in use. Please close the existing process."
    exit 1
} else {
    Write-Info "Port $backendPort is available."
}

# 2. Check Frontend Port
Write-Step "Step 2: Checking frontend port ($frontendPort)..."
$frontendConnection = Get-NetTCPConnection -LocalPort $frontendPort -ErrorAction SilentlyContinue
if ($frontendConnection) {
    Write-Error "Port $frontendPort is already in use. Please close the existing process."
    exit 1
} else {
    Write-Info "Port $frontendPort is available."
}

# 3. Launch Services
Write-Step "Step 3: Launching services..."
Write-Info "Starting Backend in a new window..."
Start-Process wt -ArgumentList "new-tab", "-d", ".", "cmd", "/c", "title Fortuna Backend && .\\.venv\\Scripts\\activate.bat && cd $backendDir && uvicorn api:app --reload"

Write-Info "Starting Frontend in a new window..."
Start-Process wt -ArgumentList "new-tab", "-d", "$frontendDir", "cmd", "/c", "title Fortuna Frontend && npm run dev"

Write-Info "Waiting 10 seconds for services to initialize..."
Start-Sleep -Seconds 10

# 4. Launch Browser
Write-Step "Step 4: Opening dashboard..."
Start-Process "http://localhost:$frontendPort"
Write-Info "Browser launched at http://localhost:$frontendPort"

Write-Success "All services launched successfully!"

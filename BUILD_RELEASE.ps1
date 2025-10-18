# Master Release Build Script for Fortuna Faucet
# This script automates the entire process of creating a distributable MSI installer.

$ErrorActionPreference = 'Stop'

# --- CONFIGURATION ---
$PYTHON_VERSION = "3.11.7"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-embed-amd64.zip"
$WIX_PATH = "C:\Program Files (x86)\WiX Toolset v3.14\bin"

# --- SCRIPT START ---
Write-Host "🚀 Starting Fortuna Faucet Release Build..." -ForegroundColor Green

# --- PREREQUISITE CHECK ---
Write-Host "🔍 Checking for WiX Toolset prerequisite..."
if (-not (Test-Path $WIX_PATH)) {
    Write-Host "❌ ERROR: WiX Toolset Not Found!" -ForegroundColor Red
    Write-Host "This build script requires the WiX Toolset to create the MSI installer."
    Write-Host "Please download and install it from the official site before proceeding:"
    Write-Host "➡️  https://wixtoolset.org/releases/"
    Write-Host "Build aborted."
    exit 1
}
Write-Host "✅ WiX Toolset found." -ForegroundColor Green

# 1. Set up build environment
$buildDir = ".\build"
if (Test-Path $buildDir) { Remove-Item $buildDir -Recurse -Force }
New-Item $buildDir -ItemType Directory | Out-Null
$pythonDir = "$buildDir\python"
New-Item $pythonDir -ItemType Directory | Out-Null

# 2. Download and prepare portable Python
Write-Host "🐍 Downloading and preparing Python runtime..."
$pythonZip = "$buildDir\python.zip"
Invoke-WebRequest -Uri $PYTHON_URL -OutFile $pythonZip
Expand-Archive -Path $pythonZip -DestinationPath $pythonDir

# 3. Install Python dependencies into portable environment
Write-Host "📦 Installing Python dependencies via pip..."
Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile "$buildDir\get-pip.py"
& "$pythonDir\python.exe" "$buildDir\get-pip.py"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: Failed to install pip." -ForegroundColor Red; exit 1 }
& "$pythonDir\Scripts\pip.exe" install -r .\requirements.txt
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: Failed to install Python dependencies from requirements.txt." -ForegroundColor Red; exit 1 }

# 4. Install Frontend dependencies
Write-Host "🌐 Installing frontend dependencies via npm..."
Push-Location .\web_platform\frontend
npm install
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: 'npm install' failed." -ForegroundColor Red; Pop-Location; exit 1 }
Pop-Location

# 5. Build the main application executable
Write-Host "📦 Packaging application into Fortuna.exe using PyInstaller..."
& .\.venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name Fortuna --icon=fortuna.ico .\launcher_gui.py
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: PyInstaller build failed." -ForegroundColor Red; exit 1 }

# 6. Harvest file lists for the installer using WiX Heat
Write-Host "🔥 Harvesting runtime files for WiX installer..."
& "$WIX_PATH\heat.exe" dir $pythonDir -cg PythonRuntimeComponents -dr PYTHONDIR -out .\installer\python_files.wxs
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: WiX Heat failed to harvest Python files." -ForegroundColor Red; exit 1 }
& "$WIX_PATH\heat.exe" dir .\web_platform\frontend -cg FrontendComponents -dr FRONTENDDIR -srd -sreg -scom -suid -ag -out .\installer\frontend_files.wxs
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: WiX Heat failed to harvest frontend files." -ForegroundColor Red; exit 1 }

# 7. Compile the MSI installer
Write-Host "📦 Compiling the final MSI installer..."
& "$WIX_PATH\candle.exe" .\installer\fortuna_faucet_installer.wxs .\installer\python_files.wxs .\installer\frontend_files.wxs -out .\installer\fortuna.wixobj
if ($LASTEXITCODE -ne -0) { Write-Host "❌ ERROR: WiX Candle compilation failed." -ForegroundColor Red; exit 1 }
& "$WIX_PATH\light.exe" .\installer\fortuna.wixobj -out .\dist\FortunaFaucet_Setup_v1.0.msi
if ($LASTEXITCODE -ne 0) { Write-Host "❌ ERROR: WiX Light linking failed." -ForegroundColor Red; exit 1 }

# 8. Clean up temporary files
Remove-Item .\installer\*.wxs
Remove-Item .\installer\*.wixobj

Write-Host "✅ SUCCESS! Release build complete." -ForegroundColor Green
Write-Host "Find your installer at: .\dist\FortunaFaucet_Setup_v1.0.msi"
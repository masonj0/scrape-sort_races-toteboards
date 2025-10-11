# 🎯 FORTUNA FAUCET - Windows Installation Guide

## Quick Start (3 Minutes)

### Step 1: Download and Extract
1. Download the complete Fortuna Faucet package
2. Extract to `C:\\FortunaFaucet` (recommended)

### Step 2: Run the Installer
1. Right-click `INSTALL_FORTUNA.bat`
2. Select "Run as Administrator"
3. Wait for automatic installation (3-5 minutes)

### Step 3: Configure Your API Keys
1. Open `.env` file in Notepad
2. Add your API credentials:
   ```
   API_KEY=your_secret_key_here
   ```
3. Save and close

### Step 4: Launch Fortuna
1. Double-click **"Launch Fortuna"** shortcut on your desktop
2. Wait 10 seconds for services to start
3. Dashboard opens automatically in your browser

## Desktop Shortcuts

After installation, you'll have three shortcuts:

- **Launch Fortuna** 🚀 - Starts all services
- **Fortuna Monitor** 📊 - Opens status monitor
- **Stop Fortuna** 🛑 - Cleanly stops all services

## Troubleshooting

### "Backend Offline" Error
1. Run `STOP_FORTUNA.bat`
2. Wait 10 seconds
3. Run `LAUNCH_FORTUNA.bat` again

### Can't Find .env File
The .env file should be in the same folder as LAUNCH_FORTUNA.bat.
If missing, copy .env.example to .env


## Service Management (Advanced)

The Fortuna Faucet backend runs as a persistent Windows Service, meaning it starts with your computer and runs silently in the background.

- **To Install/Start the Service:** If you ever need to manually install it, right-click `install_service.bat` and choose "Run as Administrator".
- **To Uninstall the Service:** To completely remove the background service, right-click `uninstall_service.bat` and choose "Run as Administrator".

This allows the Electron application (the user interface) to be opened and closed without interrupting the core data collection engine.

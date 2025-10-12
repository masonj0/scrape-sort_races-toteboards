# 🎯 FORTUNA FAUCET - Windows Installation Guide

## Quick Start (3 Minutes)

### Step 1: Run the Installer
1.  Right-click `INSTALL_FORTUNA.bat`
2.  Select "Run as Administrator"
3.  The installer will guide you through the entire setup, including dependency installation and first-time configuration via the Setup Wizard.

### Step 2: Launch Fortuna
1.  Double-click the **"Launch Fortuna"** shortcut on your desktop.
2.  This will start the application in your **system tray** (the area by your clock).
3.  The Fortuna Faucet icon will appear. The application is now running.

### Step 3: Control the Application
1.  **Right-click** the Fortuna Faucet tray icon to open the control menu.
2.  Select **"Open Dashboard"** to open the main user interface in your web browser.
3.  Select **"Show Monitor"** to open the native GUI for detailed system status.
4.  Select **"Quit Fortuna"** to cleanly shut down all services.

## The Tray-Centric Workflow

Fortuna Faucet is designed to be an 'always-on' application that runs quietly in the background.

*   The **Backend Service** runs continuously, managed by Windows.
*   The **System Tray Icon** is your primary control center. It lives in the background without cluttering your taskbar.
*   The **Dashboard** (web UI) and **Monitor** (GUI) are windows you can open and close at will without stopping the core application.

## Native Notifications

The application will automatically send you a native Windows notification when it detects a high-value race (score of 85% or higher), ensuring you never miss a key opportunity.

## Service Management (Advanced)

The backend runs as a persistent Windows Service. You can manage it via the `install_service.bat` and `uninstall_service.bat` scripts (run as Administrator) or through the standard Windows Services application (`services.msc`).

## Automatic Startup

You can easily configure Fortuna Faucet to start automatically when you log into Windows.

1.  Open the **Fortuna Monitor** application.
2.  Click the **"⚙️ Startup"** button.
3.  A dialog will appear asking if you want to enable startup. Click **"Yes"**.

To disable automatic startup, simply repeat the process and click **"No"**.

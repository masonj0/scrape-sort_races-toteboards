# Fortuna Faucet: Windows Operator's Manual (GUI Edition)

Welcome to the Fortuna Faucet. This guide will get you up and running.

---

## The Golden Path (The Only Steps You Need)

This is the simplest and only way you need to interact with the application.

### Step 1: Run the Installer (First Time Only)

> Find the `INSTALL_FORTUNA.bat` file in the project folder and double-click it.

A setup wizard will run. It will verify your system and install all dependencies. You only need to do this once.

### Step 2: Run the Launcher

> Find the `launcher_gui.pyw` file (or `launcher_gui.py`) and double-click it.

This is the main control panel for the application. It's the only file you need to run from now on.

### Step 3: Start the Services

> In the control panel, click the big green `▶ START SERVICES` button.

The status indicators will turn yellow as the services start, and then green once they are online. A web browser will automatically open to the dashboard.

### To Stop the Application

> Click the big red `■ STOP SERVICES` button in the control panel, or simply close the control panel window.

---

## Advanced Usage & Troubleshooting

For most users, the GUI Launcher is all you will ever need. The scripts below are for developers or for manual troubleshooting.

-   **`SERVICE_MANAGER.bat`**: The legacy command-line menu for managing services.
-   **`health_check.bat`**: Runs a series of diagnostic checks on your environment.
-   **`fix_common_issues.bat`**: Provides an interactive menu to solve common problems.
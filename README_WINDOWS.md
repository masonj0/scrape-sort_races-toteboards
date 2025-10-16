# Fortuna Faucet: Windows Operator's Manual

Welcome to the Fortuna Faucet. This guide will get you up and running.

---

## The Golden Path (The Only Steps You Need)

This is the simplest and recommended way to use the application.

### Step 1: Run the Service Manager

> Find the `SERVICE_MANAGER.bat` file in the project folder and double-click it.

That's it. This one script is your single entry point for everything.

-   **If this is your first time running the application,** a setup wizard will automatically launch. Follow its on-screen instructions. It will install all dependencies and configure the application for you.
-   **If you have run the setup before,** a menu will appear.

### Step 2: Start the Services

> In the Service Manager menu, press `1` on your keyboard and then press `Enter` to select `[1] Start Services`.

This will launch all the required backend and frontend processes in the background.

### Step 3: You're Done!

A web browser will automatically open to the Fortuna Faucet dashboard. A real-time status console will also appear to show you the system's health.

To stop the application, simply go back to the Service Manager menu and select `[2] Stop Services`.

---

## Advanced Usage & Troubleshooting

Everything you need is in the `SERVICE_MANAGER.bat`. The information below is for developers or for troubleshooting specific issues.

### Direct Scripts

-   **`INSTALL_FORTUNA.bat`**: The main installer script. The Service Manager runs this for you on first launch.
-   **`LAUNCH_FORTUNA.bat`**: The main launch script. The Service Manager runs this for you when you select `[1] Start Services`.
-   **`STOP_FORTUNA.bat`**: Stops all running services.
-   **`RESTART_FORTUNA.bat`**: Stops, then starts all services.
-   **`health_check.bat`**: Runs a series of diagnostic checks on your environment.
-   **`fix_common_issues.bat`**: Provides an interactive menu to solve common problems like corrupted installations.
-   **`CREATE_SHORTCUTS.bat`**: Creates desktop shortcuts for the main scripts.
-   **`BUILD_INSTALLER.bat`**: For developers. Builds the distributable `.msi` installer package.

### Understanding Logs

If you encounter an issue, the system generates detailed logs to help you diagnose the problem.

-   **Installation Logs:** If the setup fails, check `pip_install.log`, `npm_install.log`, and `electron_install.log` in the root directory.
-   **Service Logs:** When the application is running, all backend and frontend output is saved to timestamped files inside the `logs/` directory.
# Fortuna Faucet: Windows Operator's Manual (v3.0)

Welcome to the Fortuna Faucet. This guide will get you up and running with our new, professional-grade command suite.

---

## The Golden Path: Your First Launch

This is the simplest and only way you need to interact with the application.

### Step 1: Run the Service Manager

> Find the `SERVICE_MANAGER.bat` file in the project folder and double-click it.

This one script is your single entry point for everything. It's intelligent and will guide you.

-   **If this is your first time,** a setup wizard will automatically launch. It will verify your system and install all dependencies. Just follow the on-screen instructions.

### Step 2: Start the Services

> Once the menu appears, press `1` on your keyboard and then press `Enter` to select `[1] Start Services`.

This will launch all required processes in the background using a race-condition-free, health-checked sequence.

### Step 3: You're Done!

A web browser will automatically open to the Fortuna Faucet dashboard once all systems are confirmed to be online.

---

## Day-to-Day Operations

Always use `SERVICE_MANAGER.bat` to manage the application.

### Key Menu Options:

-   **`[1] Start Services`**: Launches the application.
-   **`[2] Stop Services`**: Performs a clean, graceful shutdown of all processes.
-   **`[3] Restart Services`**: Performs a graceful stop, then a clean start.
-   **`[4] Check Live Status`**: Instantly checks if the backend and frontend are responsive and which ports they are using.

### Troubleshooting & Diagnostics

The Service Manager provides a suite of powerful, built-in tools to help you solve common problems.

-   **`[5] View Latest Logs`**: Automatically finds and opens the most recent backend and frontend log files in Notepad for easy debugging.
-   **`[6] View Performance Stats`**: Shows a quick, real-time snapshot of system memory, CPU usage, and disk space.
-   **`[7] Validate Dependencies`**: Runs a series of checks to ensure that Python, Node.js, Git, and all other required components are correctly installed and accessible.
-   **`[9] Reset to Factory Settings`**: A powerful tool that can safely delete all logs and caches if you need to return the system to a clean state.
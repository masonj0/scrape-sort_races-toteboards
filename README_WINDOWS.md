# Fortuna Ascended: Windows Operator's Manual

Welcome to the native Windows edition of Fortuna Ascended. This guide provides two installation methods.

---

## Method 1: Recommended for Operators (MSI Installer)

This is the simplest and most professional way to install Fortuna Ascended as a complete, standalone application.

### Step 1: Build the Installer

First, you must create the MSI installer file.

1.  **Run the Builder Script**: In the project's root directory, double-click the `BUILD_INSTALLER.bat` script.
2.  **Wait for Completion**: The script will run for a few minutes.
3.  **Locate the Installer**: Upon completion, the MSI installer (e.g., `Fortuna Ascended 1.0.0.msi`) will be located in the project's root directory.

### Step 2: Run the MSI Installer

1.  Double-click the newly created `.msi` file.
2.  Follow the on-screen instructions in the graphical installer.
3.  Once finished, the application will be installed on your system, and you can launch it from the Start Menu.

---

## Method 2: For Developers (Manual Setup from Source)

This method is for developers who have cloned the source code and want to set up a local development environment.

### Step 1: Run the Installer Script

In the project's root directory, double-click the `INSTALL_FORTUNA.bat` script. This wizard will:

1.  **Check for Python and Node.js**
2.  **Create a Python Virtual Environment** (`.venv`)
3.  **Install all Python and Node.js dependencies**

### Step 2: Launch the Application

Once the installation is complete, you can run the application using the `LAUNCH_FORTUNA.bat` script.

### Step 3: (Optional) Create Desktop Shortcuts

For easier access, run the `CREATE_SHORTCUTS.bat` script to place shortcuts for `Launch`, `Stop`, and `Monitor` on your desktop.

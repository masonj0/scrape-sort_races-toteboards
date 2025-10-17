# Fortuna Faucet: Windows Operator's Manual (MSI Edition)

Welcome to the Fortuna Faucet. This guide will get you up and running.

---

## The Golden Path: The One-Click Installer

This is the simplest, safest, and only recommended way to install the application.

### Step 1: Find the Installer

> Locate the `Fortuna Faucet Setup.msi` file. If you don't have it, a developer must create it for you using the `BUILD_INSTALLER.bat` script.

### Step 2: Run the Installer

> Double-click the `.msi` file.

A standard Windows installation wizard will appear. Follow the on-screen instructions. It will install the application, all its dependencies, and create Start Menu and Desktop shortcuts for you automatically.

### Step 3: Launch the Application

> Use the new 'Fortuna Faucet' shortcut on your Desktop or in your Start Menu.

The graphical control panel will launch. Click the big green `▶ START SERVICES` button to run the application.

**You are done. There are no other steps.**

---

## For Developers Only

If you are a developer and need to set up a local environment from the source code, please refer to the `ARCHITECTURAL_MANDATE.md` and the scripts in the root directory. The `.msi` installer is the only supported path for end-users.

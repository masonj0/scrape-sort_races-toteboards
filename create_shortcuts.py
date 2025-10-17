#!/usr/bin/env python3
"""Create Windows desktop shortcuts for Fortuna Faucet"""

import os
from pathlib import Path

# Try pywin32 approach first (most reliable)
try:
    from win32com.client import Dispatch
    import pythoncom

    def create_shortcut_com(shortcut_path, target_path, description=""):
        """Create shortcut using COM (most reliable)"""
        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = str(target_path)
        shortcut.WorkingDirectory = str(Path(target_path).parent)
        shortcut.Description = description
        # Assuming fortuna.ico is in the root directory
        shortcut.IconLocation = str(Path(__file__).parent / "fortuna.ico")
        shortcut.save()
        print(f"✅ Created: {shortcut_path}")

    SHORTCUT_METHOD = "COM"
except ImportError:
    SHORTCUT_METHOD = "MANUAL"
    print("⚠️ pywin32 not available - using manual shortcut creation")

def create_shortcuts():
    """Create all necessary shortcuts"""
    desktop = Path(os.environ["USERPROFILE"]) / "Desktop"

    if not desktop.exists():
        print("❌ Desktop folder not found")
        return False

    app_dir = Path(__file__).parent.resolve()

    shortcuts = [
        {
            "name": "🐴 Launch Fortuna",
            "target": app_dir / "launcher_gui.py",
            "description": "Launch Fortuna Faucet racing analysis tool"
        },
        {
            "name": "🔧 Setup Wizard",
            "target": app_dir / "python_service" / "setup_wizard_gui.py",
            "description": "Configure Fortuna Faucet"
        },
        {
            "name": "⚙️ Verify Installation",
            "target": app_dir / "verify_installation.py",
            "description": "Check installation status"
        }
    ]

    if SHORTCUT_METHOD == "COM":
        for shortcut in shortcuts:
            try:
                shortcut_file = desktop / f"{shortcut['name']}.lnk"
                create_shortcut_com(
                    shortcut_file,
                    shortcut['target'],
                    shortcut['description']
                )
            except Exception as e:
                print(f"❌ Failed to create {shortcut['name']}: {e}")
                return False
    else:
        # Fallback: create a batch file
        for shortcut in shortcuts:
            batch_file = desktop / f"{shortcut['name']}.bat"
            with open(batch_file, 'w', newline='\n') as f:
                f.write(f"@echo off\n")
                f.write(f"python \"{shortcut['target']}\"\\n")
            print(f"✅ Created: {batch_file}")

    return True

if __name__ == "__main__":
    if create_shortcuts():
        print("\n✅ Shortcuts created successfully!")
    else:
        print("\n❌ Failed to create some shortcuts")
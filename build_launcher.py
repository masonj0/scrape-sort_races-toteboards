#!/usr/bin/env python3
# ==============================================================================
# Checkmate V8 - Master Launcher EXE Builder
# ==============================================================================
# This script uses PyInstaller to compile the `launcher.py` orchestrator
# into a single, standalone Windows executable.
# ==============================================================================

import os
import sys
import shutil
from pathlib import Path

def create_spec_file():
    """Create a PyInstaller spec file tailored for the master launcher."""
    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'sqlite3',
        'threading',
        'webbrowser',
        'pathlib'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Checkmate_Launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    icon=None
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Checkmate_Launcher'
)
"""
    with open('launcher.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created launcher.spec file")

def build_executable():
    """Build the executable using PyInstaller and the spec file."""
    print("\\n🔨 Building the Master Launcher executable...")

    create_spec_file()
    cmd = "pyinstaller launcher.spec --noconfirm"

    print(f"\\nExecuting: {cmd}")
    result = os.system(cmd)

    if result == 0:
        print("\\n✓ Build successful!")
        print("\\n📁 Your executable is located at: dist/Checkmate_Launcher.exe")
        shutil.rmtree('build', ignore_errors=True)
        os.remove('launcher.spec')
    else:
        print("\\n❌ Build failed. Check the error messages above.")

def main():
    print("=" * 60)
    print("  Checkmate V8 - Master Launcher EXE Builder")
    print("=" * 60)

    if not Path('launcher.py').exists():
        print("\\n❌ ERROR: `launcher.py` not found in the project root.")
        sys.exit(1)

    proceed = input("\\nReady to create a standalone .exe for the launcher? (y/n): ").strip().lower()

    if proceed == 'y':
        print("\\n📦 Installing/updating PyInstaller...")
        os.system(f'{sys.executable} -m pip install --upgrade pyinstaller')
        build_executable()
        print("\\n" + "=" * 60)
        print("  BUILD COMPLETE!")
        print("=" * 60)
    else:
        print("\\nBuild cancelled.")

if __name__ == '__main__':
    main()
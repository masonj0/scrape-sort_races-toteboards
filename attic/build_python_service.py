# build_python_service.py
"""
Single EXE Builder for the Checkmate V8 Headless Python Service.
This script creates a standalone Windows console executable from the
'python_service/' directory using PyInstaller.
"""

import os

def create_spec_file():
    """Create a PyInstaller spec file tailored for the headless service."""

    # NOTE: data_files might be needed for .env, configs, etc.
    # For now, we assume it's self-contained.
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(
    ['python_service/main.py'],  # Entry point is the modern service
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'schedule',
        'pydantic',
        'pydantic_settings',
        'beautifulsoup4',
        'lxml',
        'cachetools',
        'requests',
        'python-dotenv',
        'tenacity' # Ensure all dependencies are listed
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
    name='CheckmatePythonService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # CRITICAL: This is a console app, not a windowed one.
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
    name='CheckmatePythonService'
)
"""
    with open('python_service.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created python_service.spec file")

def build_executable():
    """Build the executable using PyInstaller and the spec file."""
    print("\\n🔨 Building executable for Python Service...")

    # We will use the reliable spec-based build exclusively.
    create_spec_file()
    cmd = "pyinstaller python_service.spec --noconfirm"

    print(f"\\nExecuting: {cmd}")
    result = os.system(cmd)

    if result == 0:
        print("\\n✓ Build successful!")
        print("\\n📁 Your executable is located at: dist/CheckmatePythonService.exe")
    else:
        print("\\n❌ Build failed. Check the error messages above.")

def main():
    print("=" * 60)
    print("  Checkmate Python Service - EXE BUILDER")
    print("=" * 60)

    proceed = input("\\nThis script will create a standalone .exe from the 'python_service'. Ready? (y/n): ").strip().lower()

    if proceed == 'y':
        print("\\n📦 Installing PyInstaller...")
        os.system('pip install pyinstaller')
        build_executable()
        print("\\n" + "=" * 60)
        print("  BUILD COMPLETE!")
        print("=" * 60)
    else:
        print("\\nBuild cancelled.")

if __name__ == '__main__':
    main()
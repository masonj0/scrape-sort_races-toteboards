#!/usr/bin/env python3
"""Comprehensive installation verification before launch"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Verify Python 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required (found {version.major}.{version.minor})")
        return False
    print(f"✅ Python {version.major}.{version.minor} OK")
    return True

def check_pip_packages():
    """Verify all Python dependencies installed"""
    try:
        import fastapi
        import httpx
        import pydantic
        print("✅ Python dependencies OK")
        return True
    except ImportError as e:
        print(f"❌ Missing Python package: {e}")
        return False

def check_nodejs():
    """Verify Node.js is installed"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} OK")
            return True
    except FileNotFoundError:
        print("❌ Node.js not found in PATH")
        return False

def check_npm_packages():
    """Verify npm packages in frontend"""
    frontend_dir = Path("web_platform/frontend/node_modules")
    if frontend_dir.exists():
        print("✅ npm packages installed")
        return True
    else:
        print("❌ npm packages not installed (run: npm install in frontend dir)")
        return False

def check_dotenv_file():
    """Verify .env file exists and is readable"""
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "API_KEY=" in content:
                    print("✅ .env file OK")
                    return True
                else:
                    print("❌ .env missing API_KEY")
                    return False
        except Exception as e:
            print(f"❌ Cannot read .env: {e}")
            return False
    else:
        print("❌ .env file not found")
        return False

def verify_all():
    """Run all checks"""
    print("\n" + "="*60)
    print("🔍 FORTUNA FAUCET - INSTALLATION VERIFICATION")
    print("="*60 + "\n")

    checks = [
        ("Python 3.11+", check_python_version),
        ("Python dependencies", check_pip_packages),
        ("Node.js", check_nodejs),
        ("npm packages", check_npm_packages),
        (".env configuration", check_dotenv_file),
    ]

    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}: {e}")
            results.append((check_name, False))
        print()

    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print("="*60)
    print(f"SUMMARY: {passed}/{total} checks passed")
    print("="*60)

    if passed == total:
        print("\n✅ All systems ready! You can now launch Fortuna Faucet.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(verify_all())
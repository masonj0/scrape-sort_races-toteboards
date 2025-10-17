import keyring
from pathlib import Path

try:
    import keyring.backends.windows
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

class SecureCredentialsManager:
    """Store secrets in Windows Credential Manager, not plaintext files"""

    SERVICE_NAME = "Fortuna Faucet"

    @staticmethod
    def save_api_key(key: str) -> bool:
        """Save API key securely to Windows Credential Manager"""
        if not IS_WINDOWS:
            return False
        try:
            keyring.set_password(
                SecureCredentialsManager.SERVICE_NAME,
                "api_key",
                key
            )
            return True
        except Exception as e:
            print(f"❌ Failed to save credentials: {e}")
            return False

    @staticmethod
    def get_api_key() -> str:
        """Retrieve API key from Windows Credential Manager"""
        if not IS_WINDOWS:
            return None
        try:
            key = keyring.get_password(
                SecureCredentialsManager.SERVICE_NAME,
                "api_key"
            )
            if not key:
                raise ValueError("No stored credentials found")
            return key
        except Exception as e:
            print(f"❌ Failed to retrieve credentials: {e}")
            return None

    @staticmethod
    def delete_all_credentials():
        """Clear stored credentials (for uninstall)"""
        if not IS_WINDOWS:
            return
        try:
            keyring.delete_password(
                SecureCredentialsManager.SERVICE_NAME,
                "api_key"
            )
        except:
            pass
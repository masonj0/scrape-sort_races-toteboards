# manage_secrets.py
import sys
from pathlib import Path
from cryptography.fernet import Fernet

KEY_FILE = Path('.key')

def get_cipher():
    if not KEY_FILE.exists():
        print("Secret key not found. Generating a new one...")
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        print(f"New key saved to '{KEY_FILE}'. DO NOT LOSE THIS FILE.")
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

def encrypt(value: str):
    cipher = get_cipher()
    encrypted_value = cipher.encrypt(value.encode()).decode()
    print("--- Encrypted Value ---")
    print(f"encrypted:{encrypted_value}")
    print("\nCopy the full line above (including 'encrypted:') into your .env file.")

def decrypt(value: str):
    cipher = get_cipher()
    if value.startswith('encrypted:'):
        value = value[10:]
    try:
        decrypted_value = cipher.decrypt(value.encode()).decode()
        print("--- Decrypted Value ---")
        print(decrypted_value)
    except Exception as e:
        print(f"[ERROR] Decryption failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ['encrypt', 'decrypt']:
        print("Usage: python manage_secrets.py [encrypt|decrypt] \"<your_secret>\"")
        sys.exit(1)

    action = sys.argv[1]
    secret_value = sys.argv[2]

    if action == 'encrypt':
        encrypt(secret_value)
    elif action == 'decrypt':
        decrypt(secret_value)
# app/features/vault.py
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import Dict, List, Optional, Any

class NexaVault:
    def __init__(self, filepath: str = "user/vault.enc"):
        self.filepath = filepath
        self.password: Optional[str] = None
        self.decrypted_data: Dict[str, str] = {}
        self.is_unlocked = False

    def derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    def setup_vault(self, password: str) -> str:
        if os.path.exists(self.filepath):
            return "Vault already exists. Use open to unlock it."
        
        self.password = password
        self.decrypted_data = {}
        self.is_unlocked = True
        self._save_encrypted()
        return "Vault created and initialized successfully!"

    def unlock_vault(self, password: str) -> bool:
        if not os.path.exists(self.filepath):
            return False
        
        try:
            with open(self.filepath, "rb") as f:
                raw_data = f.read()
            
            if len(raw_data) < 16:
                return False

            salt = raw_data[:16]
            encrypted_payload = raw_data[16:]
            
            key = self.derive_key(password, salt)
            fernet = Fernet(key)
            
            decrypted = fernet.decrypt(encrypted_payload).decode('utf-8')
            self.decrypted_data = json.loads(decrypted)
            self.password = password
            self.is_unlocked = True
            return True
        except Exception:
            return False

    def lock_vault(self):
        self.password = None
        self.decrypted_data = {}
        self.is_unlocked = False

    def add_secret(self, key: str, value: str) -> str:
        if not self.is_unlocked:
            return "Vault is locked. Unlock it first."
        
        self.decrypted_data[key] = value
        self._save_encrypted()
        return f"Secret for '{key}' saved successfully."

    def get_secret(self, key: str) -> Optional[str]:
        if not self.is_unlocked:
            return None
        return self.decrypted_data.get(key)

    def delete_secret(self, key: str) -> bool:
        if not self.is_unlocked:
            return False
        if key in self.decrypted_data:
            del self.decrypted_data[key]
            self._save_encrypted()
            return True
        return False

    def list_keys(self) -> List[str]:
        if not self.is_unlocked:
            return []
        return list(self.decrypted_data.keys())

    def export_vault(self) -> str:
        if not self.is_unlocked:
            return "Vault is locked. Unlock it first."
        # Returns raw JSON dump (only for backup/export purposes)
        return json.dumps(self.decrypted_data, indent=2)

    def _save_encrypted(self):
        if not self.password:
            return

        salt = os.urandom(16)
        key = self.derive_key(self.password, salt)
        fernet = Fernet(key)
        
        serialized = json.dumps(self.decrypted_data).encode('utf-8')
        encrypted = fernet.encrypt(serialized)
        
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "wb") as f:
            f.write(salt + encrypted)
stream = None

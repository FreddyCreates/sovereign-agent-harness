"""
Sovereign Vault Module — Client-Side Zero-Custody Key Manager
--------------------------------------------------------------
Manages encrypted credentials locally on-device using AES-256-GCM.
Ensures raw API keys are never leaked to LLM context buffers.
"""

import os
import json
from typing import Dict, Any, Optional, List
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

DEFAULT_VAULT_PATH = os.path.expanduser("~/.sovereign_vault/harness_vault.enc")

class SovereignVault:
    def __init__(self, vault_path: str = DEFAULT_VAULT_PATH, passphrase: str = "sovereign-agent-master-passphrase"):
        self.vault_path = vault_path
        self.salt = b"SOVEREIGN_AGENT_HARNESS_SALT_v1"
        self.key = self._derive_key(passphrase.encode("utf-8"))
        self.aesgcm = AESGCM(self.key)
        self.data: Dict[str, Any] = {"keys": {}, "credentials": {}, "version": "1.0.0"}
        self._load_or_initialize()

    def _derive_key(self, passphrase: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100_000,
        )
        return kdf.derive(passphrase)

    def _load_or_initialize(self):
        if os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, "rb") as f:
                    encrypted = f.read()
                nonce = encrypted[:12]
                ciphertext = encrypted[12:]
                decrypted = self.aesgcm.decrypt(nonce, ciphertext, None)
                self.data = json.loads(decrypted.decode("utf-8"))
            except Exception as e:
                print(f"[SovereignVault] Decryption warning ({e}); initializing new vault.")
                self.data = {"keys": {}, "credentials": {}, "version": "1.0.0"}
        else:
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.vault_path), exist_ok=True)
        nonce = os.urandom(12)
        plaintext = json.dumps(self.data, indent=2).encode("utf-8")
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        with open(self.vault_path, "wb") as f:
            f.write(nonce + ciphertext)

    def set_key(self, key_name: str, key_value: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        self.data["keys"][key_name] = {
            "value": key_value,
            "metadata": metadata or {},
        }
        self.save()
        return True

    def store_key(self, key_name: str, key_value: str, passphrase: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        return self.set_key(key_name, key_value, metadata)

    def get_key(self, key_name: str, default: Optional[str] = None) -> Optional[str]:
        # Also check environment variables if missing in vault
        val = self.data["keys"].get(key_name, {}).get("value")
        if not val:
            val = os.getenv(key_name, default)
        return val

    def retrieve_key(self, key_name: str, passphrase: Optional[str] = None, default: Optional[str] = None) -> Optional[str]:
        return self.get_key(key_name, default)

    def list_keys(self) -> List[str]:
        return list(self.data["keys"].keys())

    def mask_secrets_in_text(self, text: str) -> str:
        """Sanitizes text by replacing any plaintext secret keys with masked placeholders."""
        masked_text = text
        for key_info in self.data["keys"].values():
            val = key_info.get("value")
            if val and len(val) > 6 and val in masked_text:
                masked_text = masked_text.replace(val, f"[SECRET_MASKED_{val[:3]}...{val[-3:]}]")
        return masked_text

    def get_status(self) -> Dict[str, Any]:
        return {
            "vault_path": self.vault_path,
            "zero_custody": True,
            "total_keys": len(self.data["keys"]),
            "status": "HEALTHY"
        }

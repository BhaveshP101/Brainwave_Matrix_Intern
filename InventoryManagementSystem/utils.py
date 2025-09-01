import hashlib
import os
import re

    # --- Password hashing (salted SHA-256) ---
    # For production, consider bcrypt/argon2. Here we keep stdlib-only for portability.
def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
        if salt is None:
            salt = os.urandom(16)
        if isinstance(salt, str):
            salt = salt.encode("utf-8")
        pwd_bytes = password.encode("utf-8")
        digest = hashlib.sha256(salt + pwd_bytes).hexdigest()
        return digest, salt.hex()

def verify_password(password: str, salt_hex: str, expected_hash: str) -> bool:
        salt = bytes.fromhex(salt_hex)
        digest, _ = hash_password(password, salt)
        return digest == expected_hash

    # --- Validation helpers ---
def is_non_empty(text: str) -> bool:
        return bool(text and text.strip())

def is_positive_int(value: str) -> bool:
        try:
            v = int(value)
            return v >= 0
        except Exception:
            return False

def is_positive_float(value: str) -> bool:
        try:
            v = float(value)
            return v >= 0.0
        except Exception:
            return False

def price_str_to_float(value: str) -> float:
        return float(value)

def normalize_str(s: str) -> str:
        return re.sub(r"\\s+", " ", (s or "").strip())

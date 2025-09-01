\
from typing import Optional
from db import get_connection
from utils import hash_password, verify_password, normalize_str

def authenticate(username: str, password: str) -> Optional[dict]:
        username = normalize_str(username)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            if not row:
                return None
            if verify_password(password, row["salt_hex"], row["pwd_hash"]):
                return dict(row)
            return None

def create_user(username: str, password: str, role: str) -> tuple[bool, str]:
        username = normalize_str(username)
        if role not in ("admin","user"):
            return False, "Role must be 'admin' or 'user'."
        if not username:
            return False, "Username cannot be empty."
        if len(password) < 6:
            return False, "Password must be at least 6 characters."
        pwd_hash, salt_hex = hash_password(password)
        try:
            with get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users(username, pwd_hash, salt_hex, role) VALUES (?,?,?,?)",
                    (username, pwd_hash, salt_hex, role),
                )
                conn.commit()
            return True, "User created."
        except Exception as e:
            return False, f"Error creating user: {e}"

def list_users():
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, username, role FROM users ORDER BY user_id")
            return [dict(r) for r in cur.fetchall()]

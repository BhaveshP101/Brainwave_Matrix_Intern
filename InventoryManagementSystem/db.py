\
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("inventory.db")

def get_connection():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
        with get_connection() as conn:
            cur = conn.cursor()
            # Users
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pwd_hash TEXT NOT NULL,
                salt_hex TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','user'))
            )""")
            # Products
            cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL DEFAULT 0,
                quantity INTEGER NOT NULL DEFAULT 0,
                reorder_level INTEGER NOT NULL DEFAULT 5,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")
            # Sales
            cur.execute("""
            CREATE TABLE IF NOT EXISTS sales(
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity_sold INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                sold_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(product_id) ON DELETE CASCADE
            )""")
            conn.commit()

def ensure_default_admin():
        # create default admin if none
        from utils import hash_password
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) AS c FROM users")
            if cur.fetchone()["c"] == 0:
                pwd_hash, salt_hex = hash_password("admin123")
                cur.execute(
                    "INSERT INTO users(username, pwd_hash, salt_hex, role) VALUES (?,?,?,?)",
                    ("admin", pwd_hash, salt_hex, "admin"),
                )
                conn.commit()

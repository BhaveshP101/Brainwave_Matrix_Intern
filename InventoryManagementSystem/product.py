from typing import List, Optional, Dict, Any
from db import get_connection
from utils import normalize_str

def add_product(name: str, category: str, price: float, quantity: int, reorder_level: int = 5) -> int:
        name = normalize_str(name)
        category = normalize_str(category)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO products(name, category, price, quantity, reorder_level) VALUES(?,?,?,?,?)",
                (name, category, price, quantity, reorder_level),
            )
            conn.commit()
            return cur.lastrowid

def update_product(product_id: int, name: str, category: str, price: float, quantity: int, reorder_level: int):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE products
                   SET name=?, category=?, price=?, quantity=?, reorder_level=?
                   WHERE product_id=?""",
                (normalize_str(name), normalize_str(category), price, quantity, reorder_level, product_id),
            )
            conn.commit()

def delete_product(product_id: int):
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM products WHERE product_id=?", (product_id,))
            conn.commit()

def search_products(query: str) -> List[Dict[str, Any]]:
        q = f"%{normalize_str(query)}%"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """SELECT * FROM products
                   WHERE name LIKE ? OR category LIKE ? OR CAST(product_id AS TEXT) LIKE ?
                   ORDER BY product_id DESC""",
                (q, q, q),
            )
            return [dict(r) for r in cur.fetchall()]

def list_products() -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products ORDER BY product_id DESC")
            return [dict(r) for r in cur.fetchall()]

def low_stock(threshold: int | None = None) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cur = conn.cursor()
            if threshold is None:
                cur.execute("SELECT * FROM products WHERE quantity <= reorder_level ORDER BY quantity ASC")
            else:
                cur.execute("SELECT * FROM products WHERE quantity <= ? ORDER BY quantity ASC", (threshold,))
            return [dict(r) for r in cur.fetchall()]

def adjust_stock(product_id: int, delta_qty: int):
        with get_connection() as conn:
            cur = conn.cursor()
            # Prevent negative stock
            cur.execute("SELECT quantity FROM products WHERE product_id=?", (product_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Product not found")
            new_qty = row["quantity"] + delta_qty
            if new_qty < 0:
                raise ValueError("Insufficient stock")
            cur.execute("UPDATE products SET quantity=? WHERE product_id=?", (new_qty, product_id))
            conn.commit()

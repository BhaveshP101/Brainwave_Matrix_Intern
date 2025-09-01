from typing import List, Dict, Any, Tuple
from db import get_connection

def record_sale(product_id: int, quantity_sold: int) -> Tuple[int, float]:
        # Fetch unit price and check stock, then insert sale and update stock
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT price, quantity FROM products WHERE product_id=?", (product_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Product not found")
            unit_price = row["price"]
            stock = row["quantity"]
            if quantity_sold <= 0:
                raise ValueError("Quantity sold must be positive")
            if stock < quantity_sold:
                raise ValueError("Insufficient stock")

            total = round(unit_price * quantity_sold, 2)
            cur.execute(
                "INSERT INTO sales(product_id, quantity_sold, unit_price, total_price) VALUES(?,?,?,?)",
                (product_id, quantity_sold, unit_price, total),
            )
            cur.execute("UPDATE products SET quantity=? WHERE product_id=?", (stock - quantity_sold, product_id))
            conn.commit()
            return cur.lastrowid, total

def sales_summary(date_from: str | None = None, date_to: str | None = None) -> Dict[str, Any]:
        query = "SELECT COUNT(*) as transactions, COALESCE(SUM(total_price),0) as revenue FROM sales"
        params = []
        where = []
        if date_from:
            where.append("DATE(sold_at) >= DATE(?)")
            params.append(date_from)
        if date_to:
            where.append("DATE(sold_at) <= DATE(?)")
            params.append(date_to)
        if where:
            query += " WHERE " + " AND ".join(where)
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, tuple(params))
            row = cur.fetchone()
            return {"transactions": row["transactions"], "revenue": round(row["revenue"], 2)}

def list_sales(date_from: str | None = None, date_to: str | None = None) -> List[Dict[str, Any]]:
        query = "SELECT sale_id, product_id, quantity_sold, unit_price, total_price, sold_at FROM sales"
        params = []
        where = []
        if date_from:
            where.append("DATE(sold_at) >= DATE(?)")
            params.append(date_from)
        if date_to:
            where.append("DATE(sold_at) <= DATE(?)")
            params.append(date_to)
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY sold_at DESC"
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, tuple(params))
            return [dict(r) for r in cur.fetchall()]

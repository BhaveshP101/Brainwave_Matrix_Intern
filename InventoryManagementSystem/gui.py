import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from auth import authenticate, create_user, list_users
from product import add_product, update_product, delete_product, list_products, search_products, low_stock
from sales import record_sale, sales_summary, list_sales
from utils import is_positive_float, is_positive_int, normalize_str
import csv
from datetime import date


class LoginWindow(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Inventory Manager - Login")
            self.geometry("380x230")
            self.resizable(False, False)

            frm = ttk.Frame(self, padding=16)
            frm.pack(fill="both", expand=True)

            ttk.Label(frm, text="Username").grid(row=0, column=0, sticky="w", pady=6)
            self.e_user = ttk.Entry(frm, width=28)
            self.e_user.grid(row=0, column=1)

            ttk.Label(frm, text="Password").grid(row=1, column=0, sticky="w", pady=6)
            self.e_pwd = ttk.Entry(frm, width=28, show="*")
            self.e_pwd.grid(row=1, column=1)

            self.var_show = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(frm, text="Show password", variable=self.var_show, command=self.toggle_pwd)
            cb.grid(row=2, column=1, sticky="w")

            btn = ttk.Button(frm, text="Login", command=self.on_login)
            btn.grid(row=3, column=1, sticky="e", pady=12)

            self.status = ttk.Label(frm, text="Default admin: admin / admin123", foreground="gray")
            self.status.grid(row=4, column=0, columnspan=2, sticky="w")

            self.bind("<Return>", lambda e: self.on_login())

        def toggle_pwd(self):
            self.e_pwd.configure(show="" if self.var_show.get() else "*")

        def on_login(self):
            user = self.e_user.get().strip()
            pwd = self.e_pwd.get()
            row = authenticate(user, pwd)
            if not row:
                messagebox.showerror("Login failed", "Invalid username or password.")
                return
            self.destroy()
            app = MainWindow(current_user=row)
            app.mainloop()

class MainWindow(tk.Tk):
        def __init__(self, current_user: dict):
            super().__init__()
            self.current_user = current_user
            self.title(f"Inventory Manager - Logged in as {current_user['username']} ({current_user['role']})")
            self.geometry("1050x650")

            self.notebook = ttk.Notebook(self)
            self.notebook.pack(fill="both", expand=True)

            self.products_tab = ttk.Frame(self.notebook)
            self.sales_tab = ttk.Frame(self.notebook)
            self.reports_tab = ttk.Frame(self.notebook)
            self.users_tab = ttk.Frame(self.notebook)

            self.notebook.add(self.products_tab, text="Products")
            self.notebook.add(self.sales_tab, text="Sales")
            self.notebook.add(self.reports_tab, text="Reports")
            if self.current_user["role"] == "admin":
                self.notebook.add(self.users_tab, text="Users")

            self.build_products_tab()
            self.build_sales_tab()
            self.build_reports_tab()
            if self.current_user["role"] == "admin":
                self.build_users_tab()

        # --- Products tab ---
        def build_products_tab(self):
            frm = ttk.Frame(self.products_tab, padding=8)
            frm.pack(fill="both", expand=True)

            form = ttk.LabelFrame(frm, text="Product Details", padding=8)
            form.pack(fill="x")

            self.var_pid = tk.StringVar()
            ttk.Label(form, text="ID").grid(row=0, column=0, sticky="w")
            self.e_pid = ttk.Entry(form, textvariable=self.var_pid, state="readonly", width=10)
            self.e_pid.grid(row=0, column=1, padx=6, pady=4)

            ttk.Label(form, text="Name").grid(row=0, column=2, sticky="w")
            self.e_name = ttk.Entry(form, width=30)
            self.e_name.grid(row=0, column=3, padx=6, pady=4)

            ttk.Label(form, text="Category").grid(row=0, column=4, sticky="w")
            self.e_cat = ttk.Entry(form, width=20)
            self.e_cat.grid(row=0, column=5, padx=6, pady=4)

            ttk.Label(form, text="Price").grid(row=1, column=0, sticky="w")
            self.e_price = ttk.Entry(form, width=12)
            self.e_price.grid(row=1, column=1, padx=6, pady=4)

            ttk.Label(form, text="Quantity").grid(row=1, column=2, sticky="w")
            self.e_qty = ttk.Entry(form, width=12)
            self.e_qty.grid(row=1, column=3, padx=6, pady=4)

            ttk.Label(form, text="Reorder ≤").grid(row=1, column=4, sticky="w")
            self.e_reorder = ttk.Entry(form, width=12)
            self.e_reorder.grid(row=1, column=5, padx=6, pady=4)

            btns = ttk.Frame(form)
            btns.grid(row=2, column=0, columnspan=6, sticky="e", pady=6)
            ttk.Button(btns, text="Add", command=self.on_add_product).pack(side="left", padx=4)
            ttk.Button(btns, text="Update", command=self.on_update_product).pack(side="left", padx=4)
            ttk.Button(btns, text="Delete", command=self.on_delete_product).pack(side="left", padx=4)
            ttk.Button(btns, text="Clear", command=self.clear_product_form).pack(side="left", padx=4)

            # Search
            search_frame = ttk.Frame(frm)
            search_frame.pack(fill="x", pady=6)
            ttk.Label(search_frame, text="Search").pack(side="left")
            self.e_search = ttk.Entry(search_frame, width=36)
            self.e_search.pack(side="left", padx=6)
            ttk.Button(search_frame, text="Go", command=self.refresh_products_filtered).pack(side="left")
            ttk.Button(search_frame, text="Show All", command=self.refresh_products).pack(side="left", padx=6)

            # Table
            table_frame = ttk.Frame(frm)
            table_frame.pack(fill="both", expand=True)
            columns = ("product_id","name","category","price","quantity","reorder_level")
            self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
            for c in columns:
                self.tree.heading(c, text=c.capitalize())
                self.tree.column(c, width=120 if c!="name" else 220, anchor="center")
            self.tree.pack(fill="both", expand=True, side="left")
            self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

            # Scrollbar
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")

            # Tag for low stock highlighting
            self.tree.tag_configure("low", background="#ffe8e8")

            self.refresh_products()

        def on_tree_select(self, _evt=None):
            sel = self.tree.selection()
            if not sel:
                return
            vals = self.tree.item(sel[0])["values"]
            self.var_pid.set(vals[0])
            self.e_name.delete(0,"end"); self.e_name.insert(0, vals[1])
            self.e_cat.delete(0,"end"); self.e_cat.insert(0, vals[2])
            self.e_price.delete(0,"end"); self.e_price.insert(0, vals[3])
            self.e_qty.delete(0,"end"); self.e_qty.insert(0, vals[4])
            self.e_reorder.delete(0,"end"); self.e_reorder.insert(0, vals[5])

        def clear_product_form(self):
            self.var_pid.set("")
            for e in (self.e_name, self.e_cat, self.e_price, self.e_qty, self.e_reorder):
                e.delete(0,"end")

        def refresh_products(self):
            self.tree.delete(*self.tree.get_children())
            for p in list_products():
                tag = ("low",) if p["quantity"] <= p["reorder_level"] else ("",)
                self.tree.insert("", "end", values=(p["product_id"], p["name"], p["category"], p["price"], p["quantity"], p["reorder_level"]), tags=tag)

        def refresh_products_filtered(self):
            q = self.e_search.get().strip()
            self.tree.delete(*self.tree.get_children())
            for p in search_products(q):
                tag = ("low",) if p["quantity"] <= p["reorder_level"] else ("",)
                self.tree.insert("", "end", values=(p["product_id"], p["name"], p["category"], p["price"], p["quantity"], p["reorder_level"]), tags=tag)

        def on_add_product(self):
            name = self.e_name.get().strip()
            cat = self.e_cat.get().strip()
            price = self.e_price.get().strip()
            qty = self.e_qty.get().strip()
            reorder = self.e_reorder.get().strip() or "5"

            if not name:
                messagebox.showwarning("Validation", "Name is required."); return
            if not is_positive_float(price):
                messagebox.showwarning("Validation", "Price must be a non-negative number."); return
            if not is_positive_int(qty) or not is_positive_int(reorder):
                messagebox.showwarning("Validation", "Quantity and Reorder must be non-negative integers."); return

            add_product(name, cat, float(price), int(qty), int(reorder))
            self.clear_product_form()
            self.refresh_products()
            messagebox.showinfo("Success", "Product added.")

        def on_update_product(self):
            pid = self.var_pid.get()
            if not pid:
                messagebox.showwarning("Update", "Select a product first."); return
            name = self.e_name.get().strip()
            cat = self.e_cat.get().strip()
            price = self.e_price.get().strip()
            qty = self.e_qty.get().strip()
            reorder = self.e_reorder.get().strip() or "5"
            if not name:
                messagebox.showwarning("Validation", "Name is required."); return
            if not is_positive_float(price):
                messagebox.showwarning("Validation", "Price must be a non-negative number."); return
            if not is_positive_int(qty) or not is_positive_int(reorder):
                messagebox.showwarning("Validation", "Quantity and Reorder must be non-negative integers."); return
            update_product(int(pid), name, cat, float(price), int(qty), int(reorder))
            self.refresh_products()
            messagebox.showinfo("Updated", "Product updated.")

        def on_delete_product(self):
            pid = self.var_pid.get()
            if not pid:
                messagebox.showwarning("Delete", "Select a product first."); return
            if not messagebox.askyesno("Confirm", "Delete this product?"):
                return
            delete_product(int(pid))
            self.clear_product_form()
            self.refresh_products()
            messagebox.showinfo("Deleted", "Product deleted.")

        # --- Sales tab ---
        def build_sales_tab(self):
            frm = ttk.Frame(self.sales_tab, padding=8)
            frm.pack(fill="both", expand=True)

            lf = ttk.LabelFrame(frm, text="Record Sale", padding=8)
            lf.pack(fill="x")

            ttk.Label(lf, text="Product ID").grid(row=0, column=0, sticky="w")
            self.e_sale_pid = ttk.Entry(lf, width=12)
            self.e_sale_pid.grid(row=0, column=1, padx=6, pady=4)

            ttk.Label(lf, text="Quantity Sold").grid(row=0, column=2, sticky="w")
            self.e_sale_qty = ttk.Entry(lf, width=12)
            self.e_sale_qty.grid(row=0, column=3, padx=6, pady=4)

            ttk.Button(lf, text="Submit", command=self.submit_sale).grid(row=0, column=4, padx=6)

            self.sales_status = ttk.Label(lf, text="", foreground="green")
            self.sales_status.grid(row=1, column=0, columnspan=5, sticky="w")

            # Sales list
            list_frame = ttk.LabelFrame(frm, text="Recent Sales", padding=8)
            list_frame.pack(fill="both", expand=True, pady=6)

            self.sales_tree = ttk.Treeview(list_frame, columns=("sale_id","product_id","quantity_sold","unit_price","total_price","sold_at"), show="headings")
            for c in ("sale_id","product_id","quantity_sold","unit_price","total_price","sold_at"):
                self.sales_tree.heading(c, text=c.replace("_"," ").title())
                self.sales_tree.column(c, width=130, anchor="center")
            self.sales_tree.pack(fill="both", expand=True, side="left")
            vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.sales_tree.yview)
            self.sales_tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")

            self.refresh_sales()

        def submit_sale(self):
            pid = self.e_sale_pid.get().strip()
            qty = self.e_sale_qty.get().strip()
            if not pid.isdigit():
                messagebox.showwarning("Validation", "Product ID must be a number."); return
            if not qty.isdigit() or int(qty) <= 0:
                messagebox.showwarning("Validation", "Quantity must be a positive integer."); return
            try:
                sale_id, total = record_sale(int(pid), int(qty))
                self.sales_status.config(text=f"Sale #{sale_id} recorded. Total = {total}")
                self.refresh_products()
                self.refresh_sales()
                self.e_sale_qty.delete(0,"end")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        def refresh_sales(self):
            self.sales_tree.delete(*self.sales_tree.get_children())
            for s in list_sales():
                self.sales_tree.insert("", "end", values=(s["sale_id"], s["product_id"], s["quantity_sold"], s["unit_price"], s["total_price"], s["sold_at"]))

        # --- Reports tab ---
        def build_reports_tab(self):
            frm = ttk.Frame(self.reports_tab, padding=8)
            frm.pack(fill="both", expand=True)

            top = ttk.Frame(frm)
            top.pack(fill="x", pady=6)

            ttk.Label(top, text="From (YYYY-MM-DD)").pack(side="left")
            self.e_from = ttk.Entry(top, width=12)
            self.e_from.pack(side="left", padx=6)
            ttk.Label(top, text="To").pack(side="left")
            self.e_to = ttk.Entry(top, width=12)
            self.e_to.pack(side="left", padx=6)

            ttk.Button(top, text="Today", command=self.set_today).pack(side="left", padx=4)
            ttk.Button(top, text="This Month", command=self.set_this_month).pack(side="left", padx=4)
            ttk.Button(top, text="Run Summary", command=self.run_summary).pack(side="left", padx=8)
            ttk.Button(top, text="Export Sales CSV", command=self.export_sales_csv).pack(side="right", padx=4)
            ttk.Button(top, text="Export Products CSV", command=self.export_products_csv).pack(side="right", padx=4)

            # Summary
            self.summary_lbl = ttk.Label(frm, text="Summary: —", font=("TkDefaultFont", 10, "bold"))
            self.summary_lbl.pack(anchor="w", pady=6)

            # Low stock
            lf = ttk.LabelFrame(frm, text="Low Stock Alerts", padding=8)
            lf.pack(fill="both", expand=True)
            self.low_tree = ttk.Treeview(lf, columns=("product_id","name","category","price","quantity","reorder_level"), show="headings")
            for c in ("product_id","name","category","price","quantity","reorder_level"):
                self.low_tree.heading(c, text=c.capitalize())
                self.low_tree.column(c, width=120 if c!="name" else 220, anchor="center")
            self.low_tree.pack(fill="both", expand=True, side="left")
            vsb = ttk.Scrollbar(lf, orient="vertical", command=self.low_tree.yview)
            self.low_tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")
            self.refresh_low_stock()

        def set_today(self):
            today = date.today().isoformat()
            self.e_from.delete(0,"end"); self.e_from.insert(0, today)
            self.e_to.delete(0,"end"); self.e_to.insert(0, today)

        def set_this_month(self):
            d = date.today()
            first = d.replace(day=1).isoformat()
            last = d.isoformat()
            self.e_from.delete(0,"end"); self.e_from.insert(0, first)
            self.e_to.delete(0,"end"); self.e_to.insert(0, last)

        def run_summary(self):
            df = self.e_from.get().strip() or None
            dt = self.e_to.get().strip() or None
            s = sales_summary(df, dt)
            self.summary_lbl.config(text=f"Summary: transactions={s['transactions']}, revenue={s['revenue']}")
            self.refresh_low_stock()

        def refresh_low_stock(self):
            self.low_tree.delete(*self.low_tree.get_children())
            for p in low_stock():
                self.low_tree.insert("", "end", values=(p["product_id"], p["name"], p["category"], p["price"], p["quantity"], p["reorder_level"]))

        def export_products_csv(self):
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Export Products CSV")
            if not path: return
            from product import list_products
            rows = list_products()
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["product_id","name","category","price","quantity","reorder_level","created_at"])
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("Export", f"Exported {len(rows)} products.")

        def export_sales_csv(self):
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")], title="Export Sales CSV")
            if not path: return
            df = self.e_from.get().strip() or None
            dt = self.e_to.get().strip() or None
            rows = list_sales(df, dt)
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["sale_id","product_id","quantity_sold","unit_price","total_price","sold_at"])
                writer.writeheader()
                writer.writerows(rows)
            messagebox.showinfo("Export", f"Exported {len(rows)} sales.")

        # --- Users tab (admin only) ---
        def build_users_tab(self):
            frm = ttk.Frame(self.users_tab, padding=8)
            frm.pack(fill="both", expand=True)

            lf = ttk.LabelFrame(frm, text="Create User", padding=8)
            lf.pack(fill="x")

            ttk.Label(lf, text="Username").grid(row=0, column=0, sticky="w")
            self.e_u_name = ttk.Entry(lf, width=20)
            self.e_u_name.grid(row=0, column=1, padx=6, pady=4)

            ttk.Label(lf, text="Password").grid(row=0, column=2, sticky="w")
            self.e_u_pwd = ttk.Entry(lf, width=20, show="*")
            self.e_u_pwd.grid(row=0, column=3, padx=6, pady=4)
            self._u_show = tk.BooleanVar(value=False)
            ttk.Checkbutton(lf, text="Show", variable=self._u_show, command=lambda: self.e_u_pwd.config(show="" if self._u_show.get() else "*")).grid(row=0, column=4, padx=4)

            ttk.Label(lf, text="Role").grid(row=0, column=5, sticky="w")
            self.cb_role = ttk.Combobox(lf, values=["admin","user"], state="readonly", width=10)
            self.cb_role.current(1)
            self.cb_role.grid(row=0, column=6, padx=6)

            ttk.Button(lf, text="Create", command=self.on_create_user).grid(row=0, column=7, padx=6)

            # Users list
            self.user_tree = ttk.Treeview(frm, columns=("user_id","username","role"), show="headings")
            for c in ("user_id","username","role"):
                self.user_tree.heading(c, text=c.title())
                self.user_tree.column(c, width=180 if c=="username" else 120, anchor="center")
            self.user_tree.pack(fill="both", expand=True, pady=6)
            self.refresh_users()

        def on_create_user(self):
            ok, msg = create_user(self.e_u_name.get(), self.e_u_pwd.get(), self.cb_role.get())
            if ok:
                self.e_u_name.delete(0,"end"); self.e_u_pwd.delete(0,"end")
                self.refresh_users()
                messagebox.showinfo("User", "User created.")
            else:
                messagebox.showerror("User", msg)

        def refresh_users(self):
            for i in self.user_tree.get_children():
                self.user_tree.delete(i)
            for u in list_users():
                self.user_tree.insert("", "end", values=(u["user_id"], u["username"], u["role"]))

def run_app():
        from db import init_db, ensure_default_admin
        init_db()
        ensure_default_admin()
        LoginWindow().mainloop()

if __name__ == "__main__":
        run_app()

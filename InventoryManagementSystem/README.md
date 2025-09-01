\
    # Inventory Management System (Python + Tkinter + SQLite)

    A clean, portable **Inventory Management System** with:
    - **User authentication** (admin/user)
    - **Product CRUD**
    - **Inventory tracking** with **low-stock alerts**
    - **Sales recording** (auto stock update)
    - **Reports** (date filters, revenue, CSV export)
    - **GUI** built in **Tkinter**
    - **SQLite** database (no setup required)

    > Default admin login: **admin / admin123** (change after first login).

    ## Project Structure
    ```
    InventoryManagementSystem/
    ├─ main.py          # Entry point
    ├─ gui.py           # Tkinter GUI
    ├─ db.py            # SQLite schema & connection
    ├─ auth.py          # Authentication & user management
    ├─ product.py       # Product CRUD and low-stock helpers
    ├─ sales.py         # Sales and reports
    ├─ utils.py         # Hashing & validation
    ├─ inventory.db     # Auto-created on first run
    └─ README.md
    ```

    ## How to Run
    1. **Python 3.10+** recommended. No external dependencies required.
    2. Open a terminal in this folder and run:
       ```bash
       python main.py
       ```
    3. Login with `admin / admin123`.
    4. Change the admin password by creating a new admin user and disabling the default in production (or extend code to change passwords).

    ## Screens
    - **Products**: Add/Edit/Delete/Search. Low stock rows are highlighted.
    - **Sales**: Record sales with product ID and quantity. Prevents negative stock.
    - **Reports**: Date filters (Today/This Month), revenue, transactions, **Export CSV** for products/sales.
    - **Users (Admin)**: Create users with role `admin` or `user`.

    ## Notes
    - Passwords are stored using **salted SHA-256** (stdlib only). For production, switch to **bcrypt**/**argon2**.
    - CSV export uses the built-in `csv` module for compatibility.
    - Database file `inventory.db` appears in the project folder after first run.

    ## Suggested Enhancements (nice-to-have)
    - Password change/reset UI
    - Barcode scanning support
    - PDF report generation
    - Role-based UI restrictions beyond tab visibility
    - Import from CSV for initial product catalog

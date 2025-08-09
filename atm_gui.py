import tkinter as tk
from tkinter import messagebox

users = {
    "1234": {"pin": "1111", "balance": 10000},
    "5678": {"pin": "2222", "balance": 5000},
    "9876": {"pin": "3333", "balance": 7500},
}

current_user = None

def login():
    global current_user
    card = card_entry.get()
    pin = pin_entry.get()

    if card in users and users[card]["pin"] == pin:
        current_user = card
        show_main_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid Card Number or PIN")

def show_main_menu():
    login_frame.pack_forget()
    menu_frame.pack()

def logout():
    global current_user
    current_user = None
    menu_frame.pack_forget()
    login_frame.pack()

def check_balance():
    balance = users[current_user]["balance"]
    messagebox.showinfo("Balance", f"Your balance is ₹{balance}")

def deposit():
    try:
        amt = float(deposit_entry.get())
        if amt > 0:
            users[current_user]["balance"] += amt
            messagebox.showinfo("Deposit", "Amount deposited successfully.")
            deposit_entry.delete(0, tk.END)
    except:
        messagebox.showerror("Error", "Enter a valid amount.")

def withdraw():
    try:
        amt = float(withdraw_entry.get())
        if 0 < amt <= users[current_user]["balance"]:
            users[current_user]["balance"] -= amt
            messagebox.showinfo("Withdraw", "Amount withdrawn successfully.")
            withdraw_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Insufficient balance.")
    except:
        messagebox.showerror("Error", "Enter a valid amount.")

root = tk.Tk()
root.title("ATM Interface")
root.geometry("300x400")

# Login Frame
login_frame = tk.Frame(root)
tk.Label(login_frame, text="Card Number").pack(pady=5)
card_entry = tk.Entry(login_frame)
card_entry.pack(pady=5)

tk.Label(login_frame, text="PIN").pack(pady=5)
pin_entry = tk.Entry(login_frame, show="*")
pin_entry.pack(pady=5)

tk.Button(login_frame, text="Login", command=login).pack(pady=10)
login_frame.pack()

# Menu Frame
menu_frame = tk.Frame(root)

tk.Button(menu_frame, text="Check Balance", command=check_balance).pack(pady=10)

tk.Label(menu_frame, text="Deposit Amount").pack()
deposit_entry = tk.Entry(menu_frame)
deposit_entry.pack()
tk.Button(menu_frame, text="Deposit", command=deposit).pack(pady=5)

tk.Label(menu_frame, text="Withdraw Amount").pack()
withdraw_entry = tk.Entry(menu_frame)
withdraw_entry.pack()
tk.Button(menu_frame, text="Withdraw", command=withdraw).pack(pady=5)

tk.Button(menu_frame, text="Logout", command=logout).pack(pady=10)

root.mainloop()

# ---------------------------
# ATM Interface in Python
# ---------------------------

class UserAccount:
    def __init__(self, card_number, pin, balance=0):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance

    def check_balance(self):
        return self.balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        return False

    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def transfer(self, receiver_account, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            receiver_account.balance += amount
            return True
        return False


class ATM:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.load_users()

    def load_users(self):
        # Predefined user accounts (card_number, pin, balance)
        self.users["1234"] = UserAccount("1234", "1111", 10000)
        self.users["5678"] = UserAccount("5678", "2222", 5000)
        self.users["9876"] = UserAccount("9876", "3333", 7500)

    def login(self):
        print("🔐 Welcome to the Python ATM")
        card = input("Enter Card Number: ")
        pin = input("Enter PIN: ")

        user = self.users.get(card)
        if user and user.pin == pin:
            self.current_user = user
            print("✅ Login Successful!\n")
            return True
        else:
            print("❌ Invalid Card Number or PIN\n")
            return False

    def show_menu(self):
        print("========= ATM MENU =========")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Funds")
        print("5. Exit")
        print("============================")

    def handle_choice(self, choice):
        if choice == "1":
            balance = self.current_user.check_balance()
            print(f"💰 Your current balance is: ₹{balance}")
        elif choice == "2":
            amount = float(input("Enter amount to deposit: ₹"))
            if self.current_user.deposit(amount):
                print("✅ Deposit successful.")
            else:
                print("❌ Invalid deposit amount.")
        elif choice == "3":
            amount = float(input("Enter amount to withdraw: ₹"))
            if self.current_user.withdraw(amount):
                print("✅ Withdrawal successful.")
            else:
                print("❌ Insufficient balance or invalid amount.")
        elif choice == "4":
            to_card = input("Enter recipient card number: ")
            amount = float(input("Enter amount to transfer: ₹"))
            receiver = self.users.get(to_card)
            if receiver and self.current_user.transfer(receiver, amount):
                print("✅ Transfer successful.")
            else:
                print("❌ Transfer failed. Check balance or card number.")
        elif choice == "5":
            print("👋 Thank you for using our ATM. Goodbye!")
            return False
        else:
            print("❌ Invalid option. Try again.")
        return True

    def run(self):
        if not self.login():
            return
        while True:
            self.show_menu()
            choice = input("Choose an option: ")
            if not self.handle_choice(choice):
                break


# Run the application
if __name__ == "__main__":
    atm = ATM()
    atm.run()

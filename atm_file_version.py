class UserAccount:
    def __init__(self, card_number, pin, balance):
        self.card_number = card_number
        self.pin = pin
        self.balance = float(balance)

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

    def transfer(self, receiver, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            receiver.balance += amount
            return True
        return False


class ATM:
    def __init__(self):
        self.users = {}
        self.current_user = None
        self.load_users()

    def load_users(self):
        try:
            with open("users.txt", "r") as file:
                for line in file:
                    card, pin, balance = line.strip().split(",")
                    self.users[card] = UserAccount(card, pin, balance)
        except FileNotFoundError:
            print("❌ users.txt not found. Please create it.")

    def save_users(self):
        with open("users.txt", "w") as file:
            for user in self.users.values():
                file.write(f"{user.card_number},{user.pin},{user.balance}\n")

    def login(self):
        print("🔐 Welcome to the File-Based ATM")
        card = input("Enter Card Number: ")
        pin = input("Enter PIN: ")
        user = self.users.get(card)
        if user and user.pin == pin:
            self.current_user = user
            print("✅ Login Successful!\n")
            return True
        else:
            print("❌ Invalid credentials.\n")
            return False

    def show_menu(self):
        print("\n========= ATM MENU =========")
        print("1. Check Balance")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Transfer Funds")
        print("5. Exit")
        print("============================")

    def handle_choice(self, choice):
        if choice == "1":
            print(f"💰 Your balance: ₹{self.current_user.check_balance()}")
        elif choice == "2":
            amount = float(input("Enter deposit amount: ₹"))
            if self.current_user.deposit(amount):
                print("✅ Deposit successful.")
        elif choice == "3":
            amount = float(input("Enter withdrawal amount: ₹"))
            if self.current_user.withdraw(amount):
                print("✅ Withdrawal successful.")
            else:
                print("❌ Insufficient balance.")
        elif choice == "4":
            to_card = input("Enter recipient card number: ")
            amount = float(input("Enter amount to transfer: ₹"))
            receiver = self.users.get(to_card)
            if receiver and self.current_user.transfer(receiver, amount):
                print("✅ Transfer successful.")
            else:
                print("❌ Transfer failed.")
        elif choice == "5":
            self.save_users()  # Save on exit
            print("👋 Thank you for using the ATM.")
            return False
        else:
            print("❌ Invalid option.")
        return True

    def run(self):
        if not self.login():
            return
        while True:
            self.show_menu()
            choice = input("Choose an option: ")
            if not self.handle_choice(choice):
                break


if __name__ == "__main__":
    atm = ATM()
    atm.run()

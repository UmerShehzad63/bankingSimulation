import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import os
from datetime import datetime
import csv
import random
import hashlib

# Custom Exceptions
class BankingException(Exception):
    pass

class InvalidDepositAmountException(BankingException):
    pass

class InvalidWithdrawalAmountException(BankingException):
    pass

class InsufficientFundsException(BankingException):
    pass

class AccountLockedException(BankingException):
    pass

class InvalidIDException(BankingException):
    pass

class MinimumInitialDepositException(BankingException):
    pass

class AccountNotFoundException(BankingException):
    pass

class InvalidAccountTypeException(BankingException):
    pass

class InvalidPasswordException(BankingException):
    pass

class InterestAlreadyAppliedException(BankingException):
    pass

# Transaction Class
class Transaction:
    def __init__(self, trans_type, amount, description):
        self.trans_type = trans_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.description = description

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {self.trans_type} | {self.amount} HUF | {self.description}"

    def to_dict(self):
        return {
            "type": self.trans_type,
            "amount": self.amount,
            "timestamp": self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data):
        trans = cls(data["type"], data["amount"], data["description"])
        trans.timestamp = datetime.strptime(data["timestamp"], '%Y-%m-%d %H:%M:%S')
        return trans

# Savings Account Base Class
class SavingsAccount:
    def __init__(self, id_number, name, initial_deposit, account_type, password):
        if initial_deposit < 1000:
            raise MinimumInitialDepositException("Initial deposit must be at least 1000 HUF")
        self.id_number = id_number
        self.name = name
        self.balance = initial_deposit
        self.account_number = random.randint(100000, 999999)
        self.account_type = account_type
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.transaction_log = [Transaction("Deposit", initial_deposit, "Initial Deposit")]
        self.failed_withdrawals = 0
        self.is_locked = False

    def verify_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidDepositAmountException("Deposit amount must be positive")
        self.balance += amount
        self.transaction_log.append(Transaction("Deposit", amount, "Deposit"))
        return f"Deposited {amount} HUF"

    def withdraw(self, amount):
        if self.is_locked:
            raise AccountLockedException("Account is locked due to multiple failed withdrawals")
        if amount <= 0:
            raise InvalidWithdrawalAmountException("Withdrawal amount must be positive")
        if self.balance - amount < 100:
            self.failed_withdrawals += 1
            if self.failed_withdrawals >= 3:
                self.is_locked = True
                raise AccountLockedException("Account locked after 3 failed withdrawals")
            raise InsufficientFundsException("Insufficient funds: Balance cannot go below 100 HUF")
        self.balance -= amount
        self.transaction_log.append(Transaction("Withdrawal", -amount, "Withdrawal"))
        return f"Withdrew {amount} HUF"

    def apply_interest(self):
        raise NotImplementedError

    def to_dict(self):
        return {
            "id_number": self.id_number,
            "name": self.name,
            "balance": self.balance,
            "account_number": self.account_number,
            "account_type": self.account_type,
            "password_hash": self.password_hash,
            "transaction_log": [trans.to_dict() for trans in self.transaction_log],
            "failed_withdrawals": self.failed_withdrawals,
            "is_locked": self.is_locked
        }

    @classmethod
    def from_dict(cls, data):
        account_class = BasicAccount if data["account_type"] == "Basic" else PremiumAccount
        account = account_class(
            data["id_number"],
            data["name"],
            data["balance"],
            data["account_type"],
            ""  # Password not needed for loading; hash is stored
        )
        account.balance = data["balance"]
        account.account_number = data["account_number"]
        account.password_hash = data["password_hash"]
        account.transaction_log = [Transaction.from_dict(trans) for trans in data["transaction_log"]]
        account.failed_withdrawals = data["failed_withdrawals"]
        account.is_locked = data["is_locked"]
        return account

# Basic and Premium Account Subclasses
class BasicAccount(SavingsAccount):
    def apply_interest(self):
        interest = self.balance * 0.02
        self.balance += interest
        self.transaction_log.append(Transaction("Interest", interest, "2% Interest Applied"))
        return f"Applied 2% interest: {interest} HUF"

class PremiumAccount(SavingsAccount):
    def apply_interest(self):
        interest = self.balance * 0.04
        self.balance += interest
        self.transaction_log.append(Transaction("Interest", interest, "4% Interest Applied"))
        return f"Applied 4% interest: {interest} HUF"

# Bank System Class
class BankSystem:
    def __init__(self):
        self.accounts = {}
        self.account_numbers = set()
        self.load_data()

    def create_account(self, id_number, name, initial_deposit, account_type, password):
        if id_number in self.accounts:
            raise InvalidIDException("ID number already exists")
        if not password:
            raise InvalidPasswordException("Password cannot be empty")
        if account_type not in ["Basic", "Premium"]:
            raise InvalidAccountTypeException("Account type must be Basic or Premium")
        account_class = BasicAccount if account_type == "Basic" else PremiumAccount
        account = account_class(id_number, name, initial_deposit, account_type, password)
        while account.account_number in self.account_numbers:
            account.account_number = random.randint(100000, 999999)
        self.accounts[id_number] = account
        self.account_numbers.add(account.account_number)
        self.save_data()
        return account

    def login(self, id_number, password):
        if id_number not in self.accounts:
            raise InvalidIDException("ID number not found")
        account = self.accounts[id_number]
        if not account.verify_password(password):
            raise InvalidPasswordException("Incorrect password")
        return account

    def get_account(self, id_number):
        if id_number not in self.accounts:
            raise AccountNotFoundException("Account not found")
        return self.accounts[id_number]

    def remove_account(self, id_number):
        if id_number not in self.accounts:
            raise AccountNotFoundException("Account not found")
        account = self.accounts[id_number]
        withdraw_amount = 0
        if account.balance > 100:
            withdraw_amount = account.balance - 100
            account.withdraw(withdraw_amount)
        self.account_numbers.remove(account.account_number)
        del self.accounts[id_number]
        self.save_data()
        return f"Account {account.account_number} removed, {withdraw_amount} HUF withdrawn"

    def save_data(self):
        with open("bank_data.txt", "w") as f:
            for account in self.accounts.values():
                account_data = account.to_dict()
                f.write(str(account_data) + "\n")

    def load_data(self):
        if os.path.exists("bank_data.txt"):
            with open("bank_data.txt", "r") as f:
                for line in f:
                    try:
                        account_data = eval(line.strip())  # Safely parse the dictionary
                        account = SavingsAccount.from_dict(account_data)
                        self.accounts[account.id_number] = account
                        self.account_numbers.add(account.account_number)
                    except Exception as e:
                        print(f"Error loading account data: {e}")

    def export_transactions(self, account):
        filename = f"transactions_{account.account_number}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Account Number", "Date/Time", "Action", "Amount", "Description"])
            for trans in account.transaction_log:
                writer.writerow([
                    account.account_number,
                    trans.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    trans.trans_type,
                    trans.amount,
                    trans.description
                ])
        return filename

# Tkinter GUI with ttkbootstrap
class BankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Banking Simulation")
        self.bank = BankSystem()
        self.current_account = None
        self.interest_applied = False
        self.setup_gui()

    def setup_gui(self):
        self.root.geometry("900x700")
        self.style = ttk.Style("darkly")  # Use ttkbootstrap dark theme
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        # Login Frame
        self.login_frame = ttk.LabelFrame(self.main_frame, text="Account Management", padding="10", bootstyle="primary")
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        self.login_frame.columnconfigure(1, weight=1)

        ttk.Label(self.login_frame, text="ID Number:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.id_entry = ttk.Entry(self.login_frame, font=("Helvetica", 11))
        self.id_entry.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))

        ttk.Label(self.login_frame, text="Password:", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.password_entry = ttk.Entry(self.login_frame, show="*", font=("Helvetica", 11))
        self.password_entry.grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))

        ttk.Label(self.login_frame, text="Full Name:", font=("Helvetica", 11)).grid(row=2, column=0, padx=5, pady=2, sticky=tk.W)
        self.name_entry = ttk.Entry(self.login_frame, font=("Helvetica", 11))
        self.name_entry.grid(row=2, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))

        ttk.Label(self.login_frame, text="Initial Deposit:", font=("Helvetica", 11)).grid(row=3, column=0, padx=5, pady=2, sticky=tk.W)
        self.deposit_entry = ttk.Entry(self.login_frame, font=("Helvetica", 11))
        self.deposit_entry.grid(row=3, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))

        ttk.Label(self.login_frame, text="Account Type:", font=("Helvetica", 11)).grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        self.account_type = ttk.Combobox(self.login_frame, values=["Basic", "Premium"], state="readonly", font=("Helvetica", 11))
        self.account_type.grid(row=4, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
        self.account_type.set("Basic")

        ttk.Button(self.login_frame, text="Login", command=self.login, bootstyle="success-outline").grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(self.login_frame, text="Create Account", command=self.create_account, bootstyle="primary-outline").grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # Transaction Frame
        self.trans_frame = ttk.LabelFrame(self.main_frame, text="Transactions", padding="10", bootstyle="primary")
        self.trans_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.trans_frame.columnconfigure(1, weight=1)

        ttk.Label(self.trans_frame, text="Amount:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=2, sticky=tk.W)
        self.amount_entry = ttk.Entry(self.trans_frame, font=("Helvetica", 11))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))

        button_frame = ttk.Frame(self.trans_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(button_frame, text="Deposit", command=self.deposit, bootstyle="success").grid(row=0, column=0, padx=3)
        ttk.Button(button_frame, text="Withdraw", command=self.withdraw, bootstyle="warning").grid(row=0, column=1, padx=3)
        self.interest_button = ttk.Button(button_frame, text="Apply Interest", command=self.apply_interest, bootstyle="info")
        self.interest_button.grid(row=0, column=2, padx=3)
        ttk.Button(button_frame, text="Export Transactions", command=self.export_transactions, bootstyle="secondary").grid(row=1, column=0, padx=3, pady=3)
        ttk.Button(button_frame, text="Remove Account", command=self.remove_account, bootstyle="danger").grid(row=1, column=1, padx=3, pady=3)
        ttk.Button(button_frame, text="Logout", command=self.logout, bootstyle="danger").grid(row=1, column=2, padx=3, pady=3)

        # Account Info Frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Account Information", padding="10", bootstyle="primary")
        self.info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.rowconfigure(1, weight=1)

        self.balance_label = ttk.Label(self.info_frame, text="Balance: N/A", font=("Helvetica", 12, "bold"))
        self.balance_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)

        self.trans_list = tk.Text(self.info_frame, height=8, width=80, font=("Helvetica", 10))
        self.trans_list.grid(row=1, column=0, padx=5, pady=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(self.info_frame, orient=tk.VERTICAL, command=self.trans_list.yview, bootstyle="primary")
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.trans_list.config(yscrollcommand=scrollbar.set)

        # Status Bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, bootstyle="inverse-dark", padding=5)
        self.status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)

    def login(self):
        try:
            id_number = self.id_entry.get()
            password = self.password_entry.get()
            if not id_number or not password:
                raise InvalidIDException("ID number and password cannot be empty")
            self.current_account = self.bank.login(id_number, password)
            self.interest_applied = False
            self.interest_button.config(state="normal")
            self.update_account_info()
            self.status_var.set(f"Logged in as {self.current_account.name}")
            messagebox.showinfo("Success", f"Logged in as {self.current_account.name}")
        except (InvalidIDException, InvalidPasswordException) as e:
            messagebox.showerror("Error", str(e))

    def create_account(self):
        try:
            id_number = self.id_entry.get()
            password = self.password_entry.get()
            name = self.name_entry.get()
            if not id_number or not name or not password:
                raise InvalidIDException("ID number, name, and password cannot be empty")
            deposit = float(self.deposit_entry.get())
            account_type = self.account_type.get()
            self.current_account = self.bank.create_account(id_number, name, deposit, account_type, password)
            self.interest_applied = False
            self.interest_button.config(state="normal")
            self.update_account_info()
            self.status_var.set(f"Account created for {name}")
            messagebox.showinfo("Success", "Account created successfully")
        except ValueError:
            messagebox.showerror("Error", "Initial deposit must be a valid number")
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def deposit(self):
        if not self.current_account:
            messagebox.showerror("Error", "Please log in to an account")
            return
        try:
            amount = float(self.amount_entry.get())
            message = self.current_account.deposit(amount)
            self.bank.save_data()
            self.update_account_info()
            self.status_var.set(message)
            messagebox.showinfo("Success", message)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number")
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def withdraw(self):
        if not self.current_account:
            messagebox.showerror("Error", "Please log in to an account")
            return
        try:
            amount = float(self.amount_entry.get())
            message = self.current_account.withdraw(amount)
            self.bank.save_data()
            self.update_account_info()
            self.status_var.set(message)
            messagebox.showinfo("Success", message)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a valid number")
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def apply_interest(self):
        if not self.current_account:
            messagebox.showerror("Error", "Please log in to an account")
            return
        try:
            if self.interest_applied:
                raise InterestAlreadyAppliedException("Interest can only be applied once per login session")
            message = self.current_account.apply_interest()
            self.interest_applied = True
            self.interest_button.config(state="disabled")
            self.bank.save_data()
            self.update_account_info()
            self.status_var.set(message)
            messagebox.showinfo("Success", message)
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def export_transactions(self):
        if not self.current_account:
            messagebox.showerror("Error", "Please log in to an account")
            return
        try:
            filename = self.bank.export_transactions(self.current_account)
            self.status_var.set(f"Transactions exported to {filename}")
            messagebox.showinfo("Success", f"Transactions exported to {filename}")
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def remove_account(self):
        if not self.current_account:
            messagebox.showerror("Error", "Please log in to an account")
            return
        try:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to remove this account? This will withdraw all available funds and delete the account.")
            if confirm:
                message = self.bank.remove_account(self.current_account.id_number)
                self.current_account = None
                self.interest_applied = False
                self.interest_button.config(state="normal")
                self.update_account_info()
                self.bank.save_data()
                self.status_var.set(message)
                self.id_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.name_entry.delete(0, tk.END)
                self.deposit_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                messagebox.showinfo("Success", message)
        except BankingException as e:
            messagebox.showerror("Error", str(e))

    def logout(self):
        self.current_account = None
        self.interest_applied = False
        self.interest_button.config(state="normal")
        self.update_account_info()
        self.status_var.set("Logged out")
        self.id_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.deposit_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Logged out successfully")

    def update_account_info(self):
        if self.current_account:
            self.balance_label.config(text=f"Balance: {self.current_account.balance:.2f} HUF")
            self.trans_list.delete(1.0, tk.END)
            for trans in self.current_account.transaction_log:
                self.trans_list.insert(tk.END, str(trans) + "\n")
        else:
            self.balance_label.config(text="Balance: N/A")
            self.trans_list.delete(1.0, tk.END)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = BankingApp(root)
    root.mainloop()
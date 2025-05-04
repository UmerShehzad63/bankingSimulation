**********Banking Simulation**********

**************Overview**************

Banking Simulation is a Python-based application that simulates banking operations with a modern, responsive Tkinter GUI (styled with ttkbootstrap). Users can create and manage Basic or Premium savings accounts, perform deposits and withdrawals, apply interest (2% for Basic, 4% for Premium, once per login session), export transaction history to CSV, and remove accounts. Account data is stored in a human-readable bank_data.txt file, making it ideal for educational demonstrations.

**************Features**************

Create accounts with unique IDs, names, passwords, and account types (Basic or Premium).
Secure login with SHA-256 hashed passwords.
Perform deposits (positive amounts) and withdrawals (minimum balance 100 HUF).
Apply interest once per login session (2% for Basic, 4% for Premium).
Lock accounts after 3 failed withdrawal attempts.
Export transaction history to CSV files.
Remove accounts, automatically withdrawing available funds (minus 100 HUF minimum).
Responsive GUI displaying balance and scrollable transaction history.

**************Setup Instructions**************
Prerequisites
Python 3.8 or higher
Git

**************Installation**************

Clone the repository:git clone https://github.com/UmerShehzad63/bankingSimulation.git

cd bankingSimulation

**************Install required libraries**************

tkinter: Provides the GUI framework. It is included with standard Python installations on Windows and macOS. For Linux (e.g., Ubuntu/Debian), install it with:sudo apt-get update
sudo apt-get install python3-tk
ttkbootstrap: Enhances Tkinter with modern themes. Install via pip:pip install ttkbootstrap

***************Running the Application***************

Run the main script:python banking_simulation.py
The GUI will launch with a dark-themed interface, allowing you to create, manage, or remove accounts.
Account data is saved to bank_data.txt, and transaction history can be exported as transactions_<account_number>.csv.

**************Usage**************

Create Account: Enter ID, name, password, initial deposit (≥1000 HUF), and select Basic/Premium.
Log In: Use ID and password to access an account.
Transactions: Deposit, withdraw, or apply interest (once per session; button disables after use).
Export: Save transaction history to CSV.
Remove Account: Withdraw funds and delete the account.
Log Out: Reset session and interest application.
Check bank_data.txt for account details and tasks.txt for project functionalities.

**************Notes**************

Ensure ttkbootstrap and tkinter are installed for the GUI's dark theme and functionality.
sample_transactions.csv shows the transaction export format.
For issues, confirm Python 3.8+ is installed (python --version) and pip is configured (pip --version).

**************License**************

This project is licensed under the MIT License. See the LICENSE file for details.

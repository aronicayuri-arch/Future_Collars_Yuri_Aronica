from ast import literal_eval

# ─────────────────────────────────────────
#  Simple Accounting System - Extended
#  Uses a Manager class with decorators
#  to handle all accounting operations
# ─────────────────────────────────────────

DB_FILE = "accounting_db.txt"


# ─────────────────────────────────────────
#  MANAGER CLASS
# ─────────────────────────────────────────

class Manager:
    """
    Manages the accounting system.
    - Loads and saves data to a file
    - Uses decorators to add logging to each operation
    - Uses assign() to map command strings to methods
    """

    def __init__(self):
        # Load data from file at startup
        self.balance, self.warehouse, self.operations = self._load()

        # assign() maps command names → methods
        # This dict is built after all methods are defined (see bottom of __init__)
        self._commands = {
            "balance":   self.cmd_balance,
            "sale":      self.cmd_sale,
            "purchase":  self.cmd_purchase,
            "account":   self.cmd_account,
            "list":      self.cmd_list,
            "warehouse": self.cmd_warehouse,
            "review":    self.cmd_review,
            "end":       self.cmd_end,
        }

    # ─────────────────────────────────────
    #  DECORATOR
    #  Logs every operation to self.operations
    # ─────────────────────────────────────

    def log_operation(self, func):
        """
        Decorator that wraps a command method.
        Prints a separator before each command runs,
        making it easy to see where each operation starts.

        Usage:
            @self.log_operation   ← not used directly here,
                                    applied via assign() instead
        """
        def wrapper(*args, **kwargs):
            print(f"\n── Running: {func.__name__.replace('cmd_', '')} ──")
            return func(*args, **kwargs)
        return wrapper

    # ─────────────────────────────────────
    #  ASSIGN METHOD
    #  Maps a command string to the correct method
    # ─────────────────────────────────────

    def assign(self, command):
        """
        Look up the command string and return the matching method.
        The decorator (log_operation) is applied here dynamically.

        Example:
            action = manager.assign("sale")
            action()   ← runs cmd_sale() with logging
        """
        if command in self._commands:
            # Wrap the method with the decorator before returning it
            return self.log_operation(self._commands[command])
        return None

    # ─────────────────────────────────────
    #  FILE: LOAD & SAVE
    # ─────────────────────────────────────

    def _load(self):
        """Load balance, warehouse and operations from the database file."""
        default = (0, {}, [])
        try:
            with open(DB_FILE, "r") as f:
                lines = f.readlines()

            if len(lines) != 3:
                print("  ⚠ Database file is corrupted. Starting fresh.")
                return default

            balance    = literal_eval(lines[0].strip())
            warehouse  = literal_eval(lines[1].strip())
            operations = literal_eval(lines[2].strip())

            if not isinstance(balance, (int, float)):
                raise ValueError("Invalid balance")
            if not isinstance(warehouse, dict):
                raise ValueError("Invalid warehouse")
            if not isinstance(operations, list):
                raise ValueError("Invalid operations")

            print("  ✔ Data loaded from database.\n")
            return balance, warehouse, operations

        except FileNotFoundError:
            print("  ℹ No database found. Starting fresh.\n")
            return default
        except Exception as e:
            print(f"  ⚠ Error reading database ({e}). Starting fresh.\n")
            return default

    def _save(self):
        """Save balance, warehouse and operations to the database file."""
        try:
            with open(DB_FILE, "w") as f:
                f.write(repr(self.balance)    + "\n")
                f.write(repr(self.warehouse)  + "\n")
                f.write(repr(self.operations) + "\n")
            print("  ✔ Data saved to database.")
        except Exception as e:
            print(f"  ✖ Error saving data: {e}")

    # ─────────────────────────────────────
    #  COMMAND METHODS
    #  Each command is a method of the Manager class
    # ─────────────────────────────────────

    def cmd_balance(self):
        """Change the account balance by a given amount."""
        amount_str = input("Enter amount to change the balance (+ or -): ")
        if amount_str.lstrip("+-").isdigit():
            amount = int(amount_str)
            self.balance = self.balance + amount
            self.operations.append("Balance change " + str(amount))
            print("Balance updated.")
        else:
            print("Invalid amount, must be a number.")

    def cmd_sale(self):
        """Sell a product from the warehouse."""
        product   = input("Product name: ")
        price_str = input("Price: ")
        qty_str   = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty   = int(qty_str)

            if product in self.warehouse and self.warehouse[product]["qty"] >= qty:
                total = price * qty
                self.balance = self.balance + total
                self.warehouse[product]["qty"] = self.warehouse[product]["qty"] - qty
                self.operations.append("Sale " + product + " " + str(price) + " " + str(qty))
                print("Sale completed.")
            else:
                print("Not enough product in warehouse.")
        else:
            print("Invalid price or quantity.")

    def cmd_purchase(self):
        """Purchase a product and add it to the warehouse."""
        product   = input("Product name: ")
        price_str = input("Price: ")
        qty_str   = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty   = int(qty_str)
            total = price * qty

            if self.balance >= total:
                self.balance = self.balance - total
                if product not in self.warehouse:
                    self.warehouse[product] = {"price": price, "qty": 0}
                self.warehouse[product]["qty"] = self.warehouse[product]["qty"] + qty
                self.operations.append("Purchase " + product + " " + str(price) + " " + str(qty))
                print("Purchase completed.")
            else:
                print("Not enough balance.")
        else:
            print("Invalid price or quantity.")

    def cmd_account(self):
        """Display the current balance."""
        print("Current balance:", self.balance)

    def cmd_list(self):
        """List all products in the warehouse."""
        if len(self.warehouse) == 0:
            print("Warehouse is empty.")
        else:
            print("Warehouse inventory:")
            for p in self.warehouse:
                print(p, "Price:", self.warehouse[p]["price"], "Qty:", self.warehouse[p]["qty"])

    def cmd_warehouse(self):
        """Display details of a single product."""
        product = input("Enter product name: ")
        if product in self.warehouse:
            print(product, "Price:", self.warehouse[product]["price"], "Qty:", self.warehouse[product]["qty"])
        else:
            print("Product not found.")

    def cmd_review(self):
        """Review the operations history."""
        print("Enter from index (or blank):")
        fr = input()
        print("Enter to index (or blank):")
        to = input()

        if fr == "" and to == "":
            for i in range(len(self.operations)):
                print(i, self.operations[i])
        else:
            if fr.isdigit() and to.isdigit():
                fr_i = int(fr)
                to_i = int(to)
                if fr_i >= 0 and to_i < len(self.operations) and fr_i <= to_i:
                    for i in range(fr_i, to_i + 1):
                        print(i, self.operations[i])
                else:
                    print("Index range out of bounds.")
            else:
                print("Invalid indices.")

    def cmd_end(self):
        """Save data and terminate the program."""
        self._save()
        print("Program terminated.")

    # ─────────────────────────────────────
    #  RUN: MAIN LOOP
    # ─────────────────────────────────────

    def run(self):
        """Start the main loop of the accounting system."""
        print("Available commands:")
        print("balance  sale  purchase  account  list  warehouse  review  end")

        while True:
            command = input("\nEnter command: ").strip().lower()

            # Use assign() to get the correct method (with decorator applied)
            action = self.assign(command)

            if action is not None:
                action()  # Run the command
                if command == "end":
                    break  # Exit the loop after saving
            else:
                print("Unknown command.")


# ─────────────────────────────────────────
#  START THE PROGRAM
# ─────────────────────────────────────────

manager = Manager()
manager.run()

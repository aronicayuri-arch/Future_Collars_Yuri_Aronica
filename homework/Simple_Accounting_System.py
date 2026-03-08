from ast import literal_eval

# ─────────────────────────────────────────
#  File paths for the text database
# ─────────────────────────────────────────
DB_FILE = "accounting_db.txt"

# ─────────────────────────────────────────
#  LOAD DATA FROM FILE
# ─────────────────────────────────────────
def load_data():
    """Load balance, warehouse and operations from the database file.
    Returns default values if file doesn't exist or is corrupted."""
    default = (0, {}, [])
    try:
        with open(DB_FILE, "r") as f:
            lines = f.readlines()

        # File must have exactly 3 lines
        if len(lines) != 3:
            print("  ⚠ Database file is corrupted. Starting fresh.")
            return default

        balance    = literal_eval(lines[0].strip())
        warehouse  = literal_eval(lines[1].strip())
        operations = literal_eval(lines[2].strip())

        # Basic type validation
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


# ─────────────────────────────────────────
#  SAVE DATA TO FILE
# ─────────────────────────────────────────
def save_data(balance, warehouse, operations):
    """Save balance, warehouse and operations to the database file."""
    try:
        with open(DB_FILE, "w") as f:
            f.write(repr(balance)    + "\n")
            f.write(repr(warehouse)  + "\n")
            f.write(repr(operations) + "\n")
        print("  ✔ Data saved to database.")
    except Exception as e:
        print(f"  ✖ Error saving data: {e}")


# ─────────────────────────────────────────
#  LOAD STATE AT STARTUP
# ─────────────────────────────────────────
balance, warehouse, operations = load_data()

# Show available commands
print("Available commands:")
print("balance  sale  purchase  account  list  warehouse  review  end")

command = ""

# ─────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────
while command != "end":
    command = input("\nEnter command: ").strip().lower()

    # balance
    if command == "balance":
        amount_str = input("Enter amount to change the balance (+ or -): ")
        if amount_str.lstrip("+-").isdigit():
            amount = int(amount_str)
            balance = balance + amount
            operations.append("Balance change " + str(amount))
            print("Balance updated.")
        else:
            print("Invalid amount, must be a number.")

    # sale
    elif command == "sale":
        product = input("Product name: ")
        price_str = input("Price: ")
        qty_str = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty = int(qty_str)

            if product in warehouse and warehouse[product]["qty"] >= qty:
                total = price * qty
                balance = balance + total
                warehouse[product]["qty"] = warehouse[product]["qty"] - qty
                operations.append("Sale " + product + " " + str(price) + " " + str(qty))
                print("Sale completed.")
            else:
                print("Not enough product in warehouse.")
        else:
            print("Invalid price or quantity.")

    # purchase
    elif command == "purchase":
        product = input("Product name: ")
        price_str = input("Price: ")
        qty_str = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty = int(qty_str)
            total = price * qty

            if balance >= total:
                balance = balance - total
                if product not in warehouse:
                    warehouse[product] = {"price": price, "qty": 0}
                warehouse[product]["qty"] = warehouse[product]["qty"] + qty
                operations.append("Purchase " + product + " " + str(price) + " " + str(qty))
                print("Purchase completed.")
            else:
                print("Not enough balance.")
        else:
            print("Invalid price or quantity.")

    # account
    elif command == "account":
        print("Current balance:", balance)

    # list
    elif command == "list":
        if len(warehouse) == 0:
            print("Warehouse is empty.")
        else:
            print("Warehouse inventory:")
            for p in warehouse:
                print(p, "Price:", warehouse[p]["price"], "Qty:", warehouse[p]["qty"])

    # warehouse
    elif command == "warehouse":
        product = input("Enter product name: ")
        if product in warehouse:
            print(product, "Price:", warehouse[product]["price"], "Qty:", warehouse[product]["qty"])
        else:
            print("Product not found.")

    # review
    elif command == "review":
        print("Enter from index (or blank):")
        fr = input()
        print("Enter to index (or blank):")
        to = input()

        if fr == "" and to == "":
            for i in range(len(operations)):
                print(i, operations[i])
        else:
            if fr.isdigit() and to.isdigit():
                fr_i = int(fr)
                to_i = int(to)
                if fr_i >= 0 and to_i < len(operations) and fr_i <= to_i:
                    for i in range(fr_i, to_i + 1):
                        print(i, operations[i])
                else:
                    print("Index range out of bounds.")
            else:
                print("Invalid indices.")

    # end
    elif command == "end":
        save_data(balance, warehouse, operations)
        print("Program terminated.")

    # unknown
    else:
        print("Unknown command.")

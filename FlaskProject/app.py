from flask import Flask, render_template, request, redirect, url_for
from ast import literal_eval

# ─────────────────────────────────────────
#  Accounting Web App - Backend
#  Flask routes for all pages and forms
# ─────────────────────────────────────────

app = Flask(__name__)

DB_FILE = "accounting_db.txt"


# ─────────────────────────────────────────
#  FILE: LOAD & SAVE
# ─────────────────────────────────────────

def load_data():
    """Load balance, warehouse and operations from file."""
    default = (0, {}, [])
    try:
        with open(DB_FILE, "r") as f:
            lines = f.readlines()
        if len(lines) != 3:
            return default
        balance    = literal_eval(lines[0].strip())
        warehouse  = literal_eval(lines[1].strip())
        operations = literal_eval(lines[2].strip())
        return balance, warehouse, operations
    except FileNotFoundError:
        return default
    except Exception:
        return default


def save_data(balance, warehouse, operations):
    """Save balance, warehouse and operations to file."""
    try:
        with open(DB_FILE, "w") as f:
            f.write(repr(balance)    + "\n")
            f.write(repr(warehouse)  + "\n")
            f.write(repr(operations) + "\n")
    except Exception as e:
        print("Error saving data:", e)


# ─────────────────────────────────────────
#  ROUTE: HOME / DASHBOARD
# ─────────────────────────────────────────

@app.route("/")
def index():
    """Main page — shows balance and total stock."""
    balance, warehouse, operations = load_data()

    # Calculate total stock items
    total_stock = sum(p["qty"] for p in warehouse.values())

    return render_template("index.html", balance=balance, total_stock=total_stock)


# ─────────────────────────────────────────
#  ROUTE: PURCHASE FORM
# ─────────────────────────────────────────

@app.route("/purchase/", methods=["GET", "POST"])
def purchase():
    """Purchase form — GET shows the form, POST handles submission."""
    error = None
    success = None

    if request.method == "POST":
        # Read form data
        product   = request.form.get("productName", "").strip()
        price_str = request.form.get("unitPrice", "").strip()
        qty_str   = request.form.get("pieces", "").strip()

        # Validate inputs
        if not product:
            error = "Product name is required."
        elif not price_str or not qty_str:
            error = "Please fill in all fields."
        else:
            try:
                price = float(price_str)
                qty   = int(qty_str)

                if price < 0:
                    error = "Unit price must be a positive number."
                elif qty < 1:
                    error = "Quantity must be at least 1."
                else:
                    # Load, update and save data
                    balance, warehouse, operations = load_data()
                    total = price * qty

                    if balance < total:
                        error = "Not enough balance to complete this purchase."
                    else:
                        balance = balance - total
                        if product not in warehouse:
                            warehouse[product] = {"price": price, "qty": 0}
                        warehouse[product]["qty"] = warehouse[product]["qty"] + qty
                        operations.append("Purchase " + product + " " + str(price) + " " + str(qty))
                        save_data(balance, warehouse, operations)
                        success = "Purchase completed! Bought " + str(qty) + "x " + product + " for €" + str(round(total, 2))

            except ValueError:
                error = "Price and quantity must be valid numbers."

    return render_template("purchase.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: SALE FORM
# ─────────────────────────────────────────

@app.route("/sale/", methods=["GET", "POST"])
def sale():
    """Sale form — GET shows the form, POST handles submission."""
    error = None
    success = None

    if request.method == "POST":
        product   = request.form.get("productName", "").strip()
        price_str = request.form.get("unitPrice", "").strip()
        qty_str   = request.form.get("pieces", "").strip()

        if not product:
            error = "Product name is required."
        elif not price_str or not qty_str:
            error = "Please fill in all fields."
        else:
            try:
                price = float(price_str)
                qty   = int(qty_str)

                if price < 0:
                    error = "Unit price must be a positive number."
                elif qty < 1:
                    error = "Quantity must be at least 1."
                else:
                    balance, warehouse, operations = load_data()

                    if product not in warehouse:
                        error = "Product '" + product + "' not found in warehouse."
                    elif warehouse[product]["qty"] < qty:
                        error = "Not enough stock. Available: " + str(warehouse[product]["qty"])
                    else:
                        total = price * qty
                        balance = balance + total
                        warehouse[product]["qty"] = warehouse[product]["qty"] - qty
                        operations.append("Sale " + product + " " + str(price) + " " + str(qty))
                        save_data(balance, warehouse, operations)
                        success = "Sale completed! Sold " + str(qty) + "x " + product + " for €" + str(round(total, 2))

            except ValueError:
                error = "Price and quantity must be valid numbers."

    return render_template("sale.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: BALANCE CHANGE FORM
# ─────────────────────────────────────────

@app.route("/balance/", methods=["GET", "POST"])
def balance_change():
    """Balance change form — GET shows the form, POST handles submission."""
    error = None
    success = None

    if request.method == "POST":
        operation  = request.form.get("operation", "add")
        amount_str = request.form.get("amount", "").strip()

        if not amount_str:
            error = "Amount is required."
        else:
            try:
                amount = float(amount_str)

                if amount <= 0:
                    error = "Amount must be greater than 0."
                else:
                    balance, warehouse, operations = load_data()

                    if operation == "subtract":
                        if balance < amount:
                            error = "Not enough balance to subtract €" + str(amount)
                        else:
                            balance = balance - amount
                            operations.append("Balance change -" + str(amount))
                            save_data(balance, warehouse, operations)
                            success = "Balance updated! Subtracted €" + str(round(amount, 2)) + ". New balance: €" + str(round(balance, 2))
                    else:
                        balance = balance + amount
                        operations.append("Balance change +" + str(amount))
                        save_data(balance, warehouse, operations)
                        success = "Balance updated! Added €" + str(round(amount, 2)) + ". New balance: €" + str(round(balance, 2))

            except ValueError:
                error = "Amount must be a valid number."

    return render_template("balance_change.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: HISTORY PAGE
#  /history/
#  /history/<line_from>/<line_to>/
# ─────────────────────────────────────────

@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — shows all or filtered operations."""
    balance, warehouse, operations = load_data()

    error = None

    if line_from is None and line_to is None:
        # No parameters — show all
        displayed = list(enumerate(operations))
    else:
        # Validate range
        if line_from < 0 or line_to >= len(operations) or line_from > line_to:
            error = "Invalid range. From: " + str(line_from) + " To: " + str(line_to) + " (max: " + str(len(operations) - 1) + ")"
            displayed = list(enumerate(operations))
        else:
            displayed = list(enumerate(operations))[line_from:line_to + 1]

    return render_template("history.html",
                           operations=displayed,
                           line_from=line_from,
                           line_to=line_to,
                           error=error)


# ─────────────────────────────────────────
#  RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)

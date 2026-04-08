from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# ─────────────────────────────────────────
#  Accounting Web App - Backend
#  Flask routes for all pages and forms
#  Uses SQLite database via Flask-SQLAlchemy
# ─────────────────────────────────────────

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///accounting.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ─────────────────────────────────────────
#  DATABASE MODELS
# ─────────────────────────────────────────

class Balance(db.Model):
    """Stores the current account balance (single row)."""
    id     = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)


class Product(db.Model):
    """Stores warehouse products."""
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), unique=True, nullable=False)
    price    = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)


class Transaction(db.Model):
    """Stores all operations history."""
    id          = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────
#  HELPER: Get or create balance row
# ─────────────────────────────────────────

def get_balance():
    """Get current balance. Creates it with 0 if it doesn't exist yet."""
    balance = Balance.query.first()
    if balance is None:
        balance = Balance(amount=0.0)
        db.session.add(balance)
        db.session.commit()
    return balance


# ─────────────────────────────────────────
#  ROUTE: HOME / DASHBOARD
# ─────────────────────────────────────────

@app.route("/")
def index():
    """Main page — shows real balance and total stock from database."""
    try:
        balance     = get_balance()
        total_stock = db.session.query(db.func.sum(Product.quantity)).scalar() or 0
        return render_template("index.html", balance=balance.amount, total_stock=total_stock)
    except Exception as e:
        return render_template("index.html", balance=0, total_stock=0, error="Database error: " + str(e))


# ─────────────────────────────────────────
#  ROUTE: PURCHASE FORM
# ─────────────────────────────────────────

@app.route("/purchase/", methods=["GET", "POST"])
def purchase():
    """Purchase form — GET shows the form, POST handles submission."""
    error   = None
    success = None

    if request.method == "POST":
        product_name = request.form.get("productName", "").strip()
        price_str    = request.form.get("unitPrice", "").strip()
        qty_str      = request.form.get("pieces", "").strip()

        if not product_name:
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
                    total   = price * qty
                    balance = get_balance()

                    if balance.amount < total:
                        error = "Not enough balance. Available: €" + str(round(balance.amount, 2))
                    else:
                        balance.amount = balance.amount - total
                        product = Product.query.filter_by(name=product_name).first()
                        if product is None:
                            product = Product(name=product_name, price=price, quantity=qty)
                            db.session.add(product)
                        else:
                            product.quantity = product.quantity + qty
                            product.price    = price
                        t = Transaction(description="Purchase " + product_name + " " + str(price) + " x" + str(qty))
                        db.session.add(t)
                        db.session.commit()
                        success = "Purchase completed! Bought " + str(qty) + "x " + product_name + " for €" + str(round(total, 2))

            except ValueError:
                error = "Price and quantity must be valid numbers."
            except Exception as e:
                db.session.rollback()
                error = "Database error: " + str(e)

    return render_template("purchase.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: SALE FORM
# ─────────────────────────────────────────

@app.route("/sale/", methods=["GET", "POST"])
def sale():
    """Sale form — GET shows the form, POST handles submission."""
    error   = None
    success = None

    if request.method == "POST":
        product_name = request.form.get("productName", "").strip()
        price_str    = request.form.get("unitPrice", "").strip()
        qty_str      = request.form.get("pieces", "").strip()

        if not product_name:
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
                    product = Product.query.filter_by(name=product_name).first()

                    if product is None:
                        error = "Product '" + product_name + "' not found in warehouse."
                    elif product.quantity < qty:
                        error = "Not enough stock. Available: " + str(product.quantity)
                    else:
                        total   = price * qty
                        balance = get_balance()
                        balance.amount   = balance.amount + total
                        product.quantity = product.quantity - qty
                        t = Transaction(description="Sale " + product_name + " " + str(price) + " x" + str(qty))
                        db.session.add(t)
                        db.session.commit()
                        success = "Sale completed! Sold " + str(qty) + "x " + product_name + " for €" + str(round(total, 2))

            except ValueError:
                error = "Price and quantity must be valid numbers."
            except Exception as e:
                db.session.rollback()
                error = "Database error: " + str(e)

    return render_template("sale.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: BALANCE CHANGE FORM
# ─────────────────────────────────────────

@app.route("/balance/", methods=["GET", "POST"])
def balance_change():
    """Balance change form — GET shows the form, POST handles submission."""
    error   = None
    success = None

    if request.method == "POST":
        operation  = request.form.get("operation", "add")
        amount_str = request.form.get("amount", "").strip()
@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — shows all or filtered transactions from database."""
    operations = [t.description for t in Transaction.query.all()]
    error = None

    if line_from is None and line_to is None:
        displayed = list(enumerate(operations))
    else:
        if line_from < 0 or line_to >= len(operations) or line_from > line_to:
            error = "Invalid range..."
            displayed = list(enumerate(operations))
        else:
            displayed = list(enumerate(operations))[line_from:line_to + 1]

    return render_template("history.html", operations=displayed,
                           line_from=line_from, line_to=line_to, error=error)
            except Exception as e:
                db.session.rollback()
                error = "Database error: " + str(e)

    return render_template("balance_change.html", error=error, success=success)


# ─────────────────────────────────────────
#  ROUTE: HISTORY PAGE
#  /history/
#  /history/<line_from>/<line_to>/
# ─────────────────────────────────────────

@app.route("/history/")
@app.route("/history/<int:line_from>/<int:line_to>/")
def history(line_from=None, line_to=None):
    """History page — shows all or filtered transactions from database."""
    error = None

    try:
        all_transactions = Transaction.query.all()

        if line_from is None and line_to is None:
            # No parameters — show all
            displayed = list(enumerate(t.description for t in all_transactions))
        else:
            total = len(all_transactions)

            if line_from < 0 or line_to >= total or line_from > line_to:
                error     = "Invalid range. Max index: " + str(total - 1)
                displayed = list(enumerate(t.description for t in all_transactions))
            else:
                subset    = all_transactions[line_from:line_to + 1]
                displayed = [(line_from + i, t.description) for i, t in enumerate(subset)]

    except Exception as e:
        error     = "Database error: " + str(e)
        displayed = []

    return render_template("history.html",
                           operations=displayed,
                           line_from=line_from,
                           line_to=line_to,
                           error=error)


# ─────────────────────────────────────────
#  CREATE TABLES & RUN
# ─────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)

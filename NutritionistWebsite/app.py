from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from translations import TRANSLATIONS

app = Flask(__name__)
app.secret_key = "chiara-nutritionist-2026"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookings.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ── Model ──
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(100), nullable=False)
    phone      = db.Column(db.String(30),  nullable=True)
    package    = db.Column(db.String(100), nullable=False)
    message    = db.Column(db.Text,        nullable=True)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)



# ── Inject current year and language into all templates automatically ──
@app.context_processor
def inject_globals():
    return {
        "now": datetime.utcnow(),
        "lang": session.get("lang", "it")
    }

# ── Translation helper ──
def t(key):
    lang = session.get("lang", "it")
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key]["it"])
    return key


# ── Switch language ──
@app.route("/lang/<lang>/")
def set_language(lang):
    if lang in ("it", "en"):
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


# ── Home ──
@app.route("/")
def index():
    return render_template("index.html", t=t, lang=session.get("lang", "it"))


# ── Services ──
@app.route("/services/")
def services():
    return render_template("services.html", t=t, lang=session.get("lang", "it"))


# ── Testimonials ──
@app.route("/testimonials/")
def testimonials():
    return render_template("testimonials.html", t=t, lang=session.get("lang", "it"))


# ── Contact / Booking ──
@app.route("/contact/", methods=["GET", "POST"])
def contact():
    error     = None
    success   = None
    preselect = request.args.get("package", "")

    if request.method == "POST":
        name    = request.form.get("name",    "").strip()
        email   = request.form.get("email",   "").strip()
        phone   = request.form.get("phone",   "").strip()
        package = request.form.get("package", "").strip()
        message = request.form.get("message", "").strip()

        if not name:
            error = "Nome obbligatorio." if session.get("lang", "it") == "it" else "Name is required."
        elif not email or "@" not in email:
            error = "Email non valida." if session.get("lang", "it") == "it" else "Invalid email."
        elif not package:
            error = "Seleziona un pacchetto." if session.get("lang", "it") == "it" else "Please select a package."
        else:
            try:
                booking = Booking(name=name, email=email, phone=phone, package=package, message=message)
                db.session.add(booking)
                db.session.commit()
                success = t("form_success")
            except Exception as e:
                db.session.rollback()
                error = "Errore database: " + str(e)

    return render_template("contact.html", t=t, lang=session.get("lang", "it"),
                           error=error, success=success, preselect=preselect)


# ── Admin ──
@app.route("/admin/")
def admin():
    try:
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    except Exception:
        bookings = []
    return render_template("admin.html", t=t, lang=session.get("lang", "it"), bookings=bookings)


# ── Init DB and run ──
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5002)

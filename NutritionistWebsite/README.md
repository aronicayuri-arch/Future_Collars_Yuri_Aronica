# 🌿 Nutritionist Website — Dott.ssa Chiara Aronica

## About This Project

This website was built as the **final project** of my beginner Python course.

I wanted to create something meaningful and real — so I decided to build a professional website for my sister, **Dott.ssa Chiara Aronica**, who is a nutritionist in her first year of practice. The goal was to help her present herself professionally online and give her clients an easy way to discover her services and book a consultation.

---

## 💡 Motivation

My sister is just starting her career as a nutritionist and needed a way to reach potential clients online. Instead of using a generic website builder, I used the skills I learned during this Python course to build her a custom web application from scratch — something personal, functional, and truly hers.

---

## 🛠️ Technologies Used

- **Python** — core programming language
- **Flask** — web framework for routes and backend logic
- **Flask-SQLAlchemy** — database management with SQLite
- **Jinja2** — HTML templating engine
- **HTML & CSS** — frontend design
- **SQLite** — lightweight database to store booking requests
- **Git & GitHub** — version control and code sharing

---

## ✨ Features

- 🏠 **Home page** — hero section with photo, about section and services preview
- 💼 **Services page** — 3 detailed nutrition programs with prices
- ⭐ **Testimonials page** — client success stories
- 📅 **Booking form** — clients can request a consultation (saved to database)
- 🔒 **Admin panel** — view all booking requests at `/admin/`
- 🌍 **IT / EN language switch** — full Italian and English support

---

## 📚 Python Concepts Applied

| Concept | Where used |
|---|---|
| Variables & functions | Translation helper `t()` |
| Dictionaries | `TRANSLATIONS` dictionary |
| Classes | `Booking` database model |
| Loops & conditionals | Form validation, language switching |
| Exception handling | Database `try/except` blocks |
| File handling | Static files, `.gitignore` |
| Modules & imports | Flask, SQLAlchemy, datetime |
| Sessions | Language preference stored in session |

---

## 🚀 How to Run

1. Install dependencies:
```
pip install Flask flask-sqlalchemy
```

2. Run the app:
```
flask --app app run --port 5002
```

3. Open in browser:
```
http://127.0.0.1:5002
```

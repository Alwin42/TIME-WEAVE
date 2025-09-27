import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'  # replace in production
app.config['DATABASE'] = os.path.join(app.root_path, 'timeweave.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            instructor TEXT NOT NULL,
            room TEXT NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    db.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quick-add", methods=["POST"])
def quick_add():
    course = request.form.get("course", "").strip()
    instructor = request.form.get("instructor", "").strip()
    room = request.form.get("room", "").strip()
    day = request.form.get("day", "").strip()
    start_time = request.form.get("start_time", "").strip()
    end_time = request.form.get("end_time", "").strip()

    if not all([course, instructor, room, day, start_time, end_time]):
        flash("Please fill out all fields.", "error")
        return redirect(url_for("index") + "#quick-add")

    db = get_db()
    db.execute(
        "INSERT INTO entries (course, instructor, room, day, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)",
        (course, instructor, room, day, start_time, end_time)
    )
    db.commit()
    flash("Added to your timetable!", "success")
    return redirect(url_for("timetable"))


@app.route("/timetable")
def timetable():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM entries ORDER BY day, start_time"
    ).fetchall()
    return render_template("timetable.html", entries=rows)


if __name__ == "__main__":
    # Initialize the database once at startup (Flask 3.x compatible)
    with app.app_context():
        init_db()
    app.run(debug=True)
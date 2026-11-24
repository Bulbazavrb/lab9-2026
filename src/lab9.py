"""
Лабораторна робота № 9: Створення простого веб-додатку на Flask
Варіант: 12 («Планувальник подорожей» / Travel Planner)
Студент: Шульга Дмитро Ігорович
Група: 12
"""

import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "travel_planner.db")

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))


def get_db_connection() -> sqlite3.Connection:
    """Встановлює з'єднання з базою даних SQLite та налаштовує повернення рядків як словників."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Створює таблицю trips у базі даних, якщо вона ще не існує."""
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                travel_date TEXT NOT NULL,
                notes TEXT,
                done INTEGER NOT NULL DEFAULT 0
            );
            """
        )
        conn.commit()


@app.route("/")
def index():
    """Головна сторінка: відображення списку запланованих подорожей."""
    with get_db_connection() as conn:
        trips = conn.execute("SELECT * FROM trips ORDER BY done ASC, travel_date ASC;").fetchall()
    return render_template("index.html", trips=trips)


@app.route("/add", methods=["POST"])
def add_trip():
    """Додавання нової подорожі до бази даних через POST-форму."""
    destination = request.form.get("destination", "").strip()
    travel_date = request.form.get("travel_date", "").strip()
    notes = request.form.get("notes", "").strip()

    if destination and travel_date:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO trips (destination, travel_date, notes, done) VALUES (?, ?, ?, 0);",
                (destination, travel_date, notes),
            )
            conn.commit()

    return redirect(url_for("index"))


@app.route("/done/<int:trip_id>")
def toggle_done(trip_id: int):
    """Позначення подорожі як виконаної / відвіданої (або повернення в план)."""
    with get_db_connection() as conn:
        trip = conn.execute("SELECT done FROM trips WHERE id = ?;", (trip_id,)).fetchone()
        if trip is not None:
            new_status = 0 if trip["done"] else 1
            conn.execute("UPDATE trips SET done = ? WHERE id = ?;", (new_status, trip_id))
            conn.commit()

    return redirect(url_for("index"))


@app.route("/delete/<int:trip_id>")
def delete_trip(trip_id: int):
    """Видалення подорожі зі списку."""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM trips WHERE id = ?;", (trip_id,))
        conn.commit()

    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
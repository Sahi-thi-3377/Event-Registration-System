from flask import Flask, request, render_template_string
import sqlite3
import re

app = Flask(__name__)

DATABASE = "events.db"


# Initialize the database
def initialize_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_name TEXT NOT NULL,
            email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            FOREIGN KEY (event_id) REFERENCES events(id),
            UNIQUE (email, event_id)
        )
    """)

    connection.commit()
    connection.close()


# HTML page
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Event Registration System - V2</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 850px;
            margin: auto;
        }

        h1, h2 {
            color: #1e293b;
        }

        .subtitle {
            color: #64748b;
        }

        .card {
            background: white;
            padding: 25px;
            margin-bottom: 25px;
            border-radius: 10px;
            box-shadow: 0 3px 10px #00000012;
        }

        label {
            display: block;
            margin: 15px 0 6px;
            font-weight: bold;
        }

        input, select {
            width: 100%;
            padding: 11px;
            box-sizing: border-box;
            border: 1px solid #cbd5e1;
            border-radius: 5px;
        }

        button {
            margin-top: 20px;
            padding: 12px 20px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background: #1d4ed8;
        }

        .message {
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
        }

        .success {
            background: #dcfce7;
            color: #166534;
        }

        .error {
            background: #fee2e2;
            color: #991b1b;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }

        th {
            background: #e2e8f0;
        }
    </style>
</head>

<body>
<div class="container">

    <h1>Event Registration System</h1>
    <p class="subtitle">Version 2 — Register User</p>

    {% if message %}
        <div class="message {{ message_type }}">
            {{ message }}
        </div>
    {% endif %}

    <div class="card">
        <h2>Create a New Event</h2>

        <form method="POST" action="/create-event">
            <label for="name">Event Name</label>
            <input type="text" id="name" name="name"
                   maxlength="100" required>

            <label for="date">Event Date</label>
            <input type="date" id="date" name="date" required>

            <label for="location">Event Location</label>
            <input type="text" id="location" name="location"
                   maxlength="150" required>

            <button type="submit">Create Event</button>
        </form>
    </div>

    <div class="card">
        <h2>Register for an Event</h2>

        {% if events %}
        <form method="POST" action="/register">

            <label for="participant_name">Participant Name</label>
            <input type="text" id="participant_name"
                   name="participant_name" maxlength="100" required>

            <label for="email">Email Address</label>
            <input type="email" id="email" name="email"
                   maxlength="254" required>

            <label for="event_id">Select Event</label>
            <select id="event_id" name="event_id" required>
                <option value="">-- Select an Event --</option>

                {% for event in events %}
                <option value="{{ event[0] }}">
                    {{ event[1] }} — {{ event[2] }}
                </option>
                {% endfor %}
            </select>

            <button type="submit">Register Now</button>
        </form>
        {% else %}
            <p>Create an event before registering participants.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>Available Events</h2>

        {% if events %}
        <table>
            <tr>
                <th>Event Name</th>
                <th>Date</th>
                <th>Location</th>
            </tr>

            {% for event in events %}
            <tr>
                <td>{{ event[1] }}</td>
                <td>{{ event[2] }}</td>
                <td>{{ event[3] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
            <p>No events created yet.</p>
        {% endif %}
    </div>

</div>
</body>
</html>
"""


def get_events():
    connection = sqlite3.connect(DATABASE)

    events = connection.execute("""
        SELECT id, name, date, location
        FROM events
        ORDER BY id DESC
    """).fetchall()

    connection.close()
    return events


def render_home(message="", message_type="success"):
    return render_template_string(
        HTML_PAGE,
        events=get_events(),
        message=message,
        message_type=message_type
    )


@app.route("/")
def home():
    return render_home()


@app.route("/create-event", methods=["POST"])
def create_event():
    name = request.form.get("name", "").strip()
    event_date = request.form.get("date", "").strip()
    location = request.form.get("location", "").strip()

    if not name or not event_date or not location:
        return render_home(
            "Please fill in all event details.", "error"
        )

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        INSERT INTO events (name, date, location)
        VALUES (?, ?, ?)
    """, (name, event_date, location))

    connection.commit()
    connection.close()

    return render_home("Event created successfully!")


@app.route("/register", methods=["POST"])
def register_user():
    participant_name = request.form.get(
        "participant_name", ""
    ).strip()

    email = request.form.get("email", "").strip().lower()
    event_id = request.form.get("event_id", "").strip()

    if not participant_name or not email or not event_id:
        return render_home(
            "Please fill in all registration details.", "error"
        )

    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return render_home(
            "Please enter a valid email address.", "error"
        )

    try:
        selected_event_id = int(event_id)
    except ValueError:
        return render_home(
            "Please select a valid event.", "error"
        )

    connection = sqlite3.connect(DATABASE)

    event = connection.execute(
        "SELECT id FROM events WHERE id = ?",
        (selected_event_id,)
    ).fetchone()

    if event is None:
        connection.close()
        return render_home(
            "The selected event does not exist.", "error"
        )

    try:
        connection.execute("""
            INSERT INTO registrations
                (participant_name, email, event_id)
            VALUES (?, ?, ?)
        """, (participant_name, email, selected_event_id))

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()
        return render_home(
            "This email is already registered for that event.",
            "error"
        )

    connection.close()

    return render_home(
        f"Registration successful! Welcome, {participant_name}."
    )


if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)

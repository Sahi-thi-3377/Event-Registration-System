from flask import Flask, request, render_template_string
import sqlite3

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

    connection.commit()
    connection.close()

# Web page
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Event Registration System - V1</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 800px;
            margin: auto;
        }

        h1, h2 {
            color: #1e293b;
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

        input {
            width: 100%;
            padding: 10px;
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

        .success {
            background: #dcfce7;
            color: #166534;
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
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

        .subtitle {
            color: #64748b;
        }
    </style>
</head>

<body>
    <div class="container">

        <h1>Event Registration System</h1>
        <p class="subtitle">Version 1 — Create Event</p>

        {% if message %}
            <div class="success">{{ message }}</div>
        {% endif %}

        <div class="card">
            <h2>Create a New Event</h2>

            <form method="POST" action="/">
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
            <h2>Created Events</h2>

            {% if events %}
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Event Name</th>
                        <th>Date</th>
                        <th>Location</th>
                    </tr>

                    {% for event in events %}
                    <tr>
                        <td>{{ event[0] }}</td>
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

# Home page and event creation
@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        event_date = request.form.get("date", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not event_date or not location:
            message = "Please fill in all event details."
        else:
            connection = sqlite3.connect(DATABASE)

            connection.execute(
                """
                INSERT INTO events (name, date, location)
                VALUES (?, ?, ?)
                """,
                (name, event_date, location)
            )

            connection.commit()
            connection.close()

            message = "Event created successfully!"

    connection = sqlite3.connect(DATABASE)

    events = connection.execute(
        """
        SELECT id, name, date, location
        FROM events
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template_string(
        HTML_PAGE,
        events=events,
        message=message
    )

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000, debug=True)

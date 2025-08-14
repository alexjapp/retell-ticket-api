# This example is broken into two parts:
# 1. setup_database.py: A script to create and populate the SQLite database.
# 2. app.py: A Flask API that connects to the database to validate tickets.

# --- Part 1: setup_database.py ---
# You would run this script once to create the 'poc_database.db' file.

import sqlite3
from flask import Flask, jsonify

def setup():
    """
    Creates the database and a table for tickets, then populates it
    with some synthetic data. This is safe to run multiple times.
    """
    conn = sqlite3.connect('poc_database.db')
    cursor = conn.cursor()
    print("Database created and connected successfully.")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL
        )
    ''')
    print("Table 'tickets' created or already exists.")

    synthetic_tickets = [
        ('TICKET-001A', 'Open'),
        ('TICKET-002B', 'In Progress'),
        ('TICKET-003C', 'Closed'),
        ('TICKET-004D', 'Open'),
        ('TICKET-005E', 'Awaiting Technician')
    ]
    cursor.executemany('INSERT OR IGNORE INTO tickets (ticket_number, status) VALUES (?, ?)', synthetic_tickets)
    print(f"{cursor.rowcount} new records inserted into the 'tickets' table.")

    conn.commit()
    conn.close()
    print("Database connection closed.")


# --- Part 2: app.py ---
# This is the main API application.

def create_api_app():
    app = Flask(__name__)

    # This ensures the database is created when the app starts in any environment.
    with app.app_context():
        setup()

    # --- NEW: Add a root route for testing ---
    @app.route('/', methods=['GET'])
    def index():
        """
        A simple root endpoint to confirm the API is running.
        """
        return jsonify({'message': 'Welcome to the Ticket Validation API!'}), 200


    @app.route('/validate_ticket/<string:ticket_number>', methods=['GET'])
    def validate_ticket(ticket_number):
        """
        API endpoint to validate a ticket number.
        It connects to the SQLite database, queries for the ticket,
        and returns its status in a JSON format.
        """
        try:
            conn = sqlite3.connect('poc_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM tickets WHERE ticket_number = ?", (ticket_number,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return jsonify({
                    'success': True,
                    'ticket_number': ticket_number,
                    'status': result[0]
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Ticket number not found.'
                }), 404

        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'An internal error occurred.',
                'error': str(e)
            }), 500

    return app

# This is the main entry point when you run `python app.py`
# We create the app instance here for Gunicorn to find.
app = create_api_app()
    
if __name__ == '__main__':
    # Start the Flask development server for local testing.
    app.run(debug=True)

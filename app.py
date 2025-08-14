# Save this code as app.py

import sqlite3
from flask import Flask, jsonify

# --- Database Setup Function ---
def setup():
    conn = sqlite3.connect('poc_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL
        )
    ''')
    synthetic_tickets = [
        ('TICKET-001A', 'Open'),
        ('TICKET-002B', 'In Progress'),
        ('TICKET-003C', 'Closed'),
        ('TICKET-004D', 'Open'),
        ('TICKET-005E', 'Awaiting Technician')
    ]
    cursor.executemany('INSERT OR IGNORE INTO tickets (ticket_number, status) VALUES (?, ?)', synthetic_tickets)
    conn.commit()
    conn.close()

# --- API Creation Function ---
def create_api_app():
    app = Flask(__name__)

    @app.route('/validate_ticket/<string:ticket_number>', methods=['GET'])
    def validate_ticket(ticket_number):
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

# --- Main Execution Block ---

# This line is moved outside for Azure to find the 'app' object
app = create_api_app()

if __name__ == '__main__':
    setup()
    app.run(debug=True)

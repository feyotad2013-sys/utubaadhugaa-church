import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# --- SECURITY: Use Environment Variables ---
# On Render, set 'FLASK_SECRET_KEY' to a long random string
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_only_for_local_testing')

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect('church.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-prayer', methods=['POST'])
def submit_prayer():
    name = request.form['name']
    phone = request.form['phone']
    message = request.form['message']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (name, phone, message) VALUES (?, ?, ?)',
                 (name, phone, message))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # SECURE: Pulls values from your Render 'Environment' settings
        # Default values ('admin' and 'Utubaa@2026') are only for local testing
        admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'Utubaa@2026')
        
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return "Kallattiin galumsaa sirrii miti! (Incorrect login)"
            
    return render_template('login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('admin.html', messages=messages)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

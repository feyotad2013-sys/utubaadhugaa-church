import os
import sqlite3
from flask import Flask, render_template, request, flash, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "utubaa_secret_key_2026" 

# --- ADMIN CONFIG ---
ADMIN_USER = "admin"
ADMIN_PASS = "Utubaa@2026"

# --- DATABASE STARTUP ---
def init_db():
    conn = sqlite3.connect('church.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-prayer', methods=['POST'])
def submit_prayer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    conn = sqlite3.connect('church.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO requests (name, phone, message) VALUES (?, ?, ?)", (name, phone, message))
    conn.commit()
    conn.close()
    
    flash("Galatoomaa! Ergaan keessan nu qaqqabeera.")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USER and request.form['password'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash("Maqaa ykn Jecha icciitii dogoggora!")
    return render_template('login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('church.db')
    conn.row_factory = sqlite3.Row
    messages = conn.execute('SELECT * FROM requests ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', messages=messages)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- THE PORT LOGIC ---
if __name__ == "__main__":
    # This looks for the Port provided by Render, or uses 5000 for your local computer
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
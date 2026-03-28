import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# --- 1. SECURITY SETTINGS ---
# On Render, set 'FLASK_SECRET_KEY' in Environment Variables
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_2026_utubaa')

# --- 2. DATABASE LOGIC ---
def get_db_connection():
    # Use an absolute path for the database to avoid Render errors
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'church.db')
    conn = sqlite3.connect(db_path)
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

# Initialize database on startup
init_db()

# --- 3. PUBLIC ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit-prayer', methods=['POST'])
def submit_prayer():
    name = request.form.get('name')
    phone = request.form.get('phone')
    message = request.form.get('message')
    
    if name and message:
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (name, phone, message) VALUES (?, ?, ?)',
                     (name, phone, message))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/gallery')
def gallery():
    # This automatically finds all images in your static/gallery folder
    gallery_dir = os.path.join(app.root_path, 'static', 'gallery')
    images = []
    
    if os.path.exists(gallery_dir):
        # Filters for common image types
        images = [f for f in os.listdir(gallery_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    
    return render_template('gallery.html', images=images)

# --- 4. ADMIN & SECURITY ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Pulls from Render Environment Variables for 100% security
        admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'Utubaa@2026')
        
        if username == admin_user and password == admin_pass:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        return "Kallattiin galumsaa sirrii miti! (Incorrect Login)"
            
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

# --- 5. START SERVER ---
if __name__ == '__main__':
    # '0.0.0.0' and port 5000 is standard for most hosting
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response
import sqlite3
from datetime import datetime, timedelta
import uuid

# Initialize Flask application
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "your_secret_key"
SESSION_DURATION_DAYS = 7

# Initialize database and create tables if they don't exist
def init_db():
    con = sqlite3.connect('database.db')
    con.execute('''
        CREATE TABLE IF NOT EXISTS users (
            pid INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            password TEXT
        )
    ''')
    con.execute('''  
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            created_at TEXT,
            expires_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(pid)
        )
    ''')
    con.close()

init_db()

def get_db():
    try:
        con = sqlite3.connect('database.db')
        return con
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_session(user_id, remember_me):
    session_id = str(uuid.uuid4())
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=SESSION_DURATION_DAYS) if remember_me else created_at + timedelta(seconds=30)
    con = get_db()
    if con:
        cur = con.cursor()
        cur.execute("INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)", 
                    (session_id, user_id, created_at, expires_at))
        con.commit()
        con.close()
    return session_id, expires_at

def validate_session(session_id):
    con = get_db()
    if con:
        cur = con.cursor()
        cur.execute("SELECT user_id, expires_at FROM sessions WHERE session_id = ?", (session_id,))
        session_data = cur.fetchone()
        con.close()
        if session_data:
            user_id, expires_at = session_data
            if not expires_at or datetime.now() < datetime.fromisoformat(expires_at):
                return user_id
    return None

@app.before_request
def load_logged_in_user():
    session_id = request.cookies.get('session_id')
    if session_id:
        user_id = validate_session(session_id)
        if user_id:
            session['user_id'] = user_id
            con = get_db()
            if con:
                cur = con.cursor()
                cur.execute("SELECT username FROM users WHERE pid = ?", (user_id,))
                user = cur.fetchone()
                session['username'] = user[0] if user else None
                con.close()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember-me') is not None
        con = get_db()
        if con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cur.fetchone()
            con.close()
            if user and user[3] == password:
                session_id, expires_at = create_session(user[0], remember_me)
                session['user_id'] = user[0]
                session['username'] = user[1]
                response = make_response(redirect(url_for('home')))
                if remember_me:
                    response.set_cookie('session_id', session_id, max_age=SESSION_DURATION_DAYS*24*60*60, httponly=True)
                else:
                    response.set_cookie('session_id', session_id, httponly=True)
                flash("Successfully logged in!", "success")
                return response
            else:
                flash("Invalid email or password", "error")
        else:
            flash("Failed to connect to the database", "error")
    return render_template("login.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for('register'))
        
        con = get_db()
        if con:
            try:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
                con.commit()
                flash("You have been registered successfully", "success")
            except sqlite3.Error as e:
                flash(f"Error in registration: {e}")
            finally:
                con.close()
        else:
            flash("Failed to connect to the database", "error")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/profile')
def profile():
    if 'user_id' in session:
        return render_template('profile.html')
    else:
        flash("Please log in to view your profile", "error")
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session_id = request.cookies.get('session_id')
    if session_id:
        con = get_db()
        if con:
            cur = con.cursor()
            cur.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            con.commit()
            con.close()
    session.pop('user_id', None)
    session.pop('username', None)
    response = make_response(redirect(url_for('home')))
    response.set_cookie('session_id', '', expires=0)
    flash("You have been logged out", "success")
    return response

if __name__ == '__main__':
    app.run(debug=True)

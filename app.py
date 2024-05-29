from flask import Flask, render_template, redirect, url_for, request, flash, session, make_response
import sqlite3
from datetime import datetime, timedelta, timezone
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "emauehjgk"
SESSION_DURATION_DAYS = 7

def init_db():
    con = sqlite3.connect('database.db')
    con.execute('''
    CREATE TABLE IF NOT EXISTS users (
        pid INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        user_type TEXT NOT NULL
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
    con.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            label TEXT,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            FOREIGN KEY(user_id) REFERENCES users(pid)
        )
    ''')
    con.execute('''
    CREATE TABLE IF NOT EXISTS shipments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        courier_id INTEGER,
        sender_name TEXT,
        sender_address TEXT,
        recipient_name TEXT,
        recipient_address TEXT,
        status TEXT,
        shipment_code TEXT,
        FOREIGN KEY(user_id) REFERENCES users(pid),
        FOREIGN KEY(courier_id) REFERENCES users(pid)
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
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(days=SESSION_DURATION_DAYS) if remember_me else created_at + timedelta(seconds=30)
    con = get_db()
    if con:
        cur = con.cursor()
        cur.execute("INSERT INTO sessions (session_id, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)", 
                    (session_id, user_id, created_at.isoformat(), expires_at.isoformat()))
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
            if not expires_at or datetime.now(timezone.utc) < datetime.fromisoformat(expires_at).astimezone(timezone.utc):
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
                cur.execute("SELECT username, user_type FROM users WHERE pid = ?", (user_id,))
                user = cur.fetchone()
                if user:
                    session['username'] = user[0]
                    session['user_type'] = user[1]
                con.close()

@app.route('/')
def home():
    if 'user_id' in session:
        if session.get('user_type') == 'customer':
            return redirect(url_for('customer_home'))
        elif session.get('user_type') == 'courier':
            return redirect(url_for('courier_home'))
    return render_template('index.html')

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
            cur.execute("SELECT * FROM users WHERE email =?", (email,))
            user = cur.fetchone()
            con.close()
            if user and check_password_hash(user[3], password):
                session_id, expires_at = create_session(user[0], remember_me)
                session['user_id'] = user[0]
                session['username'] = user[1]
                session['user_type'] = user[4]
                response = make_response(redirect(url_for('home')))
                max_age = None if not remember_me else SESSION_DURATION_DAYS * 24 * 60 * 60
                response.set_cookie('session_id', session_id, max_age=max_age, httponly=True)
                flash("Successfully logged in!", "success")
                return response
            else:
                flash("Invalid email or password", "error")
        else:
            flash("Failed to connect to the database", "error")
    return render_template("login.html")

@app.route('/customer-home')
def customer_home():
    if 'user_id' in session:
        user_id = session['user_id']
        
        con = get_db()
        addresses = []
        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    SELECT label, address, city, postal_code, id
                    FROM addresses
                    WHERE user_id = ?
                ''', (user_id,))
                addresses = cur.fetchall()
            except sqlite3.Error as e:
                flash(f'Error fetching addresses: {e}', 'error')
            finally:
                con.close()
        
        return render_template("customer_home.html", addresses=addresses)
    else:
        flash("Please log in to access this page", "error")
        return redirect(url_for('login'))

@app.route('/check-shipment-status', methods=['POST'])
def check_shipment_status():
    session_id = request.cookies.get('session_id')
    user_id = None
    if session_id:
        user_id = validate_session(session_id)
    shipment_code = request.form['shipment_code']
    con = get_db()
    if con:
        try:
            cur = con.cursor()
            cur.execute('''
                SELECT sender_name, sender_address, recipient_name, recipient_address, status, shipment_code
                FROM shipments
                WHERE shipment_code = ?
            ''', (shipment_code,))
            shipment_details = cur.fetchone()
            if shipment_details:
                flash('Shipment details retrieved successfully', 'success')
                if user_id:
                    return render_template('customer_home.html', shipment_details=shipment_details)
                else:
                    return render_template('index.html', shipment_details=shipment_details)
            else:
                flash('Invalid shipment code or shipment not found', 'error')
        except sqlite3.Error as e:
            flash(f'Error checking shipment status: {e}', 'error')
        finally:
            con.close()
    else:
        flash('Failed to connect to the database', 'error')
    if user_id:
        return redirect(url_for('customer_home'))
    else:
        return redirect(url_for('home'))

@app.route('/courier-home')
def courier_home():
    if 'user_id' in session:
        user_id = session['user_id']

        con = get_db()
        addresses = []
        available_shipments = []
        accepted_shipments = []

        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    SELECT label, address, city, postal_code, id
                    FROM addresses
                    WHERE user_id = ?
                ''', (user_id,))
                addresses = cur.fetchall()

                if addresses:
                    cur.execute('''
                        SELECT id, sender_name, sender_address, recipient_name, recipient_address, status, shipment_code
                        FROM shipments
                        WHERE status = 'Pending'
                    ''')
                    available_shipments = cur.fetchall()

                    cur.execute('''
                        SELECT id, sender_name, sender_address, recipient_name, recipient_address, status, shipment_code
                        FROM shipments
                        WHERE status = 'In Transit' AND courier_id = ?
                    ''', (user_id,))
                    accepted_shipments = cur.fetchall()
                else:
                    flash("You have no saved addresses. Please add an address in your profile to accept shipments.", "error")

            except sqlite3.Error as e:
                flash(f'Error fetching data: {e}', 'error')
            finally:
                con.close()

        return render_template("courier_home.html", addresses=addresses, available_shipments=available_shipments, accepted_shipments=accepted_shipments)
    else:
        flash("Please log in to access this page", "error")
        return redirect(url_for('login'))


@app.route('/accept-shipment/<int:shipment_id>', methods=['POST'])
def accept_shipment(shipment_id):
    if 'user_id' in session:
        user_id = session['user_id']

        con = get_db()
        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    UPDATE shipments
                    SET status = 'In Transit', courier_id = ?
                    WHERE id = ? AND status = 'Pending'
                ''', (user_id, shipment_id))
                if cur.rowcount == 0:
                    flash('Failed to accept shipment. It may already be accepted by another courier.', 'error')
                else:
                    con.commit()
                    flash('Shipment accepted successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Error accepting shipment: {e}', 'error')
            finally:
                con.close()
    else:
        flash('You need to log in to accept a shipment', 'error')

    return redirect(url_for('courier_home'))


@app.route('/mark-delivered/<int:shipment_id>', methods=['POST'])
def mark_delivered(shipment_id):
    if 'user_id' in session:
        user_id = session['user_id']

        con = get_db()
        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    UPDATE shipments
                    SET status = 'Delivered'
                    WHERE id = ? AND courier_id = ? AND status = 'In Transit'
                ''', (shipment_id, user_id))
                if cur.rowcount == 0:
                    flash('Failed to mark shipment as delivered. It may already be marked as delivered or not accepted by you.', 'error')
                else:
                    con.commit()
                    flash('Shipment marked as delivered successfully!', 'success')
            except sqlite3.Error as e:
                flash(f'Error marking shipment as delivered: {e}', 'error')
            finally:
                con.close()
    else:
        flash('You need to log in to mark a shipment as delivered', 'error')

    return redirect(url_for('courier_home'))

@app.route('/create-shipment', methods=['POST'])
def create_shipment():
    if 'user_id' in session:
        user_id = session['user_id']
        sender_name = request.form['sender_name']
        sender_address = request.form['sender_address']
        recipient_name = request.form['recipient_name']
        recipient_address = request.form['recipient_address']
        status = "Pending"
        
        shipment_code = str(uuid.uuid4().int)[:13]

        con = get_db()
        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    INSERT INTO shipments (user_id, sender_name, sender_address, recipient_name, recipient_address, status, shipment_code)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, sender_name, sender_address, recipient_name, recipient_address, status, shipment_code))
                con.commit()
                flash(f'Shipment created successfully! Your shipment code is {shipment_code}', 'success')
            except sqlite3.Error as e:
                flash(f'Shipment creation error: {e}', 'error')
            finally:
                con.close()
        else:
            flash('Failed to connect to the database', 'error')
    else:
        flash('You need to log in to create a shipment', 'error')
    return redirect(url_for('customer_home'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        user_type = request.form['user-type']
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        con = get_db()
        if con:
            try:
                cur = con.cursor()
                cur.execute("INSERT INTO users (username, email, password, user_type) VALUES (?, ?, ?, ?)", 
                            (username, email, hashed_password, user_type))
                con.commit()
                flash("You have been registered successfully", "success")
            except sqlite3.Error as e:
                flash(f"Error in registration: {e}", "error")
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
        user_id = session['user_id']
        
        con = get_db()
        addresses = []
        if con:
            try:
                cur = con.cursor()
                cur.execute('''
                    SELECT label, address, city, postal_code, id
                    FROM addresses
                    WHERE user_id = ?
                ''', (user_id,))
                addresses = cur.fetchall()
            except sqlite3.Error as e:
                flash(f'Error fetching addresses: {e}', 'error')
            finally:
                con.close()
        
        session['addresses'] = addresses
        
        return render_template('profile.html', addresses=addresses)
    else:
        flash("Please log in to view your profile", "error")
        return redirect(url_for('login'))

@app.route('/add-address', methods=['GET', 'POST'])
def add_address():
    if 'user_id' in session:
        if request.method == 'POST':
            user_id = session['user_id']
            label = request.form['label']
            address = request.form['address']
            city = request.form['city']
            postal_code = request.form['postal_code']
            
            con = get_db()
            if con:
                try:
                    cur = con.cursor()
                    cur.execute('''
                        INSERT INTO addresses (user_id, label, address, city, postal_code)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (user_id, label, address, city, postal_code))
                    con.commit()
                    flash('Address added successfully', 'success')
                except sqlite3.Error as e:
                    flash(f'Error adding address: {e}', 'error')
                finally:
                    con.close()
            return redirect(url_for('profile'))
        
        return render_template('add-address.html')
    else:
        flash('You need to login first', 'error')
        return redirect(url_for('login'))

@app.route('/delete-address/<int:address_id>', methods=['POST'])
def delete_address(address_id):
    if request.method == 'POST':
        con = get_db()
        con.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
        con.commit()
        con.close()
        flash('Address was successfully deleted!', 'success')
    else:
        flash('Invalid request method', 'error')

    return redirect(url_for('profile'))

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
    session.pop('user_type', None)
    response = make_response(redirect(url_for('home')))
    response.set_cookie('session_id', '', expires=0)
    flash("You have been logged out", "success")
    return response

if __name__ == '__main__':
    app.run(debug=True)
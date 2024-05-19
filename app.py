from flask import Flask, render_template, redirect, url_for, request, flash
import sqlite3
con=sqlite3.connect('database.db')


app = Flask(__name__, template_folder="templates", static_folder="static")


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(request.form)
        return request.form
    else:
        return render_template("login.html")

@app.route('/register' , methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if request.form['email'] == '' or request.form['password'] == '' or request.form['username'] == '':
            return redirect(url_for('register'))
        if request.form['password'] != request.form['confirm_password']:
            return redirect(url_for('register'))
        cur=con.cursor()
        cur.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (request.form['username'], request.form['email'], request.form['password']))
        con.commit()
        username=cur.execute('SELECT username FROM users WHERE email = ?', (request.form['email'],)).fetchone()
        cur.close()
        return request.form
    else:
        return render_template("register.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == '__main__':
    con.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, email TEXT, password TEXT)')
    con.execute('CREATE TABLE IF NOT EXISTS sessions (session_id TEXT, user_id TEXT, created_at TEXT, updated_at TEXT)')
    con.commit()
    app.run(debug=True)
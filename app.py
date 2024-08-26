from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_file = 'users.db'

def init_db():
    if not os.path.exists(db_file):
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
# init_db(): Initializes the SQLite database by creating a users table if it doesn't already exist.
init_db()
# Calls the init_db() function to set up the database when the application starts.

@app.route('/')
def home():
    return render_template('index.html')
# home(): Renders the index.html template when the user visits the root URL (/).

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        try:
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')
# register(): Handles both GET and POST requests for the /register route.
# GET: Renders the register.html template.
# POST: Receives form data, checks if the username exists in the SQLite database, inserts a new user into the database if not, and redirects to the login page with a success message.

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['username'], request.form['password']
        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Login failed.', 'error')
    return render_template('login.html')
# login(): Handles both GET and POST requests for the /login route.
# GET: Renders the login.html template.
# POST: Receives form data, checks the credentials against the SQLite database, sets the session if successful, and redirects to the dashboard with a success message.

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', username=session.get('username')) if 'username' in session else redirect(url_for('login'))
# dashboard(): Displays the dashboard page.
# If the user is logged in (i.e., username is in the session), it renders dashboard.html and passes the username to the template.
# If not logged in, it redirects to the login page.

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
# logout(): Logs the user out by removing the username from the session and redirects to the login page.

if __name__ == '__main__':
    app.run(debug=True)
# Application Run: Starts the Flask development server in debug mode when the script is executed directly.

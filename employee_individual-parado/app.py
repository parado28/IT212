from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
import config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def get_db():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME
    )

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        flash('Account created!', 'success')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_input = request.form['password']
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password_input):
            session['user_id'] = user[0]
            return redirect('/dashboard')
        flash('Invalid login!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    return render_template('dashboard.html', employees=employees)

@app.route('/add_employee', methods=['POST'])
def add_employee():
    if 'user_id' not in session:
        return redirect('/login')
    name = request.form['name']
    position = request.form['position']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO employees (name, position) VALUES (%s, %s)", (name, position))
    conn.commit()
    return redirect('/dashboard')

@app.route('/edit_employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        cursor.execute("UPDATE employees SET name=%s, position=%s WHERE id=%s", (name, position, id))
        conn.commit()
        return redirect('/dashboard')
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete_employee/<int:id>')
def delete_employee(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    conn.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)

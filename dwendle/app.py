from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_mysqldb import MySQL
import hashlib
from fpdf import FPDF
import io
from functools import wraps

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change for production!

# MySQL Config - update to your credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'employee_dwendle'

mysql = MySQL(app)

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login required decorator
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash("Please login first", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect(url_for('login'))

# Admin Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template('signup.html')

        hashed_pw = hash_password(password)

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO admin (username, password) VALUES (%s, %s)", (username, hashed_pw))
            mysql.connection.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Username already exists.", "danger")
        finally:
            cur.close()

    return render_template('signup.html')

# Admin Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_logged_in' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = hash_password(password)

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, hashed_pw))
        admin = cur.fetchone()
        cur.close()

        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash("Welcome, " + username, "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials", "danger")

    return render_template('login.html')

# Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

# Dashboard - employee list + search
@app.route('/dashboard')
@login_required
def dashboard():
    search_query = request.args.get('search', '')

    cur = mysql.connection.cursor()
    if search_query:
        like_query = f"%{search_query}%"
        cur.execute("SELECT * FROM employees WHERE name LIKE %s OR email LIKE %s", (like_query, like_query))
    else:
        cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', employees=employees, search=search_query)

# Add Employee
@app.route('/employee/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        salary = request.form['salary']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO employees (name, email, phone, position, salary) VALUES (%s,%s,%s,%s,%s)",
                    (name, email, phone, position, salary))
        mysql.connection.commit()
        cur.close()

        flash("Employee added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('employee_form.html', action="Add", employee=None)

# Edit Employee
@app.route('/employee/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        position = request.form['position']
        salary = request.form['salary']

        cur.execute("UPDATE employees SET name=%s, email=%s, phone=%s, position=%s, salary=%s WHERE id=%s",
                    (name, email, phone, position, salary, id))
        mysql.connection.commit()
        cur.close()

        flash("Employee updated successfully!", "success")
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cur.fetchone()
    cur.close()

    if not employee:
        flash("Employee not found", "danger")
        return redirect(url_for('dashboard'))

    return render_template('employee_form.html', action="Edit", employee=employee)

# Delete Employee
@app.route('/employee/delete/<int:id>', methods=['POST'])
@login_required
def delete_employee(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    flash("Employee deleted successfully!", "success")
    return redirect(url_for('dashboard'))

# Export PDF
@app.route('/export/pdf')
@login_required
def export_pdf():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employees")
    employees = cur.fetchall()
    cur.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Header
    pdf.cell(0, 10, "Employee List", ln=True, align='C')
    pdf.ln(10)

    # Table header
    pdf.set_font("Arial", 'B', 10)
    headers = ['ID', 'Name', 'Email', 'Phone', 'Position', 'Salary']
    widths = [10, 40, 50, 30, 35, 25]

    for i in range(len(headers)):
        pdf.cell(widths[i], 10, headers[i], border=1, align='C')
    pdf.ln()

    # Table rows
    pdf.set_font("Arial", size=10)
    for e in employees:
        pdf.cell(widths[0], 10, str(e[0]), border=1)
        pdf.cell(widths[1], 10, e[1], border=1)
        pdf.cell(widths[2], 10, e[2], border=1)
        pdf.cell(widths[3], 10, e[3], border=1)
        pdf.cell(widths[4], 10, e[4], border=1)
        pdf.cell(widths[5], 10, f"{e[5]:.2f}", border=1, align='R')
        pdf.ln()

    # Get PDF as string and send as download
    pdf_str = pdf.output(dest='S').encode('latin1')

    return send_file(
        io.BytesIO(pdf_str),
        download_name="employees.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )

if __name__ == "__main__":
    app.run(debug=True)

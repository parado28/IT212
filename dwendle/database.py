from flask_mysqldb import MySQL
from app import app
from config import Config

mysql = MySQL(app)

def init_db():
    with app.app_context():
        cur = mysql.connection.cursor()
        
        # Create admin table if not exists
        cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            password VARCHAR(100) NOT NULL
        )
        """)
        
        # Create employees table if not exists
        cur.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            phone VARCHAR(20),
            department VARCHAR(100),
            position VARCHAR(100),
            salary DECIMAL(10, 2),
            hire_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Insert default admin if not exists
        cur.execute("SELECT * FROM admins WHERE username = 'admin'")
        admin = cur.fetchone()
        if not admin:
            cur.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", 
                       ('admin', 'admin123'))  # In production, use hashed passwords
        
        mysql.connection.commit()
        cur.close()

def get_db():
    return mysql.connection
from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)
# Database file path
app.config['DATABASE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'employees.db')

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database with table and sample data
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            department TEXT,
            salary REAL
        );
    ''')
    # Prepopulate sample employees if table is empty
    cursor.execute('SELECT COUNT(*) as count FROM employees')
    if cursor.fetchone()['count'] == 0:
        sample = [
            ('Alice', 30, 'HR', 50000),
            ('Bob', 25, 'Engineering', 60000),
            ('Charlie', 28, 'Sales', 55000)
        ]
        cursor.executemany(
            'INSERT INTO employees (name, age, department, salary) VALUES (?, ?, ?, ?)',
            sample
        )
        conn.commit()
    conn.close()

@app.before_first_request
def setup():
    init_db()

@app.route('/', methods=['GET', 'POST'])
def update_employee():
    conn = get_db_connection()
    cursor = conn.cursor()
    message = ''
    if request.method == 'POST':
        emp_id = request.form.get('emp_id')
        # Collect only non-empty fields for update
        fields = {}
        for field in ('name', 'age', 'department', 'salary'):
            value = request.form.get(field)
            if value:
                fields[field] = value
        if emp_id and fields:
            # Build dynamic SQL
            set_clause = ', '.join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [emp_id]
            query = f"UPDATE employees SET {set_clause} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            message = 'Employee updated successfully.'
        else:
            message = 'Please select an employee and provide at least one field to update.'
    # Fetch current list for display
    cursor.execute('SELECT * FROM employees')
    employees = cursor.fetchall()
    conn.close()
    return render_template('update.html', employees=employees, message=message)

if __name__ == '__main__':
    app.run(debug=True)

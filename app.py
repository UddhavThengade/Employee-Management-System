from datetime import date
from functools import wraps
import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def db():
    return mysql.connector.connect(
        host=app.config["DB_HOST"], user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"], database=app.config["DB_NAME"]
    )

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def initialize():
    conn = db()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS employees (
        id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL, phone VARCHAR(25),
        department_id INT, job_title VARCHAR(100), salary DECIMAL(10,2) DEFAULT 0,
        joining_date DATE, status VARCHAR(20) DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS attendance (
        id INT AUTO_INCREMENT PRIMARY KEY, employee_id INT NOT NULL,
        attendance_date DATE NOT NULL, status ENUM('Present','Absent','Leave') NOT NULL,
        UNIQUE KEY unique_employee_day(employee_id, attendance_date),
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE)""")
    cur.execute("SELECT id FROM admins WHERE username=%s", ("admin",))
    if cur.fetchone() is None:
        cur.execute("INSERT INTO admins(username,password_hash) VALUES(%s,%s)",
                    ("admin", generate_password_hash("Admin@123")))
    for name in ("IT", "HR", "Finance", "Sales", "Operations"):
        cur.execute("INSERT IGNORE INTO departments(name) VALUES(%s)", (name,))
    conn.commit()
    cur.close()
    conn.close()

def departments_list():
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM departments ORDER BY name")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

@app.route("/")
def home():
    return redirect(url_for("dashboard") if session.get("admin_id") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM admins WHERE username=%s", (request.form.get("username","").strip(),))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user["password_hash"], request.form.get("password","")):
            session.clear()
            session["admin_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) total FROM employees")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) total FROM departments")
    dept_count = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) total FROM employees WHERE status='Active'")
    active = cur.fetchone()["total"]
    cur.execute("""SELECT e.id,e.name,e.email,e.status,COALESCE(d.name,'Unassigned') department
                   FROM employees e LEFT JOIN departments d ON e.department_id=d.id
                   ORDER BY e.id DESC LIMIT 5""")
    recent = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard.html", total=total, dept_count=dept_count, active=active, recent=recent)

@app.route("/employees")
@login_required
def employees():
    q = request.args.get("q","").strip()
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT e.*,d.name department FROM employees e
                   LEFT JOIN departments d ON e.department_id=d.id
                   WHERE e.name LIKE %s OR e.email LIKE %s OR CAST(e.id AS CHAR) LIKE %s
                   ORDER BY e.id DESC""", (f"%{q}%",f"%{q}%",f"%{q}%"))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("employees.html", employees=rows, q=q)

@app.route("/employees/add", methods=["GET","POST"])
@login_required
def add_employee():
    if request.method == "POST":
        data = (request.form.get("name","").strip(), request.form.get("email","").strip(),
                request.form.get("phone") or None, request.form.get("department_id") or None,
                request.form.get("job_title") or None, request.form.get("salary") or 0,
                request.form.get("joining_date") or None, request.form.get("status") or "Active")
        if not data[0] or not data[1]:
            flash("Name and email are required.", "danger")
        else:
            conn = db()
            cur = conn.cursor()
            try:
                cur.execute("""INSERT INTO employees
                    (name,email,phone,department_id,job_title,salary,joining_date,status)
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""", data)
                conn.commit()
                flash("Employee added.", "success")
                return redirect(url_for("employees"))
            except mysql.connector.IntegrityError:
                flash("Email already exists.", "danger")
            finally:
                cur.close()
                conn.close()
    return render_template("employee_form.html", employee=None, departments=departments_list())

@app.route("/employees/edit/<int:eid>", methods=["GET","POST"])
@login_required
def edit_employee(eid):
    conn = db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM employees WHERE id=%s", (eid,))
    employee = cur.fetchone()
    cur.close()
    conn.close()
    if not employee:
        flash("Employee not found.", "danger")
        return redirect(url_for("employees"))
    if request.method == "POST":
        data = (request.form.get("name","").strip(), request.form.get("email","").strip(),
                request.form.get("phone") or None, request.form.get("department_id") or None,
                request.form.get("job_title") or None, request.form.get("salary") or 0,
                request.form.get("joining_date") or None, request.form.get("status") or "Active", eid)
        conn = db()
        cur = conn.cursor()
        try:
            cur.execute("""UPDATE employees SET name=%s,email=%s,phone=%s,department_id=%s,
                job_title=%s,salary=%s,joining_date=%s,status=%s WHERE id=%s""", data)
            conn.commit()
            flash("Employee updated.", "success")
            return redirect(url_for("employees"))
        except mysql.connector.IntegrityError:
            flash("Email is already used by another employee.", "danger")
        finally:
            cur.close()
            conn.close()
    return render_template("employee_form.html", employee=employee, departments=departments_list())

@app.post("/employees/delete/<int:eid>")
@login_required
def delete_employee(eid):
    conn = db()
    cur = conn.cursor()
    cur.execute("DELETE FROM employees WHERE id=%s", (eid,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Employee deleted.", "success")
    return redirect(url_for("employees"))

@app.route("/departments", methods=["GET","POST"])
@login_required
def departments():
    conn = db()
    cur = conn.cursor()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        if name:
            try:
                cur.execute("INSERT INTO departments(name) VALUES(%s)", (name,))
                conn.commit()
                flash("Department added.", "success")
            except mysql.connector.IntegrityError:
                flash("Department already exists.", "danger")
        cur.close()
        conn.close()
        return redirect(url_for("departments"))
    cur.close()
    cur = conn.cursor(dictionary=True)
    cur.execute("""SELECT d.id,d.name,COUNT(e.id) employee_count FROM departments d
                   LEFT JOIN employees e ON e.department_id=d.id GROUP BY d.id,d.name ORDER BY d.name""")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("departments.html", departments=rows)

@app.route("/attendance", methods=["GET","POST"])
@login_required
def attendance():
    day = request.values.get("attendance_date", date.today().isoformat())
    conn = db()
    cur = conn.cursor(dictionary=True)
    if request.method == "POST":
        status = request.form.get("status")
        if status not in ("Present","Absent","Leave"):
            flash("Invalid attendance status.", "danger")
        else:
            cur2 = conn.cursor()
            cur2.execute("""INSERT INTO attendance(employee_id,attendance_date,status)
                VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE status=VALUES(status)""",
                (request.form.get("employee_id"), day, status))
            conn.commit()
            cur2.close()
            flash("Attendance saved.", "success")
        cur.close()
        conn.close()
        return redirect(url_for("attendance", attendance_date=day))
    cur.execute("SELECT id,name FROM employees WHERE status='Active' ORDER BY name")
    people = cur.fetchall()
    cur.execute("""SELECT e.name,a.status FROM attendance a JOIN employees e ON e.id=a.employee_id
                   WHERE a.attendance_date=%s ORDER BY e.name""", (day,))
    records = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("attendance.html", people=people, records=records, day=day)

if __name__ == "__main__":
    initialize()
    app.run(debug=True)

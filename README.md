<<<<<<< HEAD
# Employee Management System (EMS)

A beginner-friendly full-stack project using Python, Flask, MySQL, HTML, CSS and Bootstrap.

## Features
- Admin login/logout with hashed password and Flask session
- Dashboard statistics and recently added employees
- Employee CRUD (create, read, update, delete)
- Search employees by name, email or ID
- Add departments and view department employee counts
- Mark attendance by date; update a day's status for an employee
- Responsive Bootstrap interface

## Setup (Windows)
1. Install MySQL Server or start MySQL from XAMPP.
2. Open MySQL Workbench/phpMyAdmin and run `database/ems_database.sql`.
3. Open this folder in VS Code.
4. Create and activate a virtual environment:
   ```bash
   py -m venv venv
   venv\Scripts\activate
   ```
5. Install packages:
   ```bash
   pip install -r requirements.txt
   ```
6. Copy `.env.example` to `.env`. Add your MySQL password and change `SECRET_KEY`.
7. Run:
   ```bash
   python app.py
   ```
8. Visit `http://127.0.0.1:5000`.

## First login
Username: `admin`
Password: `Admin@123`

The application creates the initial admin account on first run. Change the demo password before using this outside local practice. Do not deploy with Flask debug mode enabled.

## Database tables
`admins`, `departments`, `employees`, `attendance`.

## Resume description
**Employee Management System | Python, Flask, MySQL, HTML, CSS, Bootstrap**
- Developed a responsive web application to manage employee profiles, departments and attendance records.
- Implemented admin authentication, password hashing and session-based route protection.
- Built employee CRUD operations, search functionality, dashboard statistics and relational MySQL tables.
- Used parameterized SQL queries and database constraints to maintain data consistency.

## Future enhancements
Add payroll slips, PDF/Excel reports, role-based access, pagination, CSRF protection and automated tests before production deployment.
=======
# Employee-Management-System
A web-based Employee Management System (EMS) developed using Python Flask, HTML, CSS, JavaScript, and SQLite/MySQL. This application helps organizations efficiently manage employee records, add, update, delete, and view employee details through a user-friendly interface. It simplifies employee data management and improves administrative efficiency.
>>>>>>> e149b92ebeefb1839f9d734fd12f9efd94b467bc

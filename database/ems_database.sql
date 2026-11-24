CREATE DATABASE IF NOT EXISTS ems_db;
USE ems_db;
CREATE TABLE IF NOT EXISTS admins (
 id INT AUTO_INCREMENT PRIMARY KEY,
 username VARCHAR(80) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL
);
CREATE TABLE IF NOT EXISTS departments (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS employees (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 email VARCHAR(150) NOT NULL UNIQUE,
 phone VARCHAR(25),
 department_id INT,
 job_title VARCHAR(100),
 salary DECIMAL(10,2) DEFAULT 0,
 joining_date DATE,
 status VARCHAR(20) DEFAULT 'Active',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS attendance (
 id INT AUTO_INCREMENT PRIMARY KEY,
 employee_id INT NOT NULL,
 attendance_date DATE NOT NULL,
 status ENUM('Present','Absent','Leave') NOT NULL,
 UNIQUE KEY unique_employee_day (employee_id, attendance_date),
 FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
INSERT IGNORE INTO departments(name) VALUES ('IT'),('HR'),('Finance'),('Sales'),('Operations');

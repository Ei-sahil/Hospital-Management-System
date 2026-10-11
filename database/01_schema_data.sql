CREATE DATABASE hospital_management;

CREATE TABLE Department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100)
);
CREATE TABLE Patient (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(20),
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    address VARCHAR(255),
    blood_group VARCHAR(5),
    emergency_contact VARCHAR(15),
    registration_date DATE NOT NULL
);

CREATE TABLE Doctor (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    phone VARCHAR(15) UNIQUE,
    email VARCHAR(100) UNIQUE,
    license_number VARCHAR(50) NOT NULL UNIQUE,
    department_id INT NOT NULL,

    FOREIGN KEY (department_id)
        REFERENCES Department(department_id)
);
CREATE TABLE Appointment (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'Scheduled',

    FOREIGN KEY (patient_id)
        REFERENCES Patient(patient_id),

    FOREIGN KEY (doctor_id)
        REFERENCES Doctor(doctor_id)
);
CREATE TABLE Medical_Record (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL UNIQUE,
    diagnosis VARCHAR(255),
    symptoms TEXT,
    treatment TEXT,
    notes TEXT,
    record_date DATE NOT NULL,

    FOREIGN KEY (appointment_id)
        REFERENCES Appointment(appointment_id)
);
CREATE TABLE Medicine (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100),
    unit_price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0
);
CREATE TABLE Prescription (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    prescription_date DATE NOT NULL,
    instructions TEXT,

    FOREIGN KEY (record_id)
        REFERENCES Medical_Record(record_id)
);
CREATE TABLE Prescription_Item (
    prescription_item_id INT AUTO_INCREMENT PRIMARY KEY,
    prescription_id INT NOT NULL,
    medicine_id INT NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    duration VARCHAR(100),
    quantity INT NOT NULL,

    FOREIGN KEY (prescription_id)
        REFERENCES Prescription(prescription_id),

    FOREIGN KEY (medicine_id)
        REFERENCES Medicine(medicine_id)
);
CREATE TABLE Lab_Test (
    test_id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    test_name VARCHAR(100) NOT NULL,
    test_date DATE NOT NULL,
    result TEXT,
    reference_range VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    cost DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (appointment_id)
        REFERENCES Appointment(appointment_id)
);
CREATE TABLE Bill (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_id INT,
    bill_date DATE NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    payment_method VARCHAR(30),

    FOREIGN KEY (patient_id)
        REFERENCES Patient(patient_id),

    FOREIGN KEY (appointment_id)
        REFERENCES Appointment(appointment_id)
);
CREATE TABLE Bill_Item (
    bill_item_id INT AUTO_INCREMENT PRIMARY KEY,
    bill_id INT NOT NULL,
    description VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (bill_id)
        REFERENCES Bill(bill_id)
);
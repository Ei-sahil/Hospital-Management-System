USE hospital_management;

insert into Department(department_name, location)
values
('Cardiology', 'Block A'),
('Neurology', 'Block B'),
('Orthopedics', 'Block C'),
('Pediatrics', 'Block D'),
('General Medicine', 'Block E');
INSERT INTO Patient
(first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact, registration_date)
VALUES
('Rahul', 'Sharma', '2000-05-12', 'Male', '9876543210', 'rahul.sharma@email.com', 'Delhi', 'B+', '9811111111', '2026-09-01'),
('Priya', 'Singh', '1998-08-21', 'Female', '9876543211', 'priya.singh@email.com', 'Gurugram', 'O+', '9811111112', '2026-09-03'),
('Aman', 'Verma', '1985-02-14', 'Male', '9876543212', 'aman.verma@email.com', 'Noida', 'A+', '9811111113', '2026-09-05'),
('Sneha', 'Gupta', '2010-11-30', 'Female', '9876543213', 'sneha.gupta@email.com', 'Delhi', 'AB+', '9811111114', '2026-09-07'),
('Arjun', 'Mehta', '1978-06-18', 'Male', '9876543214', 'arjun.mehta@email.com', 'Faridabad', 'O-', '9811111115', '2026-09-10');
INSERT INTO Doctor
(first_name, last_name, specialization, phone, email, license_number, department_id)
VALUES
('Amit', 'Kumar', 'Cardiologist', '9810000001', 'amit.kumar@hospital.com', 'LIC001', 1),
('Neha', 'Sharma', 'Neurologist', '9810000002', 'neha.sharma@hospital.com', 'LIC002', 2),
('Rohit', 'Verma', 'Orthopedic Surgeon', '9810000003', 'rohit.verma@hospital.com', 'LIC003', 3),
('Kavita', 'Mehta', 'Pediatrician', '9810000004', 'kavita.mehta@hospital.com', 'LIC004', 4),
('Sanjay', 'Gupta', 'General Physician', '9810000005', 'sanjay.gupta@hospital.com', 'LIC005', 5);
INSERT INTO Medicine
(medicine_name, manufacturer, unit_price, stock_quantity)
VALUES
('Paracetamol 500mg', 'Cipla', 20.00, 500),
('Azithromycin 250mg', 'Sun Pharma', 45.00, 200),
('Cetirizine 10mg', 'Dr. Reddy''s', 15.00, 300),
('Pantoprazole 40mg', 'Lupin', 30.00, 250),
('Amoxicillin 500mg', 'Abbott', 60.00, 150),
('Aspirin 75mg', 'Bayer', 25.00, 400);
INSERT INTO Appointment
(patient_id, doctor_id, appointment_date, appointment_time, reason, status)
VALUES
(1, 1, '2026-09-15', '10:00:00', 'Chest discomfort', 'Completed'),
(2, 2, '2026-09-16', '11:30:00', 'Recurring headache', 'Completed'),
(3, 3, '2026-09-17', '09:30:00', 'Knee pain', 'Completed'),
(4, 4, '2026-09-18', '14:00:00', 'Fever and weakness', 'Completed'),
(5, 5, '2026-09-19', '16:00:00', 'General health checkup', 'Completed'),
(1, 5, '2026-10-05', '10:30:00', 'Follow-up consultation', 'Scheduled'),
(2, 2, '2026-10-06', '12:00:00', 'Headache follow-up', 'Scheduled');
INSERT INTO Medical_Record
(appointment_id, diagnosis, symptoms, treatment, notes, record_date)
VALUES
(1, 'Mild Hypertension', 'Chest discomfort, mild dizziness',
 'Lifestyle modification and medication',
 'Blood pressure monitoring advised',
 '2026-09-15'),

(2, 'Migraine', 'Recurring headache, sensitivity to light',
 'Medication and rest',
 'Follow-up recommended if symptoms persist',
 '2026-09-16'),

(3, 'Knee Arthritis', 'Knee pain and stiffness',
 'Physiotherapy and medication',
 'Avoid excessive physical strain',
 '2026-09-17'),

(4, 'Viral Fever', 'Fever, weakness, body ache',
 'Medication and hydration',
 'Rest recommended',
 '2026-09-18'),

(5, 'Routine Checkup', 'No major symptoms',
 'General health monitoring',
 'Annual health check recommended',
 '2026-09-19');
INSERT INTO Prescription
(record_id, prescription_date, instructions)
VALUES
(1, '2026-09-15', 'Take medicines after meals'),
(2, '2026-09-16', 'Take medicines as prescribed'),
(3, '2026-09-17', 'Take medication with food'),
(4, '2026-09-18', 'Maintain hydration and take medicines on schedule');
INSERT INTO Prescription_Item
(prescription_id, medicine_id, dosage, frequency, duration, quantity)
VALUES
(1, 6, '75 mg', 'Once daily', '30 days', 30),
(1, 4, '40 mg', 'Once daily', '30 days', 30),

(2, 1, '500 mg', 'Twice daily', '5 days', 10),
(2, 3, '10 mg', 'Once daily', '5 days', 5),

(3, 1, '500 mg', 'Twice daily', '7 days', 14),

(4, 1, '500 mg', 'Three times daily', '5 days', 15),
(4, 3, '10 mg', 'Once daily', '5 days', 5);
INSERT INTO Lab_Test
(appointment_id, test_name, test_date, result, reference_range, status, cost)
VALUES
(1, 'Blood Pressure Test', '2026-09-15', '145/92 mmHg', 'Below 120/80 mmHg', 'Completed', 100.00),
(2, 'MRI Brain', '2026-09-16', 'No significant abnormality', 'Normal', 'Completed', 2500.00),
(3, 'Knee X-Ray', '2026-09-17', 'Mild joint space narrowing', 'Normal', 'Completed', 800.00),
(4, 'Complete Blood Count', '2026-09-18', 'Within normal limits', 'Standard range', 'Completed', 500.00);
INSERT INTO Bill
(patient_id, appointment_id, bill_date, payment_status, payment_method)
VALUES
(1, 1, '2026-09-15', 'Paid', 'UPI'),
(2, 2, '2026-09-16', 'Paid', 'Card'),
(3, 3, '2026-09-17', 'Pending', NULL),
(4, 4, '2026-09-18', 'Paid', 'Cash'),
(5, 5, '2026-09-19', 'Paid', 'UPI');
INSERT INTO Bill_Item
(bill_id, description, quantity, unit_price, amount)
VALUES
(1, 'Consultation', 1, 500.00, 500.00),
(1, 'Blood Pressure Test', 1, 100.00, 100.00),

(2, 'Consultation', 1, 500.00, 500.00),
(2, 'MRI Brain', 1, 2500.00, 2500.00),

(3, 'Consultation', 1, 500.00, 500.00),
(3, 'Knee X-Ray', 1, 800.00, 800.00),

(4, 'Consultation', 1, 500.00, 500.00),
(4, 'Complete Blood Count', 1, 500.00, 500.00),

(5, 'Consultation', 1, 500.00, 500.00);
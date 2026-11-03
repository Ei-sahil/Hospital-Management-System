USE hospital_management;

-- Synthetic analytics data for the Hospital Management System.
-- Safe to re-run: patients, appointments, lab tests and bills are checked
-- against their natural identifiers before insertion.
-- Run this after database/02_sample_data.sql.
-- All names, contact details and records below are fictional.

START TRANSACTION;

-- 1. Add patients across several registration months.
INSERT INTO Patient
(first_name, last_name, date_of_birth, gender, phone, email, address, blood_group, emergency_contact, registration_date)
SELECT x.first_name, x.last_name, x.date_of_birth, x.gender, x.phone, x.email,
       x.address, x.blood_group, x.emergency_contact, x.registration_date
FROM (
    SELECT 'Riya' first_name, 'Kapoor' last_name, '1995-03-12' date_of_birth, 'Female' gender, '9000000101' phone, 'demo.riya@example.com' email, 'Delhi' address, 'A+' blood_group, '9000001101' emergency_contact, '2026-07-08' registration_date
    UNION ALL SELECT 'Karan','Malhotra','1989-11-04','Male','9000000102','demo.karan@example.com','Noida','B+','9000001102','2026-07-19'
    UNION ALL SELECT 'Meera','Nair','2001-01-23','Female','9000000103','demo.meera@example.com','Gurugram','O+','9000001103','2026-08-03'
    UNION ALL SELECT 'Dev','Arora','1972-06-17','Male','9000000104','demo.dev@example.com','Delhi','AB+','9000001104','2026-08-15'
    UNION ALL SELECT 'Ananya','Rao','1993-09-28','Female','9000000105','demo.ananya@example.com','Faridabad','O-','9000001105','2026-08-27'
    UNION ALL SELECT 'Ishaan','Bhatia','1982-02-10','Male','9000000106','demo.ishaan@example.com','Delhi','B-','9000001106','2026-09-06'
    UNION ALL SELECT 'Pooja','Saxena','1968-12-02','Female','9000000107','demo.pooja@example.com','Noida','A-','9000001107','2026-09-22'
    UNION ALL SELECT 'Aditya','Menon','2003-04-14','Male','9000000108','demo.aditya@example.com','Gurugram','O+','9000001108','2026-10-02'
    UNION ALL SELECT 'Nisha','Khanna','1990-07-30','Female','9000000109','demo.nisha@example.com','Delhi','AB-','9000001109','2026-10-11'
    UNION ALL SELECT 'Vikram','Joshi','1979-05-08','Male','9000000110','demo.vikram@example.com','Ghaziabad','B+','9000001110','2026-10-19'
    UNION ALL SELECT 'Tanya','Sethi','1997-10-16','Female','9000000111','demo.tanya@example.com','Delhi','A+','9000001111','2026-11-01'
    UNION ALL SELECT 'Kabir','Das','1986-08-25','Male','9000000112','demo.kabir@example.com','Noida','O-','9000001112','2026-11-02'
) AS x
WHERE NOT EXISTS (SELECT 1 FROM Patient p WHERE p.email = x.email);

-- 2. Add appointments spread across months, doctors and statuses.
-- Existing doctor license numbers LIC001-LIC005 are created by 02_sample_data.sql.
INSERT INTO Appointment
(patient_id, doctor_id, appointment_date, appointment_time, reason, status)
SELECT p.patient_id, d.doctor_id, x.appointment_date, x.appointment_time, x.reason, x.status
FROM (
    SELECT 'demo.riya@example.com' email, 'LIC001' license_number, '2026-07-12' appointment_date, '09:00:00' appointment_time, 'Cardiology consultation' reason, 'Completed' status
    UNION ALL SELECT 'demo.karan@example.com','LIC002','2026-07-21','10:00:00','Neurology consultation','Completed'
    UNION ALL SELECT 'demo.meera@example.com','LIC003','2026-08-05','11:00:00','Knee pain assessment','Completed'
    UNION ALL SELECT 'demo.dev@example.com','LIC004','2026-08-18','12:00:00','Child wellness consultation','Completed'
    UNION ALL SELECT 'demo.ananya@example.com','LIC005','2026-08-29','14:00:00','General health check','Completed'
    UNION ALL SELECT 'demo.ishaan@example.com','LIC001','2026-09-08','09:30:00','Heart health follow-up','Completed'
    UNION ALL SELECT 'demo.pooja@example.com','LIC002','2026-09-24','10:30:00','Headache assessment','Completed'
    UNION ALL SELECT 'demo.aditya@example.com','LIC003','2026-10-04','11:30:00','Sports injury review','Completed'
    UNION ALL SELECT 'demo.nisha@example.com','LIC004','2026-10-13','13:00:00','Paediatric consultation','Completed'
    UNION ALL SELECT 'demo.vikram@example.com','LIC005','2026-10-21','15:00:00','Routine consultation','Completed'
    UNION ALL SELECT 'demo.riya@example.com','LIC001','2026-10-27','09:00:00','Cardiology follow-up','Completed'
    UNION ALL SELECT 'demo.karan@example.com','LIC002','2026-10-29','10:00:00','Neurology follow-up','Completed'
    UNION ALL SELECT 'demo.tanya@example.com','LIC003','2026-11-01','11:00:00','Orthopaedic consultation','Completed'
    UNION ALL SELECT 'demo.kabir@example.com','LIC005','2026-11-02','12:00:00','General consultation','Completed'
    UNION ALL SELECT 'demo.meera@example.com','LIC001','2026-11-03','14:00:00','Cardiology review','Scheduled'
    UNION ALL SELECT 'demo.dev@example.com','LIC002','2026-11-03','15:00:00','Neurology review','Scheduled'
    UNION ALL SELECT 'demo.ananya@example.com','LIC003','2026-10-30','16:00:00','Orthopaedic follow-up','Cancelled'
    UNION ALL SELECT 'demo.ishaan@example.com','LIC005','2026-10-25','09:00:00','General follow-up','Cancelled'
    UNION ALL SELECT 'demo.nisha@example.com','LIC001','2026-10-31','10:00:00','Cardiology review','Scheduled'
) AS x
INNER JOIN Patient p ON p.email = x.email
INNER JOIN Doctor d ON d.license_number = x.license_number
WHERE NOT EXISTS (
    SELECT 1 FROM Appointment a
    WHERE a.patient_id = p.patient_id
      AND a.doctor_id = d.doctor_id
      AND a.appointment_date = x.appointment_date
      AND a.appointment_time = x.appointment_time
);

-- 3. Add lab tests for completed appointments.
INSERT INTO Lab_Test
(appointment_id, test_name, test_date, result, reference_range, status, cost)
SELECT a.appointment_id, x.test_name, x.test_date, x.result, x.reference_range, x.status, x.cost
FROM (
    SELECT 'demo.riya@example.com' email, '2026-07-12' appointment_date, 'ECG' test_name, '2026-07-12' test_date, 'Normal sinus rhythm' result, 'Normal' reference_range, 'Completed' status, 700.00 cost
    UNION ALL SELECT 'demo.karan@example.com','2026-07-21','MRI Brain','2026-07-21','No acute finding','Normal','Completed',2600.00
    UNION ALL SELECT 'demo.meera@example.com','2026-08-05','Knee X-Ray','2026-08-05','No acute fracture','Normal','Completed',900.00
    UNION ALL SELECT 'demo.dev@example.com','2026-08-18','Complete Blood Count','2026-08-18','Within expected limits','Standard range','Completed',550.00
    UNION ALL SELECT 'demo.ananya@example.com','2026-08-29','Lipid Profile','2026-08-29','Sample report value','Refer to lab range','Completed',850.00
    UNION ALL SELECT 'demo.ishaan@example.com','2026-09-08','ECG','2026-09-08','Normal sinus rhythm','Normal','Completed',700.00
    UNION ALL SELECT 'demo.pooja@example.com','2026-09-24','Thyroid Profile','2026-09-24','Sample report value','Refer to lab range','Completed',1200.00
    UNION ALL SELECT 'demo.aditya@example.com','2026-10-04','Vitamin D','2026-10-04','Sample report value','Refer to lab range','Completed',1000.00
    UNION ALL SELECT 'demo.nisha@example.com','2026-10-13','Complete Blood Count','2026-10-13','Within expected limits','Standard range','Completed',550.00
    UNION ALL SELECT 'demo.vikram@example.com','2026-10-21','Blood Glucose','2026-10-21','Sample report value','Refer to lab range','Completed',300.00
    UNION ALL SELECT 'demo.tanya@example.com','2026-11-01','Knee X-Ray','2026-11-01','No acute fracture','Normal','Completed',900.00
    UNION ALL SELECT 'demo.kabir@example.com','2026-11-02','Liver Function Test','2026-11-02',NULL,'Refer to lab range','Pending',1100.00
) AS x
INNER JOIN Patient p ON p.email = x.email
INNER JOIN Appointment a ON a.patient_id = p.patient_id AND a.appointment_date = x.appointment_date
WHERE NOT EXISTS (
    SELECT 1 FROM Lab_Test lt
    WHERE lt.appointment_id = a.appointment_id AND lt.test_name = x.test_name
);

-- 4. Add bills for completed appointments, mixing Paid and Pending states.
INSERT INTO Bill
(patient_id, appointment_id, bill_date, payment_status, payment_method)
SELECT p.patient_id, a.appointment_id, x.bill_date, x.payment_status, x.payment_method
FROM (
    SELECT 'demo.riya@example.com' email, '2026-07-12' appointment_date, '2026-07-12' bill_date, 'Paid' payment_status, 'UPI' payment_method
    UNION ALL SELECT 'demo.karan@example.com','2026-07-21','2026-07-21','Paid','Card'
    UNION ALL SELECT 'demo.meera@example.com','2026-08-05','2026-08-05','Paid','Cash'
    UNION ALL SELECT 'demo.dev@example.com','2026-08-18','2026-08-18','Pending',NULL
    UNION ALL SELECT 'demo.ananya@example.com','2026-08-29','2026-08-29','Paid','UPI'
    UNION ALL SELECT 'demo.ishaan@example.com','2026-09-08','2026-09-08','Paid','Card'
    UNION ALL SELECT 'demo.pooja@example.com','2026-09-24','2026-09-24','Pending',NULL
    UNION ALL SELECT 'demo.aditya@example.com','2026-10-04','2026-10-04','Paid','UPI'
    UNION ALL SELECT 'demo.nisha@example.com','2026-10-13','2026-10-13','Paid','Cash'
    UNION ALL SELECT 'demo.vikram@example.com','2026-10-21','2026-10-21','Pending',NULL
    UNION ALL SELECT 'demo.tanya@example.com','2026-11-01','2026-11-01','Paid','UPI'
    UNION ALL SELECT 'demo.kabir@example.com','2026-11-02','2026-11-02','Pending',NULL
) AS x
INNER JOIN Patient p ON p.email = x.email
INNER JOIN Appointment a ON a.patient_id = p.patient_id AND a.appointment_date = x.appointment_date
WHERE NOT EXISTS (SELECT 1 FROM Bill b WHERE b.appointment_id = a.appointment_id);

-- 5. Add bill line items. Amount is quantity multiplied by unit price.
INSERT INTO Bill_Item (bill_id, description, quantity, unit_price, amount)
SELECT b.bill_id, x.description, 1, x.unit_price, x.unit_price
FROM (
    SELECT 'demo.riya@example.com' email, '2026-07-12' bill_date, 'Consultation' description, 500.00 unit_price
    UNION ALL SELECT 'demo.riya@example.com','2026-07-12','ECG',700.00
    UNION ALL SELECT 'demo.karan@example.com','2026-07-21','Consultation',500.00
    UNION ALL SELECT 'demo.karan@example.com','2026-07-21','MRI Brain',2600.00
    UNION ALL SELECT 'demo.meera@example.com','2026-08-05','Consultation',500.00
    UNION ALL SELECT 'demo.meera@example.com','2026-08-05','Knee X-Ray',900.00
    UNION ALL SELECT 'demo.dev@example.com','2026-08-18','Consultation',500.00
    UNION ALL SELECT 'demo.dev@example.com','2026-08-18','Complete Blood Count',550.00
    UNION ALL SELECT 'demo.ananya@example.com','2026-08-29','Consultation',500.00
    UNION ALL SELECT 'demo.ananya@example.com','2026-08-29','Lipid Profile',850.00
    UNION ALL SELECT 'demo.ishaan@example.com','2026-09-08','Consultation',500.00
    UNION ALL SELECT 'demo.ishaan@example.com','2026-09-08','ECG',700.00
    UNION ALL SELECT 'demo.pooja@example.com','2026-09-24','Consultation',500.00
    UNION ALL SELECT 'demo.pooja@example.com','2026-09-24','Thyroid Profile',1200.00
    UNION ALL SELECT 'demo.aditya@example.com','2026-10-04','Consultation',500.00
    UNION ALL SELECT 'demo.aditya@example.com','2026-10-04','Vitamin D',1000.00
    UNION ALL SELECT 'demo.nisha@example.com','2026-10-13','Consultation',500.00
    UNION ALL SELECT 'demo.nisha@example.com','2026-10-13','Complete Blood Count',550.00
    UNION ALL SELECT 'demo.vikram@example.com','2026-10-21','Consultation',500.00
    UNION ALL SELECT 'demo.vikram@example.com','2026-10-21','Blood Glucose',300.00
    UNION ALL SELECT 'demo.tanya@example.com','2026-11-01','Consultation',500.00
    UNION ALL SELECT 'demo.tanya@example.com','2026-11-01','Knee X-Ray',900.00
    UNION ALL SELECT 'demo.kabir@example.com','2026-11-02','Consultation',500.00
    UNION ALL SELECT 'demo.kabir@example.com','2026-11-02','Liver Function Test',1100.00
) AS x
INNER JOIN Patient p ON p.email = x.email
INNER JOIN Bill b ON b.patient_id = p.patient_id AND b.bill_date = x.bill_date
WHERE NOT EXISTS (
    SELECT 1 FROM Bill_Item bi
    WHERE bi.bill_id = b.bill_id AND bi.description = x.description
);

COMMIT;

-- Quick validation: these counts should increase after successful execution.
SELECT 'Patients' AS entity, COUNT(*) AS total FROM Patient
UNION ALL SELECT 'Appointments', COUNT(*) FROM Appointment
UNION ALL SELECT 'Lab tests', COUNT(*) FROM Lab_Test
UNION ALL SELECT 'Bills', COUNT(*) FROM Bill
UNION ALL SELECT 'Bill items', COUNT(*) FROM Bill_Item;

USE hospital_management;

select * 
FROM patient;
select * 
FROM Doctor;
select * 
FROM Medicine;

select *
FROM Patient
WHERE address = 'Delhi';

SELECT
    doctor_id,
    first_name,
    last_name,
    specialization
FROM Doctor;

SELECT
    medicine_name,
    manufacturer,
    unit_price
FROM Medicine
ORDER BY unit_price DESC;

SELECT
p.patient_id,
CONCAT(p.first_name, ' ' ,p.last_name) as patient_name,
a.appointment_date,
a.appointment_time,
a.reason,
a.status
from Patient p
inner join Appointment a
 on p.patient_id=a.patient_id;
 
 SELECT
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    a.reason,
    a.status
FROM Appointment a
INNER JOIN Patient p
    ON a.patient_id = p.patient_id
INNER JOIN Doctor d
    ON a.doctor_id = d.doctor_id;
    
    SELECT
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    dept.department_name,
    dept.location
FROM Doctor d
INNER JOIN Department dept
    ON d.department_id = dept.department_id;
    
-- left join demo, 
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.appointment_id,
    a.appointment_date,
    a.reason
FROM Patient p
LEFT JOIN Appointment a
    ON p.patient_id = a.patient_id;
-- self join,, this gives the list of doctors which are in same department 
SELECT
    CONCAT(d1.first_name, ' ', d1.last_name) AS doctor_1,
    CONCAT(d2.first_name, ' ', d2.last_name) AS doctor_2,
    d1.department_id
FROM Doctor d1
INNER JOIN Doctor d2
    ON d1.department_id = d2.department_id
   AND d1.doctor_id < d2.doctor_id;

-- Full outer join using left and right join and union
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.appointment_id
FROM Patient p
LEFT JOIN Appointment a
    ON p.patient_id = a.patient_id

UNION

SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    a.appointment_id
FROM Patient p
RIGHT JOIN Appointment a
    ON p.patient_id = a.patient_id;
-- total patient 
SELECT COUNT(*) AS total_patients
FROM Patient;
-- finding total appointments per patient
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    COUNT(a.appointment_id) AS total_appointments
FROM Patient p
LEFT JOIN Appointment a
    ON p.patient_id = a.patient_id
GROUP BY
    p.patient_id,
    p.first_name,
    p.last_name;
-- Calculate total billing amount
SELECT
    SUM(amount) AS total_billing_amount
FROM Bill_Item;

-- Calculate total amount for each bill
SELECT
    bill_id,
    SUM(amount) AS bill_total
FROM Bill_Item
GROUP BY bill_id
ORDER BY bill_id;

--  Find the cheapest medicine
SELECT
    MIN(unit_price) AS cheapest_medicine
FROM Medicine;

-- Count doctors in each department
SELECT
    dept.department_name,
    COUNT(d.doctor_id) AS total_doctors
FROM Department dept
LEFT JOIN Doctor d
    ON dept.department_id = d.department_id
GROUP BY dept.department_id, dept.department_name;

--  Find patients with more than one appointment
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    COUNT(a.appointment_id) AS total_appointments
FROM Patient p
LEFT JOIN Appointment a
    ON p.patient_id = a.patient_id
GROUP BY
    p.patient_id,
    p.first_name,
    p.last_name
HAVING COUNT(a.appointment_id) > 1;

-- Medicines priced above the average medicine price
SELECT
    medicine_name,
    unit_price
FROM Medicine
WHERE unit_price > (
    SELECT AVG(unit_price)
    FROM Medicine
);

--  Find patients who have at least one appointment
SELECT
    patient_id,
    first_name,
    last_name
FROM Patient
WHERE patient_id IN (
    SELECT patient_id
    FROM Appointment
);

-- correlated subquery= Patients with at least one completed appointment
SELECT
    p.patient_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name
FROM Patient p
WHERE EXISTS (
    SELECT 1
    FROM Appointment a
    WHERE a.patient_id = p.patient_id
      AND a.status = 'Completed'
);
--  A view for appointment details
CREATE VIEW appointment_details AS
SELECT
    a.appointment_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
    CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
    d.specialization,
    a.appointment_date,
    a.appointment_time,
    a.reason,
    a.status
FROM Appointment a
INNER JOIN Patient p
    ON a.patient_id = p.patient_id
INNER JOIN Doctor d
    ON a.doctor_id = d.doctor_id;

-- Transaction demo
START TRANSACTION;

UPDATE Bill
SET payment_status = 'Paid',
    payment_method = 'UPI'
WHERE bill_id = 3;

COMMIT;
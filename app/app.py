import streamlit as st
import mysql.connector
from datetime import date
from db import get_connection

st.set_page_config(
    page_title="Hospital Management System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Hospital Management System")
st.caption("Central dashboard for hospital operations")

st.sidebar.title("🏥 Hospital HMS")
st.sidebar.caption("Hospital Management System")

st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Patients",
        "Doctors",
        "Appointments",
        "Medical Records",
        "Lab Tests",
        "Prescriptions",
        "Billing"
    ]
)

st.sidebar.divider()
st.sidebar.caption("DBMS Project • MySQL + Streamlit")

if menu == "Dashboard":

    st.title("🏥 Hospital Management Dashboard")
    st.caption("Overview of the hospital management system")

    # ============================================================
    # 1. GET DASHBOARD STATISTICS
    # ============================================================

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Active patients
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Patient
        WHERE status = 'Active';
    """)

    active_patients = cursor.fetchone()["total"]

    # Active doctors
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Doctor
        WHERE status = 'Active';
    """)

    active_doctors = cursor.fetchone()["total"]

    # Scheduled appointments
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM Appointment
        WHERE status = 'Scheduled';
    """)

    scheduled_appointments = cursor.fetchone()["total"]

    # Pending bills
    cursor.execute("""
        SELECT COALESCE(SUM(bi.amount), 0) AS total
        FROM Bill b
        LEFT JOIN Bill_Item bi
            ON b.bill_id = bi.bill_id
        WHERE b.payment_status = 'Pending';
    """)

    pending_bills = cursor.fetchone()["total"]

    # Today's appointments
    cursor.execute("""
        SELECT
            a.appointment_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            CONCAT(
                'Dr. ',
                d.first_name,
                ' ',
                d.last_name
            ) AS doctor_name,
            d.specialization,
            a.appointment_time,
            a.reason,
            a.status
        FROM Appointment a
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        WHERE a.appointment_date = CURDATE()
        ORDER BY a.appointment_time;
    """)

    todays_appointments = cursor.fetchall()

    # Pending lab tests
    cursor.execute("""
        SELECT
            lt.test_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            lt.test_name,
            lt.test_date,
            lt.cost
        FROM Lab_Test lt
        INNER JOIN Appointment a
            ON lt.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        WHERE lt.status = 'Pending'
        ORDER BY lt.test_date DESC;
    """)

    pending_lab_tests = cursor.fetchall()

    cursor.close()
    connection.close()


    # ============================================================
    # 2. KPI CARDS
    # ============================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👤 Active Patients",
            active_patients
        )

    with col2:
        st.metric(
            "👨‍⚕️ Active Doctors",
            active_doctors
        )

    with col3:
        st.metric(
            "📅 Scheduled Appointments",
            scheduled_appointments
        )

    with col4:
        st.metric(
            "💰 Pending Bills",
            f"₹{pending_bills:,.2f}"
        )


    st.divider()


    # ============================================================
    # 3. TODAY'S APPOINTMENTS
    # ============================================================

    st.subheader("📅 Today's Appointments")

    if todays_appointments:

        st.dataframe(
            todays_appointments,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No appointments scheduled for today."
        )


    # ============================================================
    # 4. PENDING LAB TESTS
    # ============================================================

    st.subheader("🧪 Pending Lab Tests")

    if pending_lab_tests:

        st.dataframe(
            pending_lab_tests,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.success(
            "No pending lab tests. ✅"
        )

elif menu=="Patients":
   st.header("👨‍⚕️ Patient Management")

    
    # Add New Patient
    

   st.subheader("➕ Add New Patient")

   with st.form("add_patient_form"):

        col1, col2 = st.columns(2)

        with col1:
            first_name = st.text_input("First Name")
            date_of_birth = st.date_input("Date of Birth")
            phone = st.text_input("Phone")
            address = st.text_input("Address")

        with col2:
            last_name = st.text_input("Last Name")
            gender = st.selectbox(
                "Gender",
                ["Male", "Female", "Other"]
            )
            email = st.text_input("Email")
            blood_group = st.selectbox(
                "Blood Group",
                ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
            )

        registration_date = st.date_input(
            "Registration Date"
        )

        submitted = st.form_submit_button(
            "Add Patient"
        )

    
    # Insert Patient into Database
    

   if submitted:

        if first_name == "" or last_name == "":
            st.error("First Name and Last Name are required.")

        else:

            connection = None
            cursor = None

            try:
                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Patient
                    (
                        first_name,
                        last_name,
                        date_of_birth,
                        gender,
                        phone,
                        email,
                        address,
                        blood_group,
                        registration_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    phone if phone else None,
                    email if email else None,
                    address if address else None,
                    blood_group,
                    registration_date
                )

                cursor.execute(query, values)

                connection.commit()

                st.success("Patient added successfully! 🎉")

                st.rerun()

            except mysql.connector.Error as err:

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()
    # Update Patient 

   st.subheader("✏️ Update Patient")
   connection=get_connection();
   cursor=connection.cursor(dictionary=True)

   cursor.execute("""
    SELECT
        patient_id,
        first_name,
        last_name,
        date_of_birth,
        gender,
        phone,
        email,
        address,
        blood_group,
        registration_date
    FROM Patient
    ORDER BY patient_id;
  """)

   patient_list = cursor.fetchall()

   cursor.close()
   connection.close()

   if patient_list:
       patient_options={
           f"{p['patient_id']}-{p['first_name']} {p['last_name']}":
           p
           for p in patient_list
       }
       selected_patient_name=st.selectbox(
           "select Patient",
           list(patient_options.keys())
       )
       selected_patient=patient_options[selected_patient_name]

       with st.form("update_patient_form"):
           col1,col2=st.columns(2)

           with col1:
               first_name=st.text_input(
                   "First Name",
                   value=selected_patient["first_name"]
               )
               date_of_birth = st.date_input(
                "Date of Birth",
                value=selected_patient["date_of_birth"]
               )

               phone = st.text_input(
                "Phone",
                value=selected_patient["phone"] or ""
               )

               address = st.text_input(
                "Address",
                value=selected_patient["address"] or ""
               )
           with col2:
              last_name = st.text_input(
                "Last Name",
                value=selected_patient["last_name"]
              )

              gender_options = [
                "Male",
                "Female",
                "Other"
              ]

              current_gender = selected_patient["gender"]

              gender_index = (
                gender_options.index(current_gender)
                if current_gender in gender_options
                else 0
              )

              gender = st.selectbox(
                "Gender",
                gender_options,
                index=gender_index
              )

              email = st.text_input(
                "Email",
                value=selected_patient["email"] or ""
              )

              blood_group_options = [
                "A+",
                "A-",
                "B+",
                "B-",
                "AB+",
                "AB-",
                "O+",
                "O-"
              ]

              current_blood_group = selected_patient["blood_group"]

              blood_group_index = (
                blood_group_options.index(current_blood_group)
                if current_blood_group in blood_group_options
                else 0
              )

              blood_group = st.selectbox(
                "Blood Group",
                blood_group_options,
                index=blood_group_index
              )

           submitted = st.form_submit_button(
            "Update Patient"
           ) 
       if submitted:

           if first_name == "" or last_name == "":
              st.error(
                "First Name and Last Name are required."
            )

           else:

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    UPDATE Patient
                    SET
                        first_name = %s,
                        last_name = %s,
                        date_of_birth = %s,
                        gender = %s,
                        phone = %s,
                        email = %s,
                        address = %s,
                        blood_group = %s
                    WHERE patient_id = %s
                """

                values = (
                    first_name,
                    last_name,
                    date_of_birth,
                    gender,
                    phone if phone else None,
                    email if email else None,
                    address if address else None,
                    blood_group,
                    selected_patient["patient_id"]
                )

                cursor.execute(query, values)

                connection.commit()

                st.success(
                    "Patient updated successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()
   else:
     st.info("No patients available to update.")              
    
    #Delete patients

   st.subheader("🚫 Deactivate Patient")

   connection=get_connection()
   cursor=connection.cursor(dictionary=True)

   cursor.execute("""
    SELECT
        patient_id,
        first_name,
        last_name,
        status
    FROM Patient
    WHERE status='Active'
    ORDER BY patient_id;
    """)

   patient_list=cursor.fetchall()

   cursor.close()
   connection.close()

   if patient_list:
      patient_options = {
        f"{p['patient_id']} - {p['first_name']} {p['last_name']}": p
        for p in patient_list
        }
      selected_patient_name = st.selectbox(
        "Select Patient to Deactivate",
        list(patient_options.keys()),
        key="deactivate_patient"
      )
      selected_patient = patient_options[selected_patient_name]
      if st.button("Deactive Patient"):
          
              connection=None
              cursor=None

              try:
                  connection=get_connection()
                  cursor=connection.cursor()

                  query="""
                        UPDATE patient
                        set status='Inactive'
                        where patient_id=%s
                    """
                  value=(
                      selected_patient["patient_id"],
                    )

                  cursor.execute(query,value)
                  connection.commit()

                  st.success(
                      "Patient deactivated successfully! ✅"
                  )
              except mysql.connector.Error as err:
                  connection.rollback()

                  st.error(
                      f"Database Error:{err}"
                  )
              finally:
                  if cursor:
                      cursor.close()
                  if connection:
                      connection.close()
   else:
       st.info("No Ptients available to deactive.")                   
                  



    
    # Display Existing Patients
    

   st.subheader("📋 Registered Patients")

   connection = get_connection()
   cursor = connection.cursor(dictionary=True)

   cursor.execute("""
        SELECT
            patient_id,
            first_name,
            last_name,
            date_of_birth,
            gender,
            phone,
            email,
            address,
            blood_group,
            registration_date,
            status
        FROM Patient
        ORDER BY patient_id;
    """)

   patients = cursor.fetchall()

   cursor.close()
   connection.close()

   st.dataframe(
        patients,
        use_container_width=True
    )
elif menu == "Doctors":

    st.header("👨‍⚕️ Doctor Management")

    
    # Add New Doctor
    

    st.subheader("➕ Add New Doctor")

    # Get departments from database
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM Department
        ORDER BY department_name;
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    if not departments:

        st.warning("No departments available.")

    else:

        department_options = {
            d["department_name"]: d["department_id"]
            for d in departments
        }

        with st.form("add_doctor_form"):

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name"
                )

                specialization = st.text_input(
                    "Specialization"
                )

                phone = st.text_input(
                    "Phone"
                )

                license_number = st.text_input(
                    "License Number"
                )

            with col2:

                last_name = st.text_input(
                    "Last Name"
                )

                email = st.text_input(
                    "Email"
                )

                department_name = st.selectbox(
                    "Department",
                    list(department_options.keys())
                )

            submitted = st.form_submit_button(
                "Add Doctor"
            )

        
        # Insert Doctor
        

        if submitted:

            if (
                first_name == ""
                or last_name == ""
                or specialization == ""
                or license_number == ""
            ):

                st.error(
                    "First Name, Last Name, "
                    "Specialization and License Number "
                    "are required."
                )

            else:

                connection = None
                cursor = None

                try:

                    connection = get_connection()
                    cursor = connection.cursor()

                    query = """
                        INSERT INTO Doctor
                        (
                            first_name,
                            last_name,
                            specialization,
                            phone,
                            email,
                            license_number,
                            department_id
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """

                    values = (
                        first_name,
                        last_name,
                        specialization,
                        phone if phone else None,
                        email if email else None,
                        license_number,
                        department_options[department_name]
                    )

                    cursor.execute(
                        query,
                        values
                    )

                    connection.commit()

                    st.success(
                        "Doctor added successfully! ✅"
                    )

                except mysql.connector.Error as err:

                    connection.rollback()

                    st.error(
                        f"Database error: {err}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if connection:
                        connection.close()

    
    # Display Doctors
    

    st.subheader("📋 Registered Doctors")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.doctor_id,
            d.first_name,
            d.last_name,
            d.specialization,
            d.phone,
            d.email,
            d.license_number,
            dep.department_name,
            status
        FROM Doctor d
        INNER JOIN Department dep
            ON d.department_id = dep.department_id
        ORDER BY d.doctor_id;
    """)

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()

    st.dataframe(
        doctors,
        use_container_width=True
    )


   # Update Doctor


    st.subheader("✏️ Update Doctor")

    # Get doctors
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            doctor_id,
            first_name,
            last_name,
            specialization,
            phone,
            email,
            license_number,
            department_id,
            status
        FROM Doctor
        WHERE status='Active'
        ORDER BY doctor_id;
    """)

    doctor_list = cursor.fetchall()

    cursor.close()
    connection.close()


    # Get departments
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            department_id,
            department_name
        FROM Department
        ORDER BY department_name;
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()


    if doctor_list and departments:

        # --------------------------------
        # Doctor dropdown
        # --------------------------------

        doctor_options = {
            f"{d['doctor_id']} - {d['first_name']} {d['last_name']}": d
            for d in doctor_list
        }

        selected_doctor_name = st.selectbox(
            "Select Doctor",
            list(doctor_options.keys()),
            key="update_doctor"
        )

        selected_doctor = doctor_options[selected_doctor_name]


        
        # Department dictionary
        

        department_options = {
            d["department_name"]: d["department_id"]
            for d in departments
        }


        # Find current department name
        current_department_name = next(
            (
                d["department_name"]
                for d in departments
                if d["department_id"] == selected_doctor["department_id"]
            ),
            None
        )


        
        # Update Form
        

        with st.form("update_doctor_form"):

            col1, col2 = st.columns(2)

            with col1:

                first_name = st.text_input(
                    "First Name",
                    value=selected_doctor["first_name"]
                )

                specialization = st.text_input(
                    "Specialization",
                    value=selected_doctor["specialization"]
                )

                phone = st.text_input(
                    "Phone",
                    value=selected_doctor["phone"] or ""
                )

                license_number = st.text_input(
                    "License Number",
                    value=selected_doctor["license_number"]
                )

            with col2:

                last_name = st.text_input(
                    "Last Name",
                    value=selected_doctor["last_name"]
                )

                email = st.text_input(
                    "Email",
                    value=selected_doctor["email"] or ""
                )

                department_names = list(
                    department_options.keys()
                )

                department_index = (
                    department_names.index(current_department_name)
                    if current_department_name in department_names
                    else 0
                )

                department_name = st.selectbox(
                    "Department",
                    department_names,
                    index=department_index
                )

            col_update, col_deactivate = st.columns(2)

            with col_update:
                submitted = st.form_submit_button(
                    "✏️ Update Doctor"
                )

            with col_deactivate:
                deactivate = st.form_submit_button(
                    "🚫 Deactivate Doctor"
                )


        
        # Update Database
        

        if submitted:

            if (
                first_name == ""
                or last_name == ""
                or specialization == ""
                or license_number == ""
            ):

                st.error(
                    "First Name, Last Name, "
                    "Specialization and License Number "
                    "are required."
                )

            else:

                connection = None
                cursor = None

                try:

                    connection = get_connection()
                    cursor = connection.cursor()

                    query = """
                        UPDATE Doctor
                        SET
                            first_name = %s,
                            last_name = %s,
                            specialization = %s,
                            phone = %s,
                            email = %s,
                            license_number = %s,
                            department_id = %s
                        WHERE doctor_id = %s
                    """

                    values = (
                        first_name,
                        last_name,
                        specialization,
                        phone if phone else None,
                        email if email else None,
                        license_number,
                        department_options[department_name],
                        selected_doctor["doctor_id"]
                    )

                    cursor.execute(
                        query,
                        values
                    )

                    connection.commit()

                    st.success(
                        "Doctor updated successfully! ✅"
                    )
                    st.rerun()

                except mysql.connector.Error as err:

                    connection.rollback()

                    st.error(
                        f"Database error: {err}"
                    )

                finally:

                    if cursor:
                        cursor.close()

                    if connection:
                        connection.close()
        if deactivate:

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    UPDATE Doctor
                    SET status = 'Inactive'
                    WHERE doctor_id = %s
                """

                values = (
                    selected_doctor["doctor_id"],
                )

                cursor.execute(query, values)

                connection.commit()

                st.success(
                    "Doctor deactivated successfully! ✅"
                )
                st.rerun()

            except mysql.connector.Error as err:

                connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()
    else:

        st.info(
            "Doctors or departments are not available."
        )



    
elif menu == "Appointments":
    st.header("📅 Appointment Management")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch active patients
    cursor.execute("""
        SELECT
            patient_id,
            first_name,
            last_name
        FROM Patient
        WHERE status = 'Active'
        ORDER BY first_name, last_name;
    """)

    patients = cursor.fetchall()

    # Fetch active doctors
    cursor.execute("""
        SELECT
            doctor_id,
            first_name,
            last_name,
            specialization
        FROM Doctor
        WHERE status = 'Active'
        ORDER BY first_name, last_name;
    """)

    doctors = cursor.fetchall()

    cursor.close()
    connection.close()
    patient_options = {
        f'{p["patient_id"]} - {p["first_name"]} {p["last_name"]}':
        p["patient_id"]
        for p in patients
    }

    doctor_options = {
        f'{d["doctor_id"]} - Dr. {d["first_name"]} {d["last_name"]} ({d["specialization"]})':
        d["doctor_id"]
        for d in doctors
    }
    st.subheader("📅 Book New Appointment")

    with st.form("book_appointment_form"):

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        selected_doctor = st.selectbox(
            "Select Doctor",
            list(doctor_options.keys())
        )

        appointment_date = st.date_input(
            "Appointment Date"
        )

        appointment_time = st.time_input(
            "Appointment Time"
        )

        reason = st.text_area(
            "Reason for Visit"
        )

        submitted = st.form_submit_button(
            "📅 Book Appointment"
        )
    if submitted:

        if appointment_date < date.today():
         st.error("Appointment date cannot be in the past.")
         st.stop()
        if not reason.strip():
         st.error("Please enter the reason for the appointment.")
         st.stop()

        patient_id = patient_options[selected_patient]
        doctor_id = doctor_options[selected_doctor]

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO Appointment
                (
                    patient_id,
                    doctor_id,
                    appointment_date,
                    appointment_time,
                    reason,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """

            values = (
                patient_id,
                doctor_id,
                appointment_date,
                appointment_time,
                reason,
                "Scheduled"
            )

            cursor.execute(query, values)
            connection.commit()

            st.success("Appointment booked successfully! ✅")

            st.rerun()

        except mysql.connector.Error as err:

            if connection:
                connection.rollback()

            st.error(f"Database error: {err}")

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()
    st.subheader("📋 All Appointments")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.appointment_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            d.specialization,
            a.appointment_date,
            a.appointment_time,
            a.reason,
            a.status
        FROM Appointment a
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        ORDER BY a.appointment_date DESC,
                 a.appointment_time DESC;
    """)

    appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    st.dataframe(
        appointments,
        use_container_width=True
    )
    st.subheader("🔄 Update Appointment Status")

    if appointments:

        appointment_options = {
            f'{a["appointment_id"]} - '
            f'{a["patient_name"]} with {a["doctor_name"]} '
            f'({a["appointment_date"]})':
            a
            for a in appointments
        }

        selected_appointment_name = st.selectbox(
            "Select Appointment",
            list(appointment_options.keys())
        )

        selected_appointment = appointment_options[
            selected_appointment_name
        ]

        status_options = [
            "Scheduled",
            "Completed",
            "Cancelled"
        ]

        current_status = selected_appointment["status"]

        status_index = (
            status_options.index(current_status)
            if current_status in status_options
            else 0
        )

        new_status = st.selectbox(
            "Appointment Status",
            status_options,
            index=status_index
        )

        if st.button("🔄 Update Status"):

            connection = None
            cursor = None

            try:
                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    UPDATE Appointment
                    SET status = %s
                    WHERE appointment_id = %s
                """

                values = (
                    new_status,
                    selected_appointment["appointment_id"]
                )

                cursor.execute(query, values)
                connection.commit()

                st.success("Appointment status updated successfully! ✅")

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(f"Database error: {err}")

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

elif menu == "Medical Records":

    st.header("🩺 Medical Record Management")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            mr.record_id,
            mr.appointment_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            mr.diagnosis,
            mr.symptoms,
            mr.treatment,
            mr.notes,
            mr.record_date
        FROM Medical_Record mr
        INNER JOIN Appointment a
            ON mr.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        ORDER BY mr.record_date DESC;
    """)

    medical_records = cursor.fetchall()

    cursor.close()
    connection.close()

    st.subheader("📋 Medical Records")

    st.dataframe(
        medical_records,
        use_container_width=True
    )

    st.subheader("➕ Create Medical Record")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.appointment_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            a.appointment_date
        FROM Appointment a
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        LEFT JOIN Medical_Record mr
            ON a.appointment_id = mr.appointment_id
        WHERE a.status = 'Completed'
          AND mr.record_id IS NULL
        ORDER BY a.appointment_date DESC;
    """)

    eligible_appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    if eligible_appointments:

        appointment_options = {
            f'{a["appointment_id"]} - '
            f'{a["patient_name"]} with {a["doctor_name"]} '
            f'({a["appointment_date"]})':
            a["appointment_id"]
            for a in eligible_appointments
        }

        selected_appointment = st.selectbox(
            "Select Completed Appointment",
            list(appointment_options.keys())
        )
        with st.form("medical_record_form"):

            diagnosis = st.text_input(
                "Diagnosis"
            )

            symptoms = st.text_area(
                "Symptoms"
            )

            treatment = st.text_area(
                "Treatment"
            )

            notes = st.text_area(
                "Additional Notes"
            )

            record_date = st.date_input(
                "Record Date"
            )

            submitted = st.form_submit_button(
                "💾 Save Medical Record"
            )
        if submitted:

            appointment_id = appointment_options[selected_appointment]

            connection = None
            cursor = None

            try:
                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Medical_Record
                    (
                        appointment_id,
                        diagnosis,
                        symptoms,
                        treatment,
                        notes,
                        record_date
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                values = (
                    appointment_id,
                    diagnosis,
                    symptoms,
                    treatment,
                    notes,
                    record_date
                )

                cursor.execute(query, values)
                connection.commit()

                st.success("Medical record created successfully! ✅")

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(f"Database error: {err}")

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()
    else:
        st.info("No completed appointments are available for creating a medical record.")

elif menu == "Lab Tests":
    st.header("🧪 Lab Test Management")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            lt.test_id,
            lt.appointment_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            lt.test_name,
            lt.test_date,
            lt.result,
            lt.reference_range,
            lt.status,
            lt.cost
        FROM Lab_Test lt
        INNER JOIN Appointment a
            ON lt.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        ORDER BY lt.test_date DESC;
    """)

    lab_tests = cursor.fetchall()

    cursor.close()
    connection.close()

    st.subheader("📋 Laboratory Tests")

    st.dataframe(
        lab_tests,
        use_container_width=True
    )


    st.subheader("➕ Add Lab Test")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.appointment_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            a.appointment_date
        FROM Appointment a
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        WHERE a.status = 'Completed'
        ORDER BY a.appointment_date DESC;
    """)

    eligible_appointments = cursor.fetchall()

    cursor.close()
    connection.close()

    if eligible_appointments:

        appointment_options = {
            f'{a["appointment_id"]} - '
            f'{a["patient_name"]} with {a["doctor_name"]} '
            f'({a["appointment_date"]})':
            a["appointment_id"]
            for a in eligible_appointments
        }

        selected_appointment = st.selectbox(
            "Select Appointment",
            list(appointment_options.keys())
        )
        with st.form("lab_test_form"):

            test_name = st.text_input(
                "Test Name"
            )

            test_date = st.date_input(
                "Test Date"
            )

            reference_range = st.text_input(
                "Reference Range"
            )

            cost = st.number_input(
                "Cost",
                min_value=0.0,
                step=50.0
            )

            status = st.selectbox(
                "Status",
                ["Pending", "Completed"]
            )

            result = st.text_area(
                "Result"
            )

            submitted = st.form_submit_button(
                "🧪 Add Lab Test"
            )
        if submitted:

            if not test_name.strip():
                st.error("Please enter the test name.")
                st.stop()

            appointment_id = appointment_options[selected_appointment]

            connection = None
            cursor = None

            try:
                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Lab_Test
                    (
                        appointment_id,
                        test_name,
                        test_date,
                        result,
                        reference_range,
                        status,
                        cost
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

                values = (
                    appointment_id,
                    test_name,
                    test_date,
                    result,
                    reference_range,
                    status,
                    cost
                )

                cursor.execute(query, values)
                connection.commit()

                st.success("Lab test added successfully! ✅")

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(f"Database error: {err}")

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

elif menu == "Prescriptions":

    st.header("💊 Prescription Management")

    # ============================================================
    # 1. VIEW PRESCRIPTIONS
    # ============================================================

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            pr.prescription_id,
            pr.record_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
            pr.prescription_date,
            pr.instructions
        FROM Prescription pr
        INNER JOIN Medical_Record mr
            ON pr.record_id = mr.record_id
        INNER JOIN Appointment a
            ON mr.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        ORDER BY pr.prescription_date DESC;
    """)

    prescriptions = cursor.fetchall()

    cursor.close()
    connection.close()

    st.subheader("📋 Prescriptions")

    if prescriptions:
        st.dataframe(
            prescriptions,
            use_container_width=True
        )
    else:
        st.info("No prescriptions found.")


    # ============================================================
    # 2. CREATE PRESCRIPTION
    # ============================================================

    st.subheader("➕ Create Prescription")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            mr.record_id,
            CONCAT(p.first_name, ' ', p.last_name) AS patient_name,
            CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name
        FROM Medical_Record mr
        INNER JOIN Appointment a
            ON mr.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Doctor d
            ON a.doctor_id = d.doctor_id
        LEFT JOIN Prescription pr
            ON mr.record_id = pr.record_id
        WHERE pr.prescription_id IS NULL
        ORDER BY mr.record_date DESC;
    """)

    eligible_records = cursor.fetchall()

    cursor.close()
    connection.close()

    if eligible_records:

        record_options = {
            f'{r["record_id"]} - '
            f'{r["patient_name"]} with {r["doctor_name"]}':
            r["record_id"]
            for r in eligible_records
        }

        selected_record = st.selectbox(
            "Select Medical Record",
            list(record_options.keys())
        )

        with st.form("prescription_form"):

            prescription_date = st.date_input(
                "Prescription Date"
            )

            instructions = st.text_area(
                "General Instructions"
            )

            submitted = st.form_submit_button(
                "💊 Create Prescription"
            )

        if submitted:

            record_id = record_options[selected_record]

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Prescription
                    (
                        record_id,
                        prescription_date,
                        instructions
                    )
                    VALUES (%s, %s, %s)
                """

                values = (
                    record_id,
                    prescription_date,
                    instructions
                )

                cursor.execute(query, values)

                connection.commit()

                st.success(
                    "Prescription created successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

    else:

        st.info(
            "No medical records are available for creating a new prescription."
        )


    # ============================================================
    # 3. ADD MEDICINE TO PRESCRIPTION
    # ============================================================

    st.subheader("💊 Add Medicine to Prescription")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch prescriptions
    cursor.execute("""
        SELECT
            pr.prescription_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            pr.prescription_date
        FROM Prescription pr
        INNER JOIN Medical_Record mr
            ON pr.record_id = mr.record_id
        INNER JOIN Appointment a
            ON mr.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        ORDER BY pr.prescription_id DESC;
    """)

    prescription_options_data = cursor.fetchall()

    # Fetch medicines
    cursor.execute("""
        SELECT
            medicine_id,
            medicine_name,
            manufacturer,
            unit_price,
            stock_quantity
        FROM Medicine
        WHERE stock_quantity > 0
        ORDER BY medicine_name;
    """)

    medicines = cursor.fetchall()

    cursor.close()
    connection.close()


    if prescription_options_data and medicines:

        prescription_options = {
            f'{p["prescription_id"]} - '
            f'{p["patient_name"]} '
            f'({p["prescription_date"]})':
            p["prescription_id"]
            for p in prescription_options_data
        }

        medicine_options = {
            f'{m["medicine_name"]} - '
            f'{m["manufacturer"]} '
            f'(₹{m["unit_price"]}) '
            f'[Stock: {m["stock_quantity"]}]':
            m
            for m in medicines
        }

        selected_prescription = st.selectbox(
            "Select Prescription",
            list(prescription_options.keys())
        )

        selected_medicine = st.selectbox(
            "Select Medicine",
            list(medicine_options.keys())
        )

        selected_medicine_data = medicine_options[
            selected_medicine
        ]

        with st.form("prescription_item_form"):

            dosage = st.text_input(
                "Dosage",
                placeholder="e.g. 500 mg"
            )

            frequency = st.text_input(
                "Frequency",
                placeholder="e.g. Twice daily"
            )

            duration = st.text_input(
                "Duration",
                placeholder="e.g. 5 days"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

            submitted_item = st.form_submit_button(
                "➕ Add Medicine"
            )

        if submitted_item:

            prescription_id = prescription_options[
                selected_prescription
            ]

            medicine_id = selected_medicine_data[
                "medicine_id"
            ]

            current_stock = selected_medicine_data[
                "stock_quantity"
            ]

            # Basic validation
            if not dosage.strip():
                st.error("Please enter the dosage.")
                st.stop()

            if not frequency.strip():
                st.error("Please enter the frequency.")
                st.stop()

            if quantity > current_stock:
                st.error(
                    f"Only {current_stock} units are available in stock."
                )
                st.stop()

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                # Start transaction
                connection.start_transaction()

                # Insert prescription item
                insert_query = """
                    INSERT INTO Prescription_Item
                    (
                        prescription_id,
                        medicine_id,
                        dosage,
                        frequency,
                        duration,
                        quantity
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """

                insert_values = (
                    prescription_id,
                    medicine_id,
                    dosage,
                    frequency,
                    duration,
                    quantity
                )

                cursor.execute(
                    insert_query,
                    insert_values
                )

                # Reduce medicine stock
                update_stock_query = """
                    UPDATE Medicine
                    SET stock_quantity = stock_quantity - %s
                    WHERE medicine_id = %s
                """

                cursor.execute(
                    update_stock_query,
                    (
                        quantity,
                        medicine_id
                    )
                )

                # Commit both operations
                connection.commit()

                st.success(
                    "Medicine added to prescription successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

    elif not prescription_options_data:

        st.info(
            "Create a prescription first before adding medicines."
        )

    elif not medicines:

        st.warning(
            "No medicines with available stock."
        )


    # ============================================================
    # 4. VIEW PRESCRIPTION MEDICINES
    # ============================================================

    st.subheader("📋 Prescription Medicines")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            pi.prescription_item_id,
            pi.prescription_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            m.medicine_name,
            pi.dosage,
            pi.frequency,
            pi.duration,
            pi.quantity,
            m.unit_price,
            (pi.quantity * m.unit_price) AS medicine_cost
        FROM Prescription_Item pi
        INNER JOIN Prescription pr
            ON pi.prescription_id = pr.prescription_id
        INNER JOIN Medical_Record mr
            ON pr.record_id = mr.record_id
        INNER JOIN Appointment a
            ON mr.appointment_id = a.appointment_id
        INNER JOIN Patient p
            ON a.patient_id = p.patient_id
        INNER JOIN Medicine m
            ON pi.medicine_id = m.medicine_id
        ORDER BY pi.prescription_id DESC;
    """)

    prescription_items = cursor.fetchall()

    cursor.close()
    connection.close()

    if prescription_items:

        st.dataframe(
            prescription_items,
            use_container_width=True
        )

    else:

        st.info(
            "No medicines have been added to prescriptions yet."
        )

elif menu == "Billing":

    st.header("💰 Billing Management")

    # ============================================================
    # 1. VIEW BILLS
    # ============================================================

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            b.bill_id,
            b.patient_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            b.appointment_id,
            b.bill_date,
            b.payment_status,
            b.payment_method,
            COALESCE(
                SUM(bi.amount),
                0
            ) AS total_amount
        FROM Bill b
        INNER JOIN Patient p
            ON b.patient_id = p.patient_id
        LEFT JOIN Bill_Item bi
            ON b.bill_id = bi.bill_id
        GROUP BY
            b.bill_id,
            b.patient_id,
            p.first_name,
            p.last_name,
            b.appointment_id,
            b.bill_date,
            b.payment_status,
            b.payment_method
        ORDER BY b.bill_date DESC;
    """)

    bills = cursor.fetchall()

    cursor.close()
    connection.close()

    st.subheader("📋 Bills")

    if bills:

        st.dataframe(
            bills,
            use_container_width=True
        )

    else:

        st.info("No bills found.")


    # ============================================================
    # 2. CREATE BILL
    # ============================================================

    st.subheader("➕ Create New Bill")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            patient_id,
            first_name,
            last_name
        FROM Patient
        WHERE status = 'Active'
        ORDER BY first_name, last_name;
    """)

    patients = cursor.fetchall()

    cursor.execute("""
        SELECT
            appointment_id,
            patient_id,
            appointment_date
        FROM Appointment
        WHERE status IN ('Scheduled', 'Completed')
        ORDER BY appointment_date DESC;
    """)

    appointments = cursor.fetchall()

    cursor.close()
    connection.close()


    if patients:

        patient_options = {
            f'{p["patient_id"]} - '
            f'{p["first_name"]} '
            f'{p["last_name"]}':
            p["patient_id"]
            for p in patients
        }

        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys())
        )

        patient_id = patient_options[selected_patient]

        # Only show appointments belonging to selected patient
        patient_appointments = [
            a for a in appointments
            if a["patient_id"] == patient_id
        ]

        appointment_options = {
            f'{a["appointment_id"]} - '
            f'{a["appointment_date"]}':
            a["appointment_id"]
            for a in patient_appointments
        }

        appointment_options_with_none = {
            "No Appointment": None,
            **appointment_options
        }

        selected_appointment = st.selectbox(
            "Select Appointment",
            list(appointment_options_with_none.keys())
        )

        appointment_id = appointment_options_with_none[
            selected_appointment
        ]

        with st.form("create_bill_form"):

            bill_date = st.date_input(
                "Bill Date"
            )

            payment_status = st.selectbox(
                "Payment Status",
                [
                    "Pending",
                    "Paid"
                ]
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "Cash",
                    "UPI",
                    "Card",
                    "Net Banking"
                ]
            )

            submitted = st.form_submit_button(
                "💰 Create Bill"
            )

        if submitted:

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Bill
                    (
                        patient_id,
                        appointment_id,
                        bill_date,
                        payment_status,
                        payment_method
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """

                values = (
                    patient_id,
                    appointment_id,
                    bill_date,
                    payment_status,
                    payment_method
                )

                cursor.execute(
                    query,
                    values
                )

                connection.commit()

                st.success(
                    "Bill created successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()


    # ============================================================
    # 3. ADD BILL ITEM
    # ============================================================

    st.subheader("➕ Add Item to Bill")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            b.bill_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            b.bill_date
        FROM Bill b
        INNER JOIN Patient p
            ON b.patient_id = p.patient_id
        ORDER BY b.bill_id DESC;
    """)

    bill_options_data = cursor.fetchall()

    cursor.close()
    connection.close()


    if bill_options_data:

        bill_options = {
            f'Bill #{b["bill_id"]} - '
            f'{b["patient_name"]} '
            f'({b["bill_date"]})':
            b["bill_id"]
            for b in bill_options_data
        }

        selected_bill = st.selectbox(
            "Select Bill",
            list(bill_options.keys())
        )

        bill_id = bill_options[selected_bill]

        with st.form("bill_item_form"):

            description = st.text_input(
                "Description",
                placeholder="e.g. Consultation"
            )

            quantity = st.number_input(
                "Quantity",
                min_value=1,
                step=1
            )

            unit_price = st.number_input(
                "Unit Price",
                min_value=0.0,
                step=50.0
            )

            submitted_item = st.form_submit_button(
                "➕ Add Bill Item"
            )

        if submitted_item:

            if not description.strip():
                st.error(
                    "Please enter a description."
                )
                st.stop()

            amount = quantity * unit_price

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    INSERT INTO Bill_Item
                    (
                        bill_id,
                        description,
                        quantity,
                        unit_price,
                        amount
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """

                values = (
                    bill_id,
                    description,
                    quantity,
                    unit_price,
                    amount
                )

                cursor.execute(
                    query,
                    values
                )

                connection.commit()

                st.success(
                    "Bill item added successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()


    # ============================================================
    # 4. VIEW BILL ITEMS
    # ============================================================

    st.subheader("📋 Bill Items")

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            bi.bill_item_id,
            bi.bill_id,
            CONCAT(
                p.first_name,
                ' ',
                p.last_name
            ) AS patient_name,
            bi.description,
            bi.quantity,
            bi.unit_price,
            bi.amount
        FROM Bill_Item bi
        INNER JOIN Bill b
            ON bi.bill_id = b.bill_id
        INNER JOIN Patient p
            ON b.patient_id = p.patient_id
        ORDER BY bi.bill_id DESC;
    """)

    bill_items = cursor.fetchall()

    cursor.close()
    connection.close()

    if bill_items:

        st.dataframe(
            bill_items,
            use_container_width=True
        )

    else:

        st.info(
            "No bill items have been added yet."
        )


    # ============================================================
    # 5. UPDATE PAYMENT STATUS
    # ============================================================

    st.subheader("🔄 Update Payment Status")

    if bills:

        bill_status_options = {
            f'Bill #{b["bill_id"]} - '
            f'{b["patient_name"]} '
            f'(₹{b["total_amount"]})':
            b
            for b in bills
        }

        selected_bill_status = st.selectbox(
            "Select Bill",
            list(bill_status_options.keys())
        )

        selected_bill_data = bill_status_options[
            selected_bill_status
        ]

        payment_status_options = [
            "Pending",
            "Paid"
        ]

        current_status = selected_bill_data[
            "payment_status"
        ]

        status_index = (
            payment_status_options.index(
                current_status
            )
            if current_status in payment_status_options
            else 0
        )

        new_payment_status = st.selectbox(
            "Payment Status",
            payment_status_options,
            index=status_index
        )

        payment_method_options = [
            "Cash",
            "UPI",
            "Card",
            "Net Banking"
        ]

        current_method = selected_bill_data[
            "payment_method"
        ]

        method_index = (
            payment_method_options.index(
                current_method
            )
            if current_method in payment_method_options
            else 0
        )

        new_payment_method = st.selectbox(
            "Payment Method",
            payment_method_options,
            index=method_index
        )

        if st.button("🔄 Update Payment"):

            connection = None
            cursor = None

            try:

                connection = get_connection()
                cursor = connection.cursor()

                query = """
                    UPDATE Bill
                    SET
                        payment_status = %s,
                        payment_method = %s
                    WHERE bill_id = %s
                """

                values = (
                    new_payment_status,
                    new_payment_method,
                    selected_bill_data["bill_id"]
                )

                cursor.execute(
                    query,
                    values
                )

                connection.commit()

                st.success(
                    "Payment information updated successfully! ✅"
                )

                st.rerun()

            except mysql.connector.Error as err:

                if connection:
                    connection.rollback()

                st.error(
                    f"Database error: {err}"
                )

            finally:

                if cursor:
                    cursor.close()

                if connection:
                    connection.close()

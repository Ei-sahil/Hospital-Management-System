import streamlit as st
import pandas as pd
import mysql.connector

from db import get_connection

st.set_page_config(
    page_title="Hospital Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Hospital Data Analytics")
st.caption(
    "Operational and business insights generated from the hospital management database. "
    "This page uses aggregate data and does not display patient-level medical details."
)

def query_df(connection, query):
    """Execute a SELECT query and return its rows as a Pandas DataFrame."""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        frame = pd.DataFrame(rows)
        # MySQL DECIMAL values arrive as Decimal objects; convert numeric
        # columns so Streamlit charts and Pandas calculations handle them.
        for column in frame.columns:
            if frame[column].dtype == "object":
                numeric = pd.to_numeric(frame[column], errors="coerce")
                if numeric.notna().any():
                    frame[column] = numeric
        return frame
    finally:
        cursor.close()


@st.cache_data(ttl=60, show_spinner=False)
def load_analytics():
    """Load aggregate datasets from MySQL; cache briefly to reduce database queries."""
    connection = get_connection()
    try:
        # Revenue is aggregated per bill first to avoid multiplying bill totals
        # when joining a bill to its individual line items.
        revenue = query_df(connection,
            """
            SELECT
                DATE_FORMAT(b.bill_date, '%Y-%m') AS month,
                ROUND(SUM(COALESCE(items.bill_total, 0)), 2) AS billed_revenue,
                ROUND(SUM(
                    CASE WHEN b.payment_status = 'Paid'
                         THEN COALESCE(items.bill_total, 0)
                         ELSE 0 END
                ), 2) AS collected_revenue
            FROM Bill b
            LEFT JOIN (
                SELECT bill_id, SUM(amount) AS bill_total
                FROM Bill_Item
                GROUP BY bill_id
            ) items ON items.bill_id = b.bill_id
            GROUP BY DATE_FORMAT(b.bill_date, '%Y-%m')
            ORDER BY month
            """,
        )

        appointments = query_df(connection, """
            SELECT
                DATE_FORMAT(appointment_date, '%Y-%m') AS month,
                COUNT(*) AS appointments
            FROM Appointment
            GROUP BY DATE_FORMAT(appointment_date, '%Y-%m')
            ORDER BY month
            """)

        appointment_status = query_df(connection, """
            SELECT status, COUNT(*) AS total
            FROM Appointment
            GROUP BY status
            ORDER BY total DESC
            """)

        departments = query_df(connection, """
            SELECT dep.department_name, COUNT(a.appointment_id) AS appointments
            FROM Department dep
            LEFT JOIN Doctor d ON d.department_id = dep.department_id
            LEFT JOIN Appointment a ON a.doctor_id = d.doctor_id
            GROUP BY dep.department_id, dep.department_name
            ORDER BY appointments DESC, dep.department_name
            """)

        doctors = query_df(connection, """
            SELECT
                CONCAT('Dr. ', d.first_name, ' ', d.last_name) AS doctor_name,
                d.specialization,
                COUNT(a.appointment_id) AS appointments
            FROM Doctor d
            LEFT JOIN Appointment a ON a.doctor_id = d.doctor_id
            GROUP BY d.doctor_id, d.first_name, d.last_name, d.specialization
            ORDER BY appointments DESC, doctor_name
            LIMIT 10
            """)

        patients = query_df(connection, """
            SELECT
                DATE_FORMAT(registration_date, '%Y-%m') AS month,
                COUNT(*) AS new_patients
            FROM Patient
            GROUP BY DATE_FORMAT(registration_date, '%Y-%m')
            ORDER BY month
            """)

        lab_tests = query_df(connection, """
            SELECT test_name, COUNT(*) AS total_tests,
                   ROUND(SUM(cost), 2) AS total_cost
            FROM Lab_Test
            GROUP BY test_name
            ORDER BY total_tests DESC, test_name
            LIMIT 10
            """)

        summary = query_df(connection, """
            SELECT
                (SELECT COUNT(*) FROM Patient WHERE status = 'Active') AS active_patients,
                (SELECT COUNT(*) FROM Doctor WHERE status = 'Active') AS active_doctors,
                (SELECT COUNT(*) FROM Appointment) AS total_appointments,
                (SELECT COUNT(*) FROM Bill WHERE payment_status = 'Pending') AS pending_bills,
                (SELECT COALESCE(SUM(bi.amount), 0)
                   FROM Bill b
                   LEFT JOIN Bill_Item bi ON bi.bill_id = b.bill_id
                  WHERE b.payment_status = 'Pending') AS pending_amount,
                (SELECT COALESCE(SUM(bi.amount), 0)
                   FROM Bill b
                   LEFT JOIN Bill_Item bi ON bi.bill_id = b.bill_id
                  WHERE b.payment_status = 'Paid') AS collected_amount
            """)
        return revenue, appointments, appointment_status, departments, doctors, patients, lab_tests, summary
    finally:
        connection.close()


try:
    with st.spinner("Loading hospital analytics from MySQL..."):
        revenue, appointments, appointment_status, departments, doctors, patients, lab_tests, summary = load_analytics()

    s = summary.iloc[0]
    st.subheader("Hospital overview")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Active patients", f"{int(s['active_patients']):,}")
    k2.metric("Active doctors", f"{int(s['active_doctors']):,}")
    k3.metric("Total appointments", f"{int(s['total_appointments']):,}")
    k4.metric("Pending bills", f"{int(s['pending_bills']):,}")

    k5, k6 = st.columns(2)
    k5.metric("Collected revenue", f"₹{float(s['collected_amount']):,.2f}")
    k6.metric("Outstanding amount", f"₹{float(s['pending_amount']):,.2f}")

    st.divider()
    st.subheader("Revenue performance")
    if not revenue.empty:
        left, right = st.columns(2)
        with left:
            st.caption("Billed revenue by month")
            st.bar_chart(revenue.set_index("month")[["billed_revenue"]])
        with right:
            st.caption("Collected revenue by month")
            st.line_chart(revenue.set_index("month")[["collected_revenue"]])
        st.dataframe(revenue, use_container_width=True, hide_index=True)
    else:
        st.info("No billing records are available yet.")

    st.divider()
    st.subheader("Appointment analysis")
    left, right = st.columns(2)
    with left:
        st.caption("Appointment status distribution")
        if not appointment_status.empty:
            st.bar_chart(appointment_status.set_index("status")[["total"]])
        else:
            st.info("No appointment records are available.")
    with right:
        st.caption("Monthly appointment trend")
        if not appointments.empty:
            st.line_chart(appointments.set_index("month")[["appointments"]])
        else:
            st.info("No appointment records are available.")

    st.divider()
    st.subheader("Department and doctor workload")
    left, right = st.columns(2)
    with left:
        st.caption("Appointments by department")
        if not departments.empty:
            st.bar_chart(departments.set_index("department_name")[["appointments"]])
            st.dataframe(departments, use_container_width=True, hide_index=True)
        else:
            st.info("No department records are available.")
    with right:
        st.caption("Top doctors by appointment volume")
        if not doctors.empty:
            st.bar_chart(doctors.set_index("doctor_name")[["appointments"]])
            st.dataframe(doctors, use_container_width=True, hide_index=True)
        else:
            st.info("No doctor records are available.")

    st.divider()
    st.subheader("Patient registration trend")
    if not patients.empty:
        st.area_chart(patients.set_index("month")[["new_patients"]])
        st.dataframe(patients, use_container_width=True, hide_index=True)
    else:
        st.info("No patient registration records are available.")

    st.subheader("Laboratory test analysis")
    if not lab_tests.empty:
        st.bar_chart(lab_tests.set_index("test_name")[["total_tests"]])
        st.dataframe(lab_tests, use_container_width=True, hide_index=True)
    else:
        st.info("No laboratory test records are available.")

    st.divider()
    st.subheader("Export analytics")
    export_frames = {
        "monthly_revenue": revenue,
        "monthly_appointments": appointments,
        "appointment_status": appointment_status,
        "department_appointments": departments,
        "doctor_workload": doctors,
        "patient_registrations": patients,
        "laboratory_tests": lab_tests,
    }
    selected_export = st.selectbox("Choose an aggregate report", list(export_frames.keys()))
    export_data = export_frames[selected_export]
    st.download_button(
        "Download CSV",
        data=export_data.to_csv(index=False).encode("utf-8"),
        file_name=f"{selected_export}.csv",
        mime="text/csv",
        disabled=export_data.empty
    )

    st.caption(
        "Interpretation note: these indicators describe the records currently stored in the database. "
        "Small or sample datasets may not represent real hospital-wide performance."
    )

except mysql.connector.Error as err:
    st.error("Could not load analytics from the hospital database.")
    st.code(str(err))
    st.info(
        "Check the MySQL connection settings in Streamlit secrets and confirm that the database schema "
        "and sample data have been imported."
    )
except Exception as err:
    st.error("An unexpected error occurred while preparing the analytics dashboard.")
    st.code(str(err))

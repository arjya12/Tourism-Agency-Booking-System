import streamlit as st
import cx_Oracle
from datetime import datetime

def update_booking(conn):
    if not conn:
        st.error("No database connection.")
        return

    st.subheader("Update Booking")
    cursor = None

    try:
        cursor = conn.cursor()
        # Fetch bookings
        cursor.execute("""
            SELECT 
                b.booking_id,
                u.first_name || ' ' || u.last_name AS customer_name,
                p.package_name,
                b.booking_date
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN packages p ON b.package_id = p.package_id
            ORDER BY b.booking_date DESC
        """)
        
        bookings = cursor.fetchall()
        if not bookings:
            st.info("No bookings available to update.")
            return

        # Map booking options for dropdown
        booking_options = {f"#{b[0]} - {b[1]} - {b[2]} ({b[3]})": b[0] for b in bookings}
        selected_booking = st.selectbox("Select Booking to Update", options=list(booking_options.keys()))
        booking_id = booking_options[selected_booking]

        # Fetch selected booking details
        cursor.execute("""
            SELECT 
                b.booking_id,
                u.first_name,
                u.last_name,
                u.email,
                p.package_id,
                b.booking_date
            FROM bookings b
            JOIN users u ON b.user_id = u.id
            JOIN packages p ON b.package_id = p.package_id
            WHERE b.booking_id = :1
        """, (booking_id,))
        current_data = cursor.fetchone()

        if not current_data:
            st.error("Unable to fetch booking details.")
            return

        # Update form
        with st.form("update_booking_form"):
            st.subheader("Update Booking Details")
            col1, col2 = st.columns(2)

            with col1:
                first_name = st.text_input("First Name", value=current_data[1])
                last_name = st.text_input("Last Name", value=current_data[2])
                email = st.text_input("Email", value=current_data[3])

            with col2:
                # Fetch packages for selection
                cursor.execute("""
                    SELECT p.package_id, p.package_name 
                    FROM packages p 
                    ORDER BY p.package_name
                """)
                packages = cursor.fetchall()
                package_options = {pkg[1]: pkg[0] for pkg in packages}
                selected_package = st.selectbox(
                    "Select Package",
                    options=list(package_options.keys()),
                    index=list(package_options.values()).index(current_data[4]) if current_data[4] in package_options.values() else 0
                )
                booking_date = st.date_input("Booking Date", value=current_data[5].date())

            submit = st.form_submit_button("Update Booking")

            if submit:
                # Input validation
                if not first_name or not last_name or not email:
                    st.error("Please fill in all required fields.")
                    return
                if "@" not in email:
                    st.error("Invalid email address.")
                    return

                # Update user and booking data
                try:
                    # Update user data
                    cursor.execute("""
                        UPDATE users 
                        SET first_name = :1, last_name = :2, email = :3 
                        WHERE id = (SELECT user_id FROM bookings WHERE booking_id = :4)
                    """, (first_name, last_name, email, booking_id))

                    # Update booking data
                    cursor.execute("""
                        UPDATE bookings 
                        SET package_id = :1, booking_date = :2 
                        WHERE booking_id = :3
                    """, (package_options[selected_package], booking_date, booking_id))

                    conn.commit()
                    st.success(f"Booking #{booking_id} updated successfully!")
                    st.rerun()

                except cx_Oracle.DatabaseError as e:
                    conn.rollback()
                    st.error(f"Error updating booking: {e}")

    except cx_Oracle.DatabaseError as e:
        st.error(f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
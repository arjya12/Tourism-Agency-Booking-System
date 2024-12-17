import streamlit as st
import cx_Oracle
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.validators import validate_email

def view_bookings(conn):
    """Display all bookings in a table format with sequential IDs"""
    if not conn:
        st.error("No database connection.")
        return
        
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                ROW_NUMBER() OVER (ORDER BY b.booking_date) AS display_id,
                b.booking_id,
                u.first_name || ' ' || u.last_name AS customer_name,
                p.package_name,
                d.destination_name,
                d.country,
                p.price,
                b.booking_date
            FROM 
                bookings b
            JOIN users u ON b.user_id = u.id
            JOIN packages p ON b.package_id = p.package_id
            JOIN destinations d ON p.destination_id = d.destination_id
            ORDER BY b.booking_date
        """)
        
        columns = ['ID', 'Booking ID', 'Customer Name', 'Package', 'Destination', 'Country', 'Price', 'Booking Date']
        data = cursor.fetchall()
        
        if data:
            df = pd.DataFrame(data, columns=columns)
            df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}")
            df['Booking Date'] = pd.to_datetime(df['Booking Date']).dt.strftime('%Y-%m-%d')
            df = df.drop('Booking ID', axis=1)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No bookings found.")
            
    except cx_Oracle.DatabaseError as e:
        st.error(f"Error viewing bookings: {e}")
    finally:
        if cursor:
            cursor.close()

def create_booking(conn):
    """Create a new booking with validation"""
    if not conn:
        st.error("No database connection.")
        return
        
    cursor = None
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.package_id, p.package_name, d.destination_name, d.country, p.price 
            FROM packages p 
            JOIN destinations d ON p.destination_id = d.destination_id
            ORDER BY p.package_name
        """)
        packages = cursor.fetchall()
        if not packages:
            st.error("No packages available. Please initialize the database first.")
            return
            
        package_options = {f"{pkg[1]} ({pkg[2]}, {pkg[3]}) - ${pkg[4]:,.2f}": pkg[0] for pkg in packages}
        
        with st.form("booking_form"):
            st.subheader("Create New Booking")
            
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                last_name = st.text_input("Last Name")
                email = st.text_input("Email")
            
            with col2:
                selected_package = st.selectbox("Select Package", options=list(package_options.keys()))
                booking_date = st.date_input("Booking Date", min_value=datetime.now().date())
            
            submit = st.form_submit_button("Create Booking")
            
            if submit:
                if not first_name or not last_name or not email:
                    st.error("Please fill in all required fields")
                    return
                
                if not validate_email(email):
                    st.error("Please enter a valid email address")
                    return
                
                try:
                    cursor.execute(
                        "SELECT id FROM users WHERE UPPER(email) = UPPER(:1)",
                        (email,)
                    )
                    user_result = cursor.fetchone()
                    
                    if not user_result:
                        cursor.execute(
                            "INSERT INTO users (id, first_name, last_name, email) VALUES (users_seq.NEXTVAL, :1, :2, :3)",
                            (first_name, last_name, email)
                        )
                        cursor.execute("SELECT users_seq.CURRVAL FROM dual")
                        user_id = cursor.fetchone()[0]
                    else:
                        user_id = user_result[0]
                    
                    package_id = package_options[selected_package]
                    cursor.execute(
                        """
                        INSERT INTO bookings (booking_id, user_id, package_id, booking_date)
                        VALUES (bookings_seq.NEXTVAL, :1, :2, :3)
                        """,
                        (user_id, package_id, booking_date)
                    )
                    
                    conn.commit()
                    st.success("Booking created successfully!")
                    st.rerun()
                    
                except cx_Oracle.DatabaseError as e:
                    conn.rollback()
                    st.error(f"Error creating booking: {e}")
                    
    except cx_Oracle.DatabaseError as e:
        st.error(f"Error accessing database: {e}")
    finally:
        if cursor:
            cursor.close()
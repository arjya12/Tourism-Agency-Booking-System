import streamlit as st
import cx_Oracle
import pandas as pd
from datetime import datetime

def search_bookings(conn):
    """Search bookings with various criteria"""
    if not conn:
        st.error("No database connection.")
        return
        
    st.subheader("Search Bookings")
    
    search_type = st.radio(
        "Search by:",
        ["Customer Name", "Destination", "Date Range", "Price Range"]
    )
    
    cursor = None
    try:
        cursor = conn.cursor()
        base_query = """
            SELECT 
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
        """
        
        params = []
        where_clause = ""
        search_clicked = False
        
        if search_type == "Customer Name":
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
            with col2:
                last_name = st.text_input("Last Name")
                
            if st.button("Search"):
                search_clicked = True
                where_clause = """
                    WHERE (UPPER(u.first_name) LIKE UPPER(:1))
                    AND (UPPER(u.last_name) LIKE UPPER(:2))
                """
                params = [f"%{first_name}%", f"%{last_name}%"]
                
        elif search_type == "Destination":
            destination = st.text_input("Enter destination or country")
            if st.button("Search"):
                search_clicked = True
                where_clause = """
                    WHERE UPPER(d.destination_name) LIKE UPPER(:1)
                    OR UPPER(d.country) LIKE UPPER(:1)
                """
                params = [f"%{destination}%"]
                
        elif search_type == "Date Range":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date")
            with col2:
                end_date = st.date_input("End Date")
                
            if st.button("Search"):
                search_clicked = True
                where_clause = """
                    WHERE b.booking_date BETWEEN :1 AND :2
                """
                params = [start_date, end_date]
                
        elif search_type == "Price Range":
            col1, col2 = st.columns(2)
            with col1:
                min_price = st.number_input("Minimum Price", min_value=0.0, value=0.0)
            with col2:
                max_price = st.number_input("Maximum Price", min_value=0.0, value=5000.0)
                
            if st.button("Search"):
                search_clicked = True
                where_clause = "WHERE p.price BETWEEN :1 AND :2"
                params = [min_price, max_price]
        
        if search_clicked:
            try:
                query = base_query + where_clause + " ORDER BY b.booking_date"
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                if results:
                    columns = ['Booking ID', 'Customer Name', 'Package', 'Destination', 'Country', 'Price', 'Booking Date']
                    df = pd.DataFrame(results, columns=columns)
                    df['Price'] = df['Price'].apply(lambda x: f"${x:,.2f}")
                    df['Booking Date'] = pd.to_datetime(df['Booking Date']).dt.strftime('%Y-%m-%d')
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No bookings found matching your search criteria.")
                    
            except cx_Oracle.DatabaseError as e:
                st.error(f"Error during search: {e}")
                
    except cx_Oracle.DatabaseError as e:
        st.error(f"Error accessing database: {e}")
    finally:
        if cursor:
            cursor.close()
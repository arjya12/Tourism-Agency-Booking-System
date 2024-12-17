import streamlit as st
from config import PAGE_TITLE, PAGE_LAYOUT
from database.connection import connect_to_oracle
from operations.booking_ops import view_bookings, create_booking
from operations.search_ops import search_bookings
from operations.update_ops import update_booking
from operations.delete_ops import delete_booking
from database.initialization import complete_reset


def main():
    st.set_page_config(page_title="Travel Booking System", layout="wide")
    st.title("Travel Booking System")
    
    # Database connection
    conn = connect_to_oracle()
    if not conn:
        st.error("Failed to connect to the database.")
        return

    # Sidebar navigation and database management
    st.sidebar.title("Navigation")
    
    # Database management section
    st.sidebar.markdown("---")
    st.sidebar.subheader("Database Management")
    if st.sidebar.button("Initialize/Reset Database"):
        if complete_reset(conn):
            st.rerun()
    
    # Page navigation
    page = st.sidebar.radio("Select Operation", 
        ["View Bookings", "Create Booking", "Search Bookings", "Update Booking", "Delete Booking"]
    )
    
    # Main content
    if page == "View Bookings":
        st.subheader("Current Bookings")
        view_bookings(conn)
    elif page == "Create Booking":
        create_booking(conn)
    elif page == "Search Bookings":
        search_bookings(conn)
    elif page == "Delete Booking":
        delete_booking(conn)
    elif page == "Update Booking":
        update_booking(conn)

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("© 2024 Travel Booking System")

    # Clean up
    if conn:
        conn.close()

if __name__ == "__main__":
    main()
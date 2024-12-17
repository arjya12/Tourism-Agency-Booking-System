import streamlit as st
import cx_Oracle

def delete_booking(conn):
    st.subheader("Delete Booking")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            b.booking_id,
            u.first_name || ' ' || u.last_name AS customer_name,
            p.package_name,
            b.booking_date
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN packages p ON b.package_id = p.package_id
        ORDER BY b.booking_date
    """)
    
    bookings = cursor.fetchall()
    if not bookings:
        st.info("No bookings available to delete.")
        return
    
    booking_options = {f"#{b[0]} - {b[1]} - {b[2]} ({b[3].strftime('%Y-%m-%d')})": b[0] for b in bookings}
    selected_booking = st.selectbox("Select Booking to Delete", options=list(booking_options.keys()))
    
    if st.button("Delete Booking"):
        try:
            booking_id = booking_options[selected_booking]
            cursor.execute("DELETE FROM bookings WHERE booking_id = :1", (booking_id,))
            conn.commit()
            st.success(f"Booking {booking_id} deleted successfully!")
        except cx_Oracle.DatabaseError as e:
            conn.rollback()
            st.error(f"Error deleting booking: {e}")
        finally:
            cursor.close()

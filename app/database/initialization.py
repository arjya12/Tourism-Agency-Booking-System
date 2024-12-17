import cx_Oracle
import streamlit as st
from .connection import connect_to_oracle

def populate_sample_data(cursor):
    """Populate database with sample data"""
    try:
        # Sample users
        users_data = [
            ('Alice', 'Johnson', 'alice.johnson@example.com'),
            ('Bob', 'Smith', 'bob.smith@example.com'),
            ('Charlie', 'Brown', 'charlie.brown@example.com'),
            ('Diana', 'Miller', 'diana.miller@example.com'),
            ('Edward', 'Wilson', 'edward.wilson@example.com')
        ]
        
        user_ids = {}
        for first_name, last_name, email in users_data:
            cursor.execute(
                "INSERT INTO users (id, first_name, last_name, email) VALUES (users_seq.NEXTVAL, :1, :2, :3)",
                (first_name, last_name, email)
            )
            cursor.execute("SELECT id FROM users WHERE email = :1", (email,))
            user_ids[first_name] = cursor.fetchone()[0]

        # Sample destinations
        destinations_data = [
            (1, 'New York', 'USA'),
            (2, 'Paris', 'France'),
            (3, 'Rome', 'Italy'),
            (4, 'Tokyo', 'Japan'),
            (5, 'Toronto', 'Canada')
        ]
        
        for dest_id, name, country in destinations_data:
            cursor.execute(
                "INSERT INTO destinations (destination_id, destination_name, country) VALUES (:1, :2, :3)",
                (dest_id, name, country)
            )

        # Sample packages
        packages_data = [
            (1, 'NYC City Break', 1500.00, 1),
            (2, 'NYC Shopping Special', 1700.00, 1),
            (3, 'Paris Budget Tour', 1400.00, 2),
            (4, 'Paris Luxury Tour', 2500.00, 2),
            (5, 'Rome Cultural Experience', 1800.00, 3),
            (6, 'Rome Family Package', 2300.00, 3),
            (7, 'Tokyo Adventure', 3000.00, 4),
            (8, 'Tokyo Traditional Tour', 2600.00, 4),
            (9, 'Toronto City Discovery', 1600.00, 5),
            (10, 'Toronto Niagara Falls Tour', 1800.00, 5)
        ]
        
        for pkg_id, name, price, dest_id in packages_data:
            cursor.execute(
                "INSERT INTO packages (package_id, package_name, price, destination_id) VALUES (:1, :2, :3, :4)",
                (pkg_id, name, price, dest_id)
            )
            
    except cx_Oracle.DatabaseError as e:
        st.error(f"Error populating sample data: {e}")
        raise

def complete_reset(conn):
    """Completely reset database and sequences"""
    cursor = None
    try:
        cursor = conn.cursor()
        
        # Drop all tables
        tables = ["bookings", "packages", "destinations", "users"]
        for table in tables:
            try:
                cursor.execute(f"DROP TABLE {table} CASCADE CONSTRAINTS")
            except cx_Oracle.DatabaseError:
                pass
        
        # Drop sequences
        sequences = ["users_seq", "bookings_seq"]
        for seq in sequences:
            try:
                cursor.execute(f"DROP SEQUENCE {seq}")
            except cx_Oracle.DatabaseError:
                pass
        
        # Create new sequences
        cursor.execute("""
            CREATE SEQUENCE users_seq
            START WITH 1
            INCREMENT BY 1
            MINVALUE 1
            MAXVALUE 9999999999
            NOCYCLE
            CACHE 20
            ORDER
        """)
        
        cursor.execute("""
            CREATE SEQUENCE bookings_seq
            START WITH 1
            INCREMENT BY 1
            MINVALUE 1
            MAXVALUE 9999999999
            NOCYCLE
            CACHE 20
            ORDER
        """)
        
        # Create tables
        cursor.execute("""
            CREATE TABLE users (
                id NUMBER PRIMARY KEY,
                first_name VARCHAR2(50),
                last_name VARCHAR2(50),
                email VARCHAR2(100) UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE destinations (
                destination_id NUMBER PRIMARY KEY,
                destination_name VARCHAR2(100),
                country VARCHAR2(100)
            )
        """)

        cursor.execute("""
            CREATE TABLE packages (
                package_id NUMBER PRIMARY KEY,
                package_name VARCHAR2(100),
                price NUMBER(10, 2),
                destination_id NUMBER REFERENCES destinations(destination_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE bookings (
                booking_id NUMBER PRIMARY KEY,
                user_id NUMBER REFERENCES users(id),
                package_id NUMBER REFERENCES packages(package_id),
                booking_date DATE
            )
        """)

        # Add sample data
        populate_sample_data(cursor)
        
        conn.commit()
        st.success("Database completely reset!")
        return True
        
    except cx_Oracle.DatabaseError as e:
        st.error(f"Error during complete reset: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
    finally:
        if cursor:
            cursor.close()
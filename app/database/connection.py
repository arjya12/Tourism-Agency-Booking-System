import cx_Oracle
import streamlit as ast
from config import DB_CONNECTION

def connect_to_oracle():
    """Establish database connection with enhanced error handling"""
    try:
        conn = cx_Oracle.connect(DB_CONNECTION)
        return conn
    except cx_Oracle.DatabaseError as e:
        st.error(f"Database connection error: {e}")
        st.write("Please check:")
        st.write("- Oracle client installation")
        st.write("- Database credentials")
        st.write("- Network connection to oracle.scs.ryerson.ca")
        return None
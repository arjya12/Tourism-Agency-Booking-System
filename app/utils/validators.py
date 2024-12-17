def validate_email(email):
    return '@' in email

def validate_booking_input(user_data, package_id, booking_date):
    if not all([user_data.get('first_name'), user_data.get('last_name'), user_data.get('email')]):
        st.error("Please fill in all required fields")
        return False
    if not validate_email(user_data['email']):
        st.error("Please enter a valid email address")
        return False
    return True
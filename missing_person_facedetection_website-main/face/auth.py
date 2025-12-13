import streamlit as st

# Hardcoded credentials for simplicity
CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# Login function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in CREDENTIALS and CREDENTIALS[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["role"] = username
            st.success(f"Logged in as {username.capitalize()}")
        else:
            st.error("Invalid username or password")


# Logout function
def logout():
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.success("Logged out successfully!")


# Check if user is logged in
def is_logged_in():
    return st.session_state.get("logged_in", False)


# Get the role of the logged-in user
def get_user_role():
    return st.session_state.get("role", None)
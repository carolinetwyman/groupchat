import streamlit as st
import psycopg2
import bcrypt
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except psycopg2.OperationalError as e:
        st.error("Database connection failed. Please check your credentials.")
        st.error(f"Error Details: {str(e)}")  # Display error details
        return None  # Avoid stopping the app

# Fetch user credentials from DB
def fetch_user_credentials():
    conn = get_db_connection()
    if not conn:
        return {}  # If DB fails, return an empty dict to prevent errors

    cursor = conn.cursor()
    cursor.execute("SELECT username, password, name FROM users")
    users = cursor.fetchall()
    conn.close()

    credentials = {"usernames": {}}
    for username, password, name in users:
        credentials["usernames"][username] = {
            "name": name,
            "password": password  # Hashed password stored
        }
    return credentials

# Hash password function
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Insert user into database
def insert_user(username, password, name):
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    hashed_password = hash_password(password)

    try:
        cursor.execute(
            sql.SQL("INSERT INTO users (username, password, name) VALUES (%s, %s, %s)"),
            (username, hashed_password, name)
        )
        conn.commit()
        st.success("User registered successfully! You can now log in.")
        st.session_state["show_register"] = False  # Hide register form after success
        st.query_params["rerun"] = "true"  # Trigger rerun
    except psycopg2.IntegrityError:
        conn.rollback()
        st.error("Username already exists. Please choose another one.")
    finally:
        conn.close()

# Authenticate user
def authenticate_user(username, password):
    credentials = fetch_user_credentials()
    if username in credentials["usernames"]:
        stored_password = credentials["usernames"][username]["password"]
        if bcrypt.checkpw(password.encode(), stored_password.encode()):
            return True, credentials["usernames"][username]["name"]
    return False, None

# Handle authentication state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Authentication page
if not st.session_state.authenticated:
    st.title("🔑 Sign In to Messenger Chat Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_username and login_password:
                authenticated, name = authenticate_user(login_username, login_password)
                if authenticated:
                    st.session_state.authenticated = True
                    st.session_state.username = login_username
                    st.session_state.name = name
                    st.success(f"Welcome *{name}*!")
                    st.query_params["rerun"] = "true"  # Trigger rerun
                else:
                    st.error("Username or password is incorrect")
            else:
                st.warning("Please enter your username and password")

    with col2:
        st.subheader("Register")

        if "show_register" not in st.session_state:
            st.session_state.show_register = False

        if st.session_state.show_register:
            new_username = st.text_input("Username", key="new_username")
            new_name = st.text_input("Full Name", key="new_name")
            new_password = st.text_input("Password", type="password", key="new_password")

            if st.button("Register"):
                if new_username and new_name and new_password:
                    insert_user(new_username, new_password, new_name)
                else:
                    st.warning("Please fill out all fields")

        else:
            if st.button("Don't have an account? Register here"):
                st.session_state.show_register = True
                st.query_params["rerun"] = "true"  # Trigger rerun

    st.stop()  # Stop rendering dashboard until login is successful

# After successful login, user is redirected to the main app
st.write(f"Welcome, {st.session_state.name}!")
st.write("Select a page from the sidebar to begin exploring!")
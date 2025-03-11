import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, date
from dotenv import load_dotenv

# Check if the user is authenticated
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 You must sign in to view this section.")
    st.stop()

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def connect_db():
    """Establish and return a PostgreSQL database connection."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def check_table_exists():
    """Verify if 'messages' table exists before running queries."""
    conn = connect_db()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'messages'
                );
            """)
            return cur.fetchone()[0]

    except Exception as e:
        st.error(f"❌ Error checking database tables: {e}")
        return False
    finally:
        conn.close()

def fetch_messages(start_date=None, end_date=None):
    """Fetch messages from PostgreSQL with optional date filtering."""
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    try:
        with conn.cursor() as cur:
            query = """
                SELECT 
                    m.id, 
                    p.name AS sender_name, 
                    m.content, 
                    to_timestamp(m.timestamp_ms / 1000) AS message_timestamp
                FROM messages m
                JOIN participants p ON m.sender_id = p.id
                WHERE m.content IS NOT NULL
            """
            
            params = []
            if start_date and end_date:
                start_datetime = datetime.combine(start_date, datetime.min.time())  # Fix conversion
                end_datetime = datetime.combine(end_date, datetime.max.time())

                query += " AND m.timestamp_ms BETWEEN %s AND %s"
                params = [int(start_datetime.timestamp() * 1000), int(end_datetime.timestamp() * 1000)]

            query += " ORDER BY m.timestamp_ms DESC LIMIT 100;"

            cur.execute(query, params)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)

    except Exception as e:
        st.error(f"❌ Error fetching messages: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()

# Streamlit UI
st.title("📊 Data Exploration - PostgreSQL")

# Check if database table exists
if not check_table_exists():
    st.error("❌ Database table 'messages' does not exist. Check your database connection.")
    st.stop()

# Sidebar Filters
st.sidebar.header("📅 Date Filters")

# Load initial data to get min/max dates
df_init = fetch_messages()
start_date = df_init['message_timestamp'].min().date() if not df_init.empty else date.today()
end_date = df_init['message_timestamp'].max().date() if not df_init.empty else date.today()

date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# Fetch filtered data
df_filtered = fetch_messages(date_range[0], date_range[1])

# Display Messages
st.subheader("📝 Messages DataFrame")
if not df_filtered.empty:
    st.dataframe(df_filtered[['sender_name', 'content', 'message_timestamp']])
    st.success("✅ Data loaded successfully!")
else:
    st.warning("⚠️ No messages found for the selected date range.")
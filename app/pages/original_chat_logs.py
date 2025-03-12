import streamlit as st
import pandas as pd
import psycopg2
import os
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

def fetch_all_messages():
    """Fetch all messages from PostgreSQL without date filtering."""
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
                ORDER BY m.timestamp_ms DESC;
            """  # Removed the LIMIT to get all data

            cur.execute(query)
            rows = cur.fetchall()
            colnames = [desc[0] for desc in cur.description]
            return pd.DataFrame(rows, columns=colnames)

    except Exception as e:
        st.error(f"❌ Error fetching messages: {e}")
        return pd.DataFrame()
    
    finally:
        conn.close()

# Streamlit UI
st.title("📊 Data Exploration - PostgreSQL (All-Time Data)")

# Check if database table exists
if not check_table_exists():
    st.error("❌ Database table 'messages' does not exist. Check your database connection.")
    st.stop()

# Fetch all-time messages
df_all_time = fetch_all_messages()

# Display Messages
st.subheader("📝 Messages DataFrame (All Time)")
if not df_all_time.empty:
    st.dataframe(df_all_time[['sender_name', 'content', 'message_timestamp']])
    st.success("✅ All-time data loaded successfully!")
else:
    st.warning("⚠️ No messages found in the database.")
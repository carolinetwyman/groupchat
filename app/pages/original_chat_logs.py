# import streamlit as st
# import pandas as pd
# import json
# import os
# from datetime import datetime

# # Load Data
# DATA_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'messages', 'messages_dev', 'cleaned_messages')

# def load_data():
#     """Loads all messages from JSON files in the cleaned messages directory."""
#     all_messages = []
#     if os.path.exists(DATA_PATH):
#         for filename in os.listdir(DATA_PATH):
#             if filename.endswith('.json'):
#                 with open(os.path.join(DATA_PATH, filename), 'r', encoding='utf-8') as file:
#                     data = json.load(file)
#                     if 'messages' in data:
#                         all_messages.extend(data['messages'])
#     return all_messages

# messages = load_data()
# df = pd.DataFrame(messages)

# # Convert timestamp
# if 'timestamp_ms' in df.columns:
#     df['timestamp'] = pd.to_datetime(df['timestamp_ms'] / 1000, unit='s')

# st.title("📊 Data Exploration")

# # Sidebar Filters
# st.sidebar.header("📅 Date Filters")
# start_date = df['timestamp'].min() if 'timestamp' in df.columns else None
# end_date = df['timestamp'].max() if 'timestamp' in df.columns else None
# date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# # Filter Data
# df_filtered = df[(df['timestamp'] >= pd.to_datetime(date_range[0])) & 
#                  (df['timestamp'] <= pd.to_datetime(date_range[1]))] if start_date and end_date else df

# # Display Messages
# st.subheader("📝 Messages DataFrame")
# st.dataframe(df_filtered[['sender_name', 'content', 'timestamp']])

# st.success("✅ Data loaded successfully!")
import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# Function to fetch messages from the database
def fetch_messages(start_date=None, end_date=None):
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    # Build SQL query with proper timestamp filtering
    query = """
        SELECT 
            messages.id, 
            participants.name AS sender_name, 
            messages.content, 
            to_timestamp(messages.timestamp_ms / 1000) AS message_timestamp
        FROM messages
        JOIN participants ON messages.sender_id = participants.id
        WHERE messages.content IS NOT NULL
    """
    
    params = []
    if start_date and end_date:
        query += " AND to_timestamp(messages.timestamp_ms / 1000) BETWEEN %s AND %s"
        params = [start_date, end_date]

    query += " ORDER BY messages.timestamp_ms DESC LIMIT 100;"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# Streamlit UI
st.title("📊 Data Exploration - PostgreSQL")

# Sidebar Filters
st.sidebar.header("📅 Date Filters")

# Load initial data to get min/max dates
df_init = fetch_messages()
start_date = df_init['message_timestamp'].min() if not df_init.empty else datetime.today()
end_date = df_init['message_timestamp'].max() if not df_init.empty else datetime.today()

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
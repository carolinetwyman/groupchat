
# # import streamlit as st
# # import pandas as pd
# # import psycopg2
# # import os
# # from datetime import datetime
# # from dotenv import load_dotenv

# # # Load environment variables from .env file
# # load_dotenv()

# # DB_CONFIG = {
# #     "dbname": os.getenv("DB_NAME"),
# #     "user": os.getenv("DB_USER"),
# #     "password": os.getenv("DB_PASSWORD"),
# #     "host": os.getenv("DB_HOST"),
# #     "port": os.getenv("DB_PORT")
# # }

# # def connect_db():
# #     try:
# #         conn = psycopg2.connect(**DB_CONFIG)
# #         return conn
# #     except Exception as e:
# #         st.error(f"❌ Database connection failed: {e}")
# #         return None

# # # Function to fetch messages from the database
# # def fetch_messages(start_date=None, end_date=None):
# #     conn = connect_db()
# #     if not conn:
# #         return pd.DataFrame()

# #     # Build SQL query with proper timestamp filtering
# #     query = """
# #         SELECT 
# #             messages.id, 
# #             participants.name AS sender_name, 
# #             messages.content, 
# #             to_timestamp(messages.timestamp_ms / 1000) AS message_timestamp
# #         FROM messages
# #         JOIN participants ON messages.sender_id = participants.id
# #         WHERE messages.content IS NOT NULL
# #     """
    
# #     params = []
# #     if start_date and end_date:
# #         query += " AND to_timestamp(messages.timestamp_ms / 1000) BETWEEN %s AND %s"
# #         params = [start_date, end_date]

# #     query += " ORDER BY messages.timestamp_ms DESC LIMIT 100;"

# #     df = pd.read_sql(query, conn, params=params)
# #     conn.close()
# #     return df

# # # Streamlit UI
# # st.title("📊 Data Exploration - PostgreSQL")

# # # Sidebar Filters
# # st.sidebar.header("📅 Date Filters")

# # # Load initial data to get min/max dates
# # df_init = fetch_messages()
# # start_date = df_init['message_timestamp'].min() if not df_init.empty else datetime.today()
# # end_date = df_init['message_timestamp'].max() if not df_init.empty else datetime.today()

# # date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# # # Fetch filtered data
# # df_filtered = fetch_messages(date_range[0], date_range[1])

# # # Display Messages
# # st.subheader("📝 Messages DataFrame")
# # if not df_filtered.empty:
# #     st.dataframe(df_filtered[['sender_name', 'content', 'message_timestamp']])
# #     st.success("✅ Data loaded successfully!")
# # else:
# #     st.warning("⚠️ No messages found for the selected date range.")

# import streamlit as st
# import pandas as pd
# import psycopg2
# import os
# from datetime import datetime
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Database Configuration
# DB_CONFIG = {
#     "dbname": os.getenv("DB_NAME"),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "host": os.getenv("DB_HOST"),
#     "port": os.getenv("DB_PORT")
# }

# def connect_db():
#     """Establish and return a PostgreSQL database connection."""
#     try:
#         return psycopg2.connect(**DB_CONFIG)
#     except Exception as e:
#         st.error(f"❌ Database connection failed: {e}")
#         return None

# def fetch_messages(start_date=None, end_date=None):
#     """Fetch messages from PostgreSQL with optional date filtering."""
#     conn = connect_db()
#     if not conn:
#         return pd.DataFrame()

#     try:
#         with conn.cursor() as cur:
#             query = """
#                 SELECT 
#                     m.id, 
#                     p.name AS sender_name, 
#                     m.content, 
#                     to_timestamp(m.timestamp_ms / 1000) AS message_timestamp
#                 FROM messages m
#                 JOIN participants p ON m.sender_id = p.id
#                 WHERE m.content IS NOT NULL
#             """
            
#             params = []
#             if start_date and end_date:
#                 query += " AND m.timestamp_ms BETWEEN %s AND %s"
#                 params = [int(start_date.timestamp() * 1000), int(end_date.timestamp() * 1000)]

#             query += " ORDER BY m.timestamp_ms DESC LIMIT 100;"

#             cur.execute(query, params)
#             rows = cur.fetchall()
#             colnames = [desc[0] for desc in cur.description]
#             return pd.DataFrame(rows, columns=colnames)

#     except Exception as e:
#         st.error(f"❌ Error fetching messages: {e}")
#         return pd.DataFrame()
    
#     finally:
#         conn.close()

# # Streamlit UI
# st.title("📊 Data Exploration - PostgreSQL")

# # Sidebar Filters
# st.sidebar.header("📅 Date Filters")

# # Load initial data to get min/max dates
# df_init = fetch_messages()
# start_date = df_init['message_timestamp'].min() if not df_init.empty else datetime.today()
# end_date = df_init['message_timestamp'].max() if not df_init.empty else datetime.today()

# date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# # Fetch filtered data
# df_filtered = fetch_messages(date_range[0], date_range[1])

# # Display Messages
# st.subheader("📝 Messages DataFrame")
# if not df_filtered.empty:
#     st.dataframe(df_filtered[['sender_name', 'content', 'message_timestamp']])
#     st.success("✅ Data loaded successfully!")
# else:
#     st.warning("⚠️ No messages found for the selected date range.")

import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, date
from dotenv import load_dotenv

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

# # Fetch filtered data
# df_filtered = fetch_messages(date_range[0], date_range[1])

# # Display Messages
# st.subheader("📝 Messages DataFrame")
# if not df_filtered.empty:
#     st.dataframe(df_filtered[['sender_name', 'content', 'message_timestamp']])
#     st.success("✅ Data loaded successfully!")
# else:
#     st.warning("⚠️ No messages found for the selected date range.")
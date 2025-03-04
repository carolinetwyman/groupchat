import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from collections import defaultdict
import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# 🔹 Load Environment Variables
load_dotenv()

# 🔹 Database Connection Settings
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# 🔹 Connect to PostgreSQL Database
def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# 🔹 Fetch Messages from Database
def fetch_messages(start_date=None, end_date=None):
    conn = connect_db()
    if not conn:
        return pd.DataFrame()
    
    query = """
        SELECT 
            messages.id, 
            participants.name AS sender_name, 
            messages.timestamp_ms
        FROM messages
        JOIN participants ON messages.sender_id = participants.id
    """

    params = []
    if start_date and end_date:
        query += " WHERE to_timestamp(messages.timestamp_ms / 1000) BETWEEN %s AND %s"
        params = [start_date, end_date]

    query += " ORDER BY messages.timestamp_ms DESC LIMIT 1000;"

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # Convert timestamp_ms to datetime
    df["message_timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    
    return df

# 🔹 Fetch Reactions Data
def fetch_reactions():
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT 
            reactions.message_id, 
            reactions.reaction, 
            participants.name AS actor_name
        FROM reactions
        JOIN participants ON reactions.actor_id = participants.id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 🔹 Streamlit UI Configuration
st.set_page_config(page_title="🌐 Messenger Network Graph", layout="wide")
st.title("🌐 Sick & Twisted Network Thing")

# 🔹 Sidebar Filters
st.sidebar.header("📅 Date Filters")

# ✅ Fetch Initial Data
df_init = fetch_messages()

# ✅ Ensure proper datetime conversion
if not df_init.empty:
    start_date = df_init["message_timestamp"].min().date()
    end_date = df_init["message_timestamp"].max().date()
else:
    start_date = datetime.today().date()
    end_date = datetime.today().date()

# ✅ Sidebar Date Selection
date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# ✅ Fetch filtered messages & reactions
df_filtered = fetch_messages(date_range[0], date_range[1])
df_reactions = fetch_reactions()

# 🌐 **Generate Messenger Network Graph**
st.subheader("🌐 Tangled Web")

# Create Graph
G = nx.Graph()

# Add message sender nodes
for _, row in df_filtered.iterrows():
    sender = row['sender_name']
    G.add_node(sender)

# Add reaction edges
reaction_edges = set()  # To avoid duplicate edges
for _, row in df_reactions.iterrows():
    message_id = row['message_id']
    actor = row['actor_name']
    
    # Get sender of this message
    sender_row = df_filtered[df_filtered["id"] == message_id]
    if not sender_row.empty:
        sender = sender_row.iloc[0]["sender_name"]
        
        if sender != actor:  # Avoid self-loops
            edge = tuple(sorted([sender, actor]))  # Ensure uniqueness
            if edge not in reaction_edges:
                G.add_edge(sender, actor)
                reaction_edges.add(edge)

# ✅ Save Graph
net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
net.from_nx(G)

network_html = "network_graph.html"
net.save_graph(network_html)

# ✅ Display in Streamlit
components.html(open(network_html, "r").read(), height=600)

st.success("✅ Network Graph Loaded!")
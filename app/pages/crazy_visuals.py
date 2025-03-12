import streamlit as st
import pandas as pd
import psycopg2
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 🔹 Load Environment Variables
load_dotenv()

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

# 🔹 Fetch Messages from Database
def fetch_messages(start_date=None, end_date=None):
    """ Fetch messages from PostgreSQL with optional date filtering. """
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT 
            messages.id, 
            participants.name AS sender_name, 
            messages.content, 
            to_timestamp(messages.timestamp_ms / 1000) AT TIME ZONE 'UTC' AS message_timestamp
        FROM messages
        JOIN participants ON messages.sender_id = participants.id
        WHERE messages.content IS NOT NULL
    """

    params = []
    if start_date and end_date:
        query += " AND to_timestamp(messages.timestamp_ms / 1000) AT TIME ZONE 'UTC' BETWEEN %s AND %s"
        params = [start_date, end_date]

    query += " ORDER BY messages.timestamp_ms ASC;"

    df = pd.read_sql(query, conn, params=params)
    conn.close()

    # ✅ Ensure message_timestamp is converted properly
    df["message_timestamp"] = pd.to_datetime(df["message_timestamp"], utc=True)

    return df

# 🔹 Streamlit UI Configuration
st.set_page_config(page_title="🎨 Visualizations", layout="wide")
st.title("📊 Messenger Chat Visualizations")

# 🔹 Sidebar Filters
st.sidebar.header("📅 Date Filters")

# ✅ Fetch all data first (for date selection)
df_all = fetch_messages()

# ✅ Ensure data exists before applying filtering
if not df_all.empty:
    min_date = df_all['message_timestamp'].min().date()
    max_date = df_all['message_timestamp'].max().date()
else:
    min_date, max_date = datetime.today().date(), datetime.today().date()

# ✅ Selectable date range (Set valid range)
date_range = st.sidebar.date_input("Select date range", [min_date, max_date], min_value=min_date, max_value=max_date)

# ✅ Convert selected dates to proper datetime format
start_datetime = datetime.combine(date_range[0], datetime.min.time()).replace(tzinfo=None)
end_datetime = datetime.combine(date_range[1], datetime.max.time()).replace(tzinfo=None) + timedelta(seconds=1)

# ✅ Fetch filtered messages
df_filtered = fetch_messages(start_datetime, end_datetime)

# 🔹 Messages Over Time
st.subheader("📊 Messages Over Time")
df_filtered['date'] = df_filtered['message_timestamp'].dt.date
rolling_avg = df_filtered.groupby('date').size().rolling(7, min_periods=1).mean()

fig, ax = plt.subplots()
rolling_avg.plot(kind='line', ax=ax, color='red', linewidth=3)
ax.set_title('Messages Over Time (Smoothed)')
ax.set_xlabel('Date')
ax.set_ylabel('Message Count')
st.pyplot(fig)

# 🔥 Heatmap of Message Activity
st.subheader("🔥 Heatmap of Messages Per Day/Hour")
df_filtered['hour'] = df_filtered['message_timestamp'].dt.hour
df_filtered['weekday'] = df_filtered['message_timestamp'].dt.day_name()
heatmap_data = df_filtered.pivot_table(index='weekday', columns='hour', values='content', aggfunc='count').fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap="coolwarm", linewidths=0.5, annot=True, fmt=".0f")
ax.set_title("Heatmap of Messages Per Day/Hour")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of the Week")
st.pyplot(fig)

# 🌀 Reaction Distribution
st.subheader("🌀 Reaction Distribution Per User")

def fetch_reactions():
    """Fetch reactions from the database."""
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT 
            reactions.reaction, 
            participants.name AS user
        FROM reactions
        JOIN participants ON reactions.actor_id = participants.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df

def fetch_reactions():
    """Fetch reactions from the database and fix encoding issues."""
    conn = connect_db()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT 
            reactions.reaction, 
            participants.name AS user
        FROM reactions
        JOIN participants ON reactions.actor_id = participants.id
    """

    df = pd.read_sql(query, conn)
    conn.close()

    # ✅ Fix encoding issues
    df['reaction'] = df['reaction'].astype(str).apply(lambda x: x.encode('latin1').decode('utf-8', 'ignore'))
    df['user'] = df['user'].astype(str).apply(lambda x: x.encode('latin1').decode('utf-8', 'ignore'))

    return df

df_reactions = fetch_reactions()

if not df_reactions.empty:
    fig = px.sunburst(
        df_reactions, 
        path=['reaction', 'user'], 
        title="🌀 Reaction Breakdown",
        color_discrete_sequence=px.colors.qualitative.Dark24
    )

    # ✅ Fix Unicode in Labels
    fig.update_traces(textinfo='label+percent entry')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    st.plotly_chart(fig)

# ⚡ Message Length Bubble Chart
st.subheader("⚡ Message Length vs. Time")
df_filtered['content'] = df_filtered['content'].astype(str).fillna('')
df_filtered['msg_length'] = df_filtered['content'].apply(len)
df_filtered = df_filtered[df_filtered['msg_length'] > 0]

fig = px.scatter(df_filtered, x='message_timestamp', y='msg_length', size='msg_length', color='sender_name',
                 title="⚡ Message Length Over Time", template='plotly_dark', opacity=0.7)
st.plotly_chart(fig)

# 📝 User Word Count Analysis
st.subheader("📊 User Word Count Ranking")

def fetch_word_count():
    """Fetch word count per user from the database."""
    conn = connect_db()
    if not conn:
        return {}

    query = """
        SELECT 
            participants.name AS sender_name,
            SUM(LENGTH(messages.content) - LENGTH(REPLACE(messages.content, ' ', '')) + 1) AS word_count
        FROM messages
        JOIN participants ON messages.sender_id = participants.id
        WHERE messages.content IS NOT NULL
        GROUP BY participants.name
        ORDER BY word_count DESC;
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return dict(zip(df["sender_name"], df["word_count"]))

user_word_count = fetch_word_count()

if user_word_count:
    for idx, (user, count) in enumerate(user_word_count.items(), start=1):
        st.write(f"**{idx}. {user}** — {count} words")
else:
    st.warning("⚠️ No valid messages found.")

# 📊 Chat vs. Famous Authors' Word Count
st.subheader("📚 Chat vs. Famous Authors' Word Count")
total_chat_word_count = sum(user_word_count.values())

famous_authors = {
    "William Shakespeare (Complete Works)": 884_647,
    "J.K. Rowling (Harry Potter Series)": 1_084_170,
    "Leo Tolstoy (War and Peace)": 587_287,
    "George R.R. Martin (A Song of Ice and Fire)": 1_770_000,
    "Stephen King (The Stand)": 471_485,
    "J.R.R. Tolkien (Lord of the Rings)": 481_103,
    "Fyodor Dostoevsky (The Brothers Karamazov)": 364_153,
    "Jane Austen (Complete Works)": 681_520,
    "Homer (The Iliad & The Odyssey)": 347_100,
    "Charles Dickens (A Tale of Two Cities)": 135_420
}

comparison_df = pd.DataFrame(list(famous_authors.items()), columns=['Author', 'Word Count'])
comparison_df.loc[len(comparison_df)] = ["💬 Your Chat", total_chat_word_count]
comparison_df = comparison_df.sort_values(by="Word Count", ascending=False)

st.write(f"🔢 **Total Chat Word Count:** {total_chat_word_count:,} words")
fig = px.bar(comparison_df, x="Word Count", y="Author", orientation="h",
             title="Chat Word Count vs. Famous Authors", text_auto=True,
             color="Word Count", color_continuous_scale="blues")
st.plotly_chart(fig)

st.success("✅ Visualizations loaded!")
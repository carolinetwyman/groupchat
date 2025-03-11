import streamlit as st
import pandas as pd
import numpy as np
import psycopg2
import os
import plotly.express as px
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
from textblob import TextBlob
from collections import defaultdict
from dotenv import load_dotenv

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

# 🔹 Fetch Messages from Database
def fetch_messages(start_date=None, end_date=None):
    conn = connect_db()
    if not conn:
        return pd.DataFrame()
    
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

    query += " ORDER BY messages.timestamp_ms DESC LIMIT 500;"

    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# 🔹 Streamlit UI Configuration
st.set_page_config(page_title="🎨 Groupchat Analysis", layout="wide")
st.title("📊 Groupchat Analysis")

# 🔹 Sidebar Filters
st.sidebar.header("📅 Date Filters")

# Load data to get min/max dates
df_init = fetch_messages()
start_date = df_init['message_timestamp'].min() if not df_init.empty else datetime.today()
end_date = df_init['message_timestamp'].max() if not df_init.empty else datetime.today()

date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# Fetch filtered data
df_filtered = fetch_messages(date_range[0], date_range[1])

# 🔹 Sentiment Analysis
st.subheader("📉 Sentiment Analysis Over Time")

df_filtered['sentiment'] = df_filtered['content'].astype(str).apply(lambda x: TextBlob(x).sentiment.polarity)
fig = px.line(df_filtered, x='message_timestamp', y='sentiment', title="📉 Sentiment Over Time", color='sender_name')
st.plotly_chart(fig)

# 🔹 Sentiment Analysis Per User
st.subheader("💬 User Sentiment Ranking")

# Compute sentiment for each user
user_sentiment = defaultdict(list)
for _, row in df_filtered.iterrows():
    sender = row.get("sender_name", "Unknown")
    content = str(row.get("content", ""))
    if content.strip():
        sentiment_score = TextBlob(content).sentiment.polarity
        user_sentiment[sender].append(sentiment_score)

# Compute and sort average sentiment per user
user_avg_sentiment = {user: np.mean(scores) for user, scores in user_sentiment.items() if scores}
sorted_sentiment = sorted(user_avg_sentiment.items(), key=lambda x: x[1], reverse=True)

# Display Sentiment Ranking
st.title("📊 User Sentiment Ranking")
if sorted_sentiment:
    for idx, (user, sentiment) in enumerate(sorted_sentiment, start=1):
        st.write(f"**{idx}. {user}** — Sentiment Score: {sentiment:.2f}")
else:
    st.warning("⚠️ No valid messages found for sentiment analysis.")

# 📊 **Bar Chart: Sentiment Ranking**
sentiment_df = pd.DataFrame(sorted_sentiment, columns=["User", "Average Sentiment"])
fig = px.bar(sentiment_df, x="User", y="Average Sentiment", title="Sentiment Ranking by User",
             text_auto=True, color="Average Sentiment", color_continuous_scale="RdYlGn")
st.plotly_chart(fig)

# ☁️ **Word Cloud**
st.subheader("☁️ Most Frequent Words")
all_content = ' '.join(df_filtered['content'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='plasma').generate(all_content)
st.image(wordcloud.to_array())

# Generate word cloud for positive & negative words
positive_words = ' '.join(df_filtered[df_filtered['sentiment'] > 0]['content'].dropna())
negative_words = ' '.join(df_filtered[df_filtered['sentiment'] < 0]['content'].dropna())

wordcloud_positive = WordCloud(width=800, height=400, background_color='black', colormap='Greens').generate(positive_words)
wordcloud_negative = WordCloud(width=800, height=400, background_color='black', colormap='Reds').generate(negative_words)

st.subheader("🌿 Positive Word Cloud")
st.image(wordcloud_positive.to_array())

st.subheader("🔥 Negative Word Cloud")
st.image(wordcloud_negative.to_array())

st.success("✅ Data loaded successfully!")
import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
from textblob import TextBlob
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from collections import Counter
import emoji
from collections import defaultdict

# 🔹 Set Streamlit Page Configuration
st.set_page_config(page_title="🎨 Groupchat Analysis", layout="wide")

# 🔹 Custom Styling
st.markdown(
    """
    <style>
    .stApp {
        background: url('https://source.unsplash.com/1600x900/?abstract');
        background-size: cover;
    }
    </style>
    """, unsafe_allow_html=True
)

# 🔹 Load Data from `../data/messages/messages_dev/cleaned_messages/`
DATA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'data', 'messages', 'messages_dev', 'cleaned_messages')

def load_data():
    """Loads all messages from JSON files in the cleaned messages directory."""
    all_messages = []
    if os.path.exists(DATA_PATH):
        for filename in os.listdir(DATA_PATH):
            if filename.endswith('.json'):
                with open(os.path.join(DATA_PATH, filename), 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if 'messages' in data:
                        all_messages.extend(data['messages'])
    return all_messages

messages = load_data()
df = pd.DataFrame(messages)

# 🔹 Convert timestamp
if 'timestamp_ms' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp_ms'] / 1000, unit='s')

# 🔹 Load Merged MP4 File
MERGED_VIDEO_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data/audio/merged/output.mp4")

# 🎵 **Audio Playback Feature**
st.title("🎵 Merged Audio Playback")
st.write("Listen to the newly merged MP4 file directly from this webpage!")

if os.path.exists(MERGED_VIDEO_FILE):
    st.video(MERGED_VIDEO_FILE)
    with open(MERGED_VIDEO_FILE, "rb") as file:
        st.download_button(label="⬇️ Download Merged Audio", data=file, file_name="merged_audio.mp4", mime="video/mp4")
else:
    st.error("🚨 Error: The merged MP4 file was not found! Please ensure the file exists.")
    
# 📺 **NEW FEATURE**: Video Playback
VIDEO_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "data/videos/merged/output.mp4")

st.header("🎬 Merged Video Playback")
st.write("Watch the newly merged video right here!")

if os.path.exists(VIDEO_PATH):
    st.video(VIDEO_PATH)

    # Download Button
    with open(VIDEO_PATH, "rb") as file:
        st.download_button(
            label="⬇️ Download Merged Video",
            data=file,
            file_name="merged_video.mp4",
            mime="video/mp4"
        )
else:
    st.error("🚨 Error: The merged video file was not found! Please ensure the file exists.")

# 🔹 Sidebar Filters
st.sidebar.header("📅 Date Filters")
start_date = df['timestamp'].min() if 'timestamp' in df.columns else None
end_date = df['timestamp'].max() if 'timestamp' in df.columns else None
date_range = st.sidebar.date_input("Select date range", [start_date, end_date])

# 🔹 Filter Data
df_filtered = df[(df['timestamp'] >= pd.to_datetime(date_range[0])) & (df['timestamp'] <= pd.to_datetime(date_range[1]))] if start_date and end_date else df

# 🔹 Display Messages
st.subheader("📝 Messages DataFrame")
st.dataframe(df_filtered[['sender_name', 'content', 'timestamp']])

# 📊 **Messages Over Time**
st.subheader("📊 Messages Over Time")
df_filtered['date'] = df_filtered['timestamp'].dt.date
rolling_avg = df_filtered.groupby('date').size().rolling(3).mean()

fig, ax = plt.subplots()
rolling_avg.plot(kind='line', ax=ax, color='red', linewidth=3)
ax.set_title('Messages Over Time (Smoothed)')
ax.set_xlabel('Date')
ax.set_ylabel('Message Count')
st.pyplot(fig)

# 🔥 **Heatmap of Message Activity**
st.subheader("🔥 Heatmap of Messages Per Day/Hour")
df_filtered['hour'] = df_filtered['timestamp'].dt.hour
df_filtered['weekday'] = df_filtered['timestamp'].dt.day_name()
heatmap_data = df_filtered.pivot_table(index='weekday', columns='hour', values='content', aggfunc='count').fillna(0)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap="coolwarm", linewidths=0.5, annot=True, fmt=".0f")
ax.set_title("Heatmap of Messages Per Day/Hour")
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Day of the Week")
st.pyplot(fig)

# 🌀 **Reaction Distribution**
st.subheader("🌀 Reaction Distribution Per User")

reaction_data = []
for _, row in df_filtered.iterrows():
    if isinstance(row.get('reactions'), list):
        for reaction in row['reactions']:
            emoji_char = reaction['reaction'].encode('latin1').decode('utf-8')  # Fix Unicode Encoding
            reaction_data.append({"user": reaction['actor'], "reaction": emoji_char})

df_reactions = pd.DataFrame(reaction_data)

if not df_reactions.empty:
    fig = px.sunburst(df_reactions, path=['reaction', 'user'], title="Reaction Breakdown", color_discrete_sequence=px.colors.qualitative.Dark24)
    st.plotly_chart(fig)

# ⚡ **Message Length Bubble Chart**
st.subheader("⚡ Message Length vs. Time")

df_filtered['content'] = df_filtered['content'].astype(str).fillna('')
df_filtered['msg_length'] = df_filtered['content'].apply(len)
df_filtered = df_filtered[df_filtered['msg_length'] > 0]

fig = px.scatter(df_filtered, x='timestamp', y='msg_length', size='msg_length', color='sender_name',
                 title="⚡ Message Length Over Time", template='plotly_dark', opacity=0.7)
st.plotly_chart(fig)

# ☁️ **Word Cloud**
st.subheader("☁️ Most Frequent Words")
all_content = ' '.join(df_filtered['content'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='plasma').generate(all_content)
st.image(wordcloud.to_array())

# 🔥 **Sentiment Analysis**
st.subheader("📉 Sentiment Analysis Over Time")

df_filtered['sentiment'] = df_filtered['content'].apply(lambda x: TextBlob(x).sentiment.polarity)
fig = px.line(df_filtered, x='timestamp', y='sentiment', title="📉 Sentiment Over Time", color='sender_name')
st.plotly_chart(fig)

# 🎯 **Sentiment Analysis Per User**
st.subheader("💬 User Sentiment Ranking")

# Initialize sentiment storage
user_sentiment = defaultdict(list)

# Compute sentiment for each user
for _, row in df.iterrows():
    sender = row.get("sender_name", "Unknown")
    content = str(row.get("content", ""))  # Convert to string and handle NaNs

    if content.strip():  # Ignore empty messages
        sentiment_score = TextBlob(content).sentiment.polarity
        user_sentiment[sender].append(sentiment_score)

# Compute average sentiment per user
user_avg_sentiment = {user: np.mean(scores) for user, scores in user_sentiment.items() if scores}

# Sort users by sentiment score (most positive first)
sorted_sentiment = sorted(user_avg_sentiment.items(), key=lambda x: x[1], reverse=True)

# Display Sentiment Ranking
st.title("📊 User Sentiment Ranking")

if sorted_sentiment:
    st.write("💡 **Users ranked by average message sentiment (polarity):**")

    for idx, (user, sentiment) in enumerate(sorted_sentiment, start=1):
        st.write(f"**{idx}. {user}** — Sentiment Score: {sentiment:.2f}")
else:
    st.warning("⚠️ No valid messages found. Ensure the dataset contains meaningful text.")

# 📊 **Bar Chart: Sentiment Ranking**
sentiment_df = pd.DataFrame(sorted_sentiment, columns=["User", "Average Sentiment"])
fig = px.bar(sentiment_df, x="User", y="Average Sentiment", title="Sentiment Ranking by User",
             text_auto=True, color="Average Sentiment", color_continuous_scale="RdYlGn")

st.plotly_chart(fig)

# 🌐 **Messenger Network Graph**
st.subheader("🌐 Messenger Network Graph")

G = nx.Graph()

for _, row in df_filtered.iterrows():
    sender = row['sender_name']
    if 'reactions' in row and isinstance(row['reactions'], list):
        for reaction in row['reactions']:
            receiver = reaction['actor']
            if sender != receiver:
                G.add_edge(sender, receiver)

# Save Graph
net = Network(height="600px", width="100%")
net.from_nx(G)
network_html = os.path.join(os.path.abspath(os.path.dirname(__file__)), "network_graph.html")
net.save_graph(network_html)

# Display in Streamlit
components.html(open(network_html, "r").read(), height=600)

# 🎯 Streamlit Page Configuration
st.subheader("💬 Reaction Normalization Analysis")

# 🔹 Initialize Dictionaries
reaction_counts = defaultdict(int)  # Tracks total reactions per sender
message_counts = defaultdict(int)   # Tracks total messages per sender

# 🔹 Calculate Message & Reaction Counts
for _, row in df_filtered.iterrows():
    sender_name = row.get("sender_name", "Unknown")

    if "reactions" in row and isinstance(row["reactions"], list):
        message_counts[sender_name] += 1  # Count messages with reactions
        reaction_counts[sender_name] += len(row["reactions"])  # Count reactions

# 🔹 Compute Normalized Reactions Safely
normalized_reactions = []
for sender, msg_count in message_counts.items():
    if msg_count > 0:  # Avoid division by zero
        normalized_reactions.append({
            "Sender Name": sender,
            "Normalized Reactions": reaction_counts[sender] / msg_count
        })

# 🔹 Sort results by highest normalized reactions
normalized_reactions.sort(key=lambda x: x["Normalized Reactions"], reverse=True)

# 🎯 **Display Results in Streamlit as a List**
st.title("📊 Bruce Quotient (Anthony Variant) - Reaction Normalization")

if normalized_reactions:
    st.write("💡 **Users ranked by normalized reaction count per message:**")

    for idx, item in enumerate(normalized_reactions, start=1):
        st.write(f"**{idx}. {item['Sender Name']}** — {item['Normalized Reactions']:.2f} reactions per message")

else:
    st.warning("⚠️ No valid messages with reactions found. Make sure the dataset contains reactions!")


# 🎯 **Calculate Word Count Per User**
st.subheader("📝 User Word Count Analysis")

# Initialize word count dictionary
user_word_count = defaultdict(int)

# Function to count words in a string
def count_words(text):
    return len(text.split()) if isinstance(text, str) else 0

# Count words for each user
for _, row in df.iterrows():
    sender_name = row.get("sender_name", "Unknown")
    content = row.get("content", "")
    user_word_count[sender_name] += count_words(content)

# Sort users by word count
sorted_user_word_count = sorted(user_word_count.items(), key=lambda x: x[1], reverse=True)

# Display word count ranking in Streamlit
st.title("📊 User Word Count Ranking")

if sorted_user_word_count:
    st.write("💡 **Users ranked by total words sent in messages:**")

    for idx, (user, count) in enumerate(sorted_user_word_count, start=1):
        st.write(f"**{idx}. {user}** — {count} words")
else:
    st.warning("⚠️ No valid messages found. Ensure the dataset contains messages.")
    
# 🎯 **Compare Total Word Count to Famous Authors**
st.subheader("📚 Chat vs. Famous Authors' Word Count")

# Calculate total word count of chat
total_chat_word_count = sum(user_word_count.values())

# Famous authors' word counts (approximate values)
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

# Create DataFrame for visualization
comparison_df = pd.DataFrame(list(famous_authors.items()), columns=['Author/Work', 'Word Count'])
comparison_df.loc[len(comparison_df)] = ["💬 Your Chat", total_chat_word_count]  # Append chat data

# Sort DataFrame
comparison_df = comparison_df.sort_values(by="Word Count", ascending=False)

# Display the ranking
st.write(f"🔢 **Total Chat Word Count:** {total_chat_word_count:,} words")

for idx, row in comparison_df.iterrows():
    st.write(f"**{row['Author/Work']}** — {row['Word Count']:,} words")

# 📊 **Bar Chart: Chat vs. Famous Authors**
fig = px.bar(comparison_df, x="Word Count", y="Author/Work", orientation="h",
             title="Chat Word Count vs. Famous Authors", text_auto=True,
             color="Word Count", color_continuous_scale="blues")

st.plotly_chart(fig)
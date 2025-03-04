import json
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime
from datetime import timezone
import os

output_folder = '../graphs/dev/'

# Create the directory for saving graphs if it doesn't exist
os.makedirs(f'{output_folder}', exist_ok=True)

# Load JSON data from the file (example: message_1.json)
with open('../data/messages/messages_dev/cleaned_messages/message_1.json', 'r') as file:
    data = json.load(file)

# Extract message data and participant data
messages = data["messages"]
participants = [p["name"] for p in data["participants"]]

# Process message data
messages_data = []
for message in messages:
    sender_name = message["sender_name"]
    content = message["content"]
    timestamp_ms = message["timestamp_ms"]
    timestamp = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)  # Convert from ms to seconds, with timezone
    messages_data.append({
        "sender_name": sender_name,
        "content": content,
        "timestamp": timestamp
    })

# Create a DataFrame from messages data
df = pd.DataFrame(messages_data)

# Get the current timestamp for filenames
timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')

# Example 1: Time Series Plot (Messages over time)
plt.figure(figsize=(10, 6))
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.groupby(df['timestamp'].dt.date).size().plot(kind='line')
plt.title('Messages Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Messages')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot to the specified directory
plt.savefig(f'{output_folder}messages_over_time{timestamp_str}.png')
plt.close()

# Example 2: Word Cloud (Most frequent words in messages)
all_content = ' '.join(df['content'])
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_content)

# Save the Word Cloud image
wordcloud.to_file(f'{output_folder}wordcloud{timestamp_str}.png')

# Example 3: Bar Chart (Message count by sender)
sender_counts = df['sender_name'].value_counts()
plt.figure(figsize=(10, 6))
sender_counts.plot(kind='bar', color='skyblue')
plt.title('Messages Sent by Each Participant')
plt.xlabel('Sender Name')
plt.ylabel('Message Count')
plt.xticks(rotation=90)
plt.tight_layout()

# Save the bar chart to the specified directory
plt.savefig(f'{output_folder}messages_by_sender_{timestamp_str}.png')
plt.close()

print(f"Visualizations saved to {output_folder} with timestamp {timestamp_str}")
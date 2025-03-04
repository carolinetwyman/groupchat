import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
import re
import csv

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Collect raw and cleaned content from all files
raw_content_list = []
cleaned_content_list = []

# Load each file and extract content
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            print(f"Processing file: {file_name}")
            data = json.load(file)

            # Extract raw content from each message
            for message in data.get("messages", []):
                if message.get("content"):
                    raw_content = message["content"]

                    # ✅ Discard messages that contain "to your message"
                    if re.search(r'\bto your message\b', raw_content, flags=re.IGNORECASE):
                        continue

                    raw_content_list.append(raw_content)

                    # Clean the content
                    cleaned_content = re.sub(r'https?://\S+', '', raw_content)  # Remove URLs
                    cleaned_content = re.sub(r'[^a-zA-Z\s]', '', cleaned_content)  # Remove punctuation
                    cleaned_content = re.sub(r'\bmessage\b', '', cleaned_content, flags=re.IGNORECASE)
                    cleaned_content = re.sub(r'\bcatalina wine mixer\b', '', cleaned_content, flags=re.IGNORECASE)
                    cleaned_content = re.sub(r'\breacted\b', '', cleaned_content, flags=re.IGNORECASE)

                    cleaned_content_list.append(cleaned_content)

    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# ✅ Save raw content into a CSV
if raw_content_list:
    with open('raw_message_content.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Raw Message Content'])
        for content in raw_content_list:
            writer.writerow([content])
    print("CSV file 'raw_message_content.csv' saved successfully.")

# ✅ Save cleaned content into a separate CSV
if cleaned_content_list:
    with open('cleaned_message_content.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Cleaned Message Content'])
        for content in cleaned_content_list:
            writer.writerow([content])
    print("CSV file 'cleaned_message_content.csv' saved successfully.")

# ✅ Generate word cloud if there is any cleaned content
if cleaned_content_list:
    content_text = " ".join(cleaned_content_list).strip()

    if content_text:
        wordcloud = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate(content_text)

        # Display the word cloud
        plt.figure(figsize=(100, 50))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

        # Save the word cloud as an image
        wordcloud.to_file('wordcloud.png')
        print("Word cloud saved as 'wordcloud.png'")
    else:
        print("No content available for the word cloud.")
else:
    print("No content found in the files.")
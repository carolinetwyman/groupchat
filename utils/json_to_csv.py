# utils/chat_utils.py

import json
import os
import re
import csv

def process_chat_files(file_names):
    """Processes chat JSON files, extracts and cleans message content."""
    raw_content_list = []
    cleaned_content_list = []

    for file_name in file_names:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                print(f"Processing file: {file_name}")
                data = json.load(file)

                for message in data.get("messages", []):
                    if message.get("content"):
                        raw_content = message["content"]

                        # Discard messages that contain "to your message"
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

    return raw_content_list, cleaned_content_list


def save_to_csv(filename, data, header):
    """Saves a list of data to a CSV file."""
    if data:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([header])
            for content in data:
                writer.writerow([content])
        print(f"CSV file '{filename}' saved successfully.")


def export_chat_data(file_names):
    """Main function to process chat files and save raw and cleaned content."""
    raw_content_list, cleaned_content_list = process_chat_files(file_names)

    save_to_csv('new_raw_message_content.csv', raw_content_list, 'Raw Message Content')
    save_to_csv('new_cleaned_message_content.csv', cleaned_content_list, 'Cleaned Message Content')
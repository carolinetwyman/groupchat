import json
import csv
from collections import defaultdict
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Dictionary to store total word count per user
user_word_count = defaultdict(int)

# Function to count words in a string
def count_words(text):
    return len(text.split()) if text else 0

# Load each file and calculate word count per user
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for message in data.get("messages", []):
                sender_name = message.get("sender_name", "Unknown")
                content = message.get("content", "")
                user_word_count[sender_name] += count_words(content)
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Sort the results by total word count (descending)
sorted_user_word_count = sorted(user_word_count.items(), key=lambda x: x[1], reverse=True)

# Output the results to a CSV file
output_file = 'user_word_count.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["User Name", "Total Word Count"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for user, count in sorted_user_word_count:
        writer.writerow({"User Name": user, "Total Word Count": count})

print(f"CSV file '{output_file}' has been created successfully.")
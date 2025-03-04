import json
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Initialize a list to store all messages
user_messages = []

# Function to count words in a string
def count_words(text):
    return len(text.split()) if text else 0

# Specify the user whose word count you want to find
target_user = "Joey D Bednarski"  # Replace with the desired user's name

# Load each file and extract messages for the user
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Filter messages by sender_name
            user_messages.extend(
                message for message in data.get("messages", [])
                if message.get("sender_name") == target_user
            )
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Count total words in the "content" field of each message by the user
total_word_count = sum(count_words(message.get("content", "")) for message in user_messages)

print(f"Total word count for {target_user}: {total_word_count}")
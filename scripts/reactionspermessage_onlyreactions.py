import json
import csv
from collections import defaultdict
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Dictionaries to store counts
reaction_counts = defaultdict(int)  # Total reactions per sender (only for messages with reactions)
message_counts = defaultdict(int)   # Total messages per sender (only messages with reactions)

# Load each file and count messages and reactions
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for message in data.get("messages", []):
                sender_name = message.get("sender_name", "Unknown")
                # Only count messages that have reactions
                if "reactions" in message and len(message["reactions"]) > 0:
                    message_counts[sender_name] += 1
                    reaction_counts[sender_name] += len(message["reactions"])
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Calculate normalized reactions
normalized_reactions = [
    {"Sender Name": sender, "Normalized Reactions": reaction_counts[sender] / message_counts[sender]}
    for sender in message_counts if message_counts[sender] > 0
]

# Sort the results by normalized reactions (descending)
normalized_reactions.sort(key=lambda x: x["Normalized Reactions"], reverse=True)

# Export to CSV
output_file = 'bruce_quotient_anthony_variant.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Sender Name", "Normalized Reactions"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(normalized_reactions)

print(f"CSV file '{output_file}' has been created successfully.")
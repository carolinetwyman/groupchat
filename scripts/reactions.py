import json
from collections import defaultdict
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]
# Dictionary to store reaction counts per sender
reaction_counts = defaultdict(int)

# Load each file and count reactions
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Iterate through each message
            for message in data.get("messages", []):
                # Check if the message has reactions
                if "reactions" in message:
                    # Count the number of reactions and associate them with the sender
                    reaction_counts[message.get("sender_name", "Unknown")] += len(message["reactions"])
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Find the sender with the most reactions
if reaction_counts:
    top_sender = max(reaction_counts, key=reaction_counts.get)
    print(f"The sender with the most child reactions is: {top_sender} with {reaction_counts[top_sender]} reactions.")
else:
    print("No reactions found in the files.")
import json
from collections import defaultdict
import os

# Data containers

messages_data = []
# Folder path
folder_paths = []
folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Initialize counts for specific reactions
reaction_counts = {
    "\u00f0\u009f\u0098\u00a1": 0,  # 😡 in Unicode escape sequence
    "\u00f0\u009f\u0092\u00af": 0,  # 💯 in Unicode escape sequence
    "😡": 0,  # Actual emoji character
    "💯": 0   # Actual emoji character
}

# Load each file and count the specified reactions
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for message in data.get("messages", []):
                if "reactions" in message:
                    for reaction in message["reactions"]:
                        # Count both Unicode escape sequences and emoji characters
                        reaction_value = reaction.get("reaction")
                        if reaction_value in reaction_counts:
                            reaction_counts[reaction_value] += 1
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Combine results (escape sequences + emojis)
total_angry = reaction_counts["\u00f0\u009f\u0098\u00a1"] + reaction_counts["😡"]
total_hundred = reaction_counts["\u00f0\u009f\u0092\u00af"] + reaction_counts["💯"]

# Print results
print(f"Total 😡 reactions: {total_angry}")
print(f"Total 💯 reactions: {total_hundred}")
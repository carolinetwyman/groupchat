import json
from collections import defaultdict
import csv
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Dictionary to store the count of reactions given by each actor
actor_reactions_count = defaultdict(int)

# Load each file and count reactions
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for message in data.get("messages", []):
                # If the message has reactions, count each actor's reaction
                if "reactions" in message:
                    for reaction in message["reactions"]:
                        actor_name = reaction.get("actor", "Unknown")
                        actor_reactions_count[actor_name] += 1
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Sort the results by the number of reactions given (descending)
sorted_actor_reactions = sorted(actor_reactions_count.items(), key=lambda x: x[1], reverse=True)

# Output the results to a CSV file
output_file = 'actor_reactions_count.csv'
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Actor Name", "Reactions Given"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for actor, count in sorted_actor_reactions:
        writer.writerow({"Actor Name": actor, "Reactions Given": count})

print(f"CSV file '{output_file}' has been created successfully.")
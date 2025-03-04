import json
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Initialize counter
unsent_image_count = 0

# Load each file and count occurrences
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            # Count messages with the specific condition
            unsent_image_count += sum(
                1 for message in data.get("messages", [])
                if message.get("is_unsent_image_by_messenger_kid_parent", False) == True
            )
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

print(f"Total messages with 'is_unsent_image_by_messenger_kid_parent' = true: {unsent_image_count}")
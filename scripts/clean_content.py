import json
import os
import re
from datetime import datetime

def fix_encoding(text):
    """
    Fixes misinterpreted Unicode sequences by decoding them properly.
    Example: \u00e2\u0080\u0099 → ’
    """
    if not isinstance(text, str):
        return text  # Return unchanged if it's not a string
    
    try:
        return text.encode('latin1').decode('utf-8')  # Fix double encoding issue
    except UnicodeDecodeError:
        return text

# Define folder paths
input_folder = '../data/messages/messages_dev/raw_messages/'
output_folder = '../data/messages/messages_dev/cleaned_messages/'
os.makedirs(output_folder, exist_ok=True)

# Count files
file_count = len([file for file in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, file))])
file_names = [f'{input_folder}message_{i}.json' for i in range(1, file_count + 1)]

# Process each file
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            print(f"Processing file: {file_name}")
            data = json.load(file)
            
            cleaned_messages = []

            # Clean only the content of messages
            for message in data.get("messages", []):
                if "content" in message and message["content"]:
                    raw_content = message["content"]
                    raw_content = fix_encoding(raw_content)                    
                    
                    if not re.search(r'\bto your message\b', raw_content, flags=re.IGNORECASE):
                        cleaned_content = re.sub(r'https?://\S+', '', raw_content)  # Remove URLs
                        cleaned_content = re.sub(r'\bmessage\b', '', cleaned_content, flags=re.IGNORECASE)  # Remove the word 'message'
                        # Keep original spacing, emojis, and remove special characters (excluding spaces)
                        cleaned_content = re.sub(r'[^a-zA-Z0-9\s\u0000-\uFFFF]', '', cleaned_content)
                        message["content"] = cleaned_content
                        
                        cleaned_messages.append(message)
                        
                elif not "content" in message:
                    cleaned_messages.append(message)

            data["messages"] = cleaned_messages

            # Save cleaned content as JSON with timestamp
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file_name = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_name))[0]}_{timestamp_str}.json")
            with open(output_file_name, 'w', encoding='utf-8') as output_file:
                json.dump(data, output_file, ensure_ascii=True, indent=4)
            print(f"Cleaned JSON file saved: {output_file_name}")

    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")
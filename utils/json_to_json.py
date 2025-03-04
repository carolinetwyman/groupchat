# utils/chat_utils.py

import json
import re
import os


def clean_message_content(content):
    """Cleans the message content based on specific rules."""
    # Discard messages that contain "to your message"
    if re.search(r'\bto your message\b', content, flags=re.IGNORECASE):
        return None

    # Clean the content
    cleaned_content = re.sub(r'https?://\S+', '', content)  # Remove URLs
    cleaned_content = re.sub(r'[^a-zA-Z\s]', '', cleaned_content)  # Remove punctuation
    cleaned_content = re.sub(r'\bmessage\b', '', cleaned_content, flags=re.IGNORECASE)
    cleaned_content = re.sub(r'\bcatalina wine mixer\b', '', cleaned_content, flags=re.IGNORECASE)
    cleaned_content = re.sub(r'\breacted\b', '', cleaned_content, flags=re.IGNORECASE)

    return cleaned_content.strip()


def process_chat_files_to_cleaned_json(file_names, output_folder):
    """
    Processes chat JSON files, cleans only `messages.content`, and saves the result as one consolidated JSON file.
    """
    os.makedirs(output_folder, exist_ok=True)  # ✅ Create the directory if it doesn’t exist

    combined_data = {
        "participants": [],
        "messages": [],
        "title": None,
        "is_still_participant": None,
        "thread_path": None,
        "magic_words": [],
        "image": {},
        "joinable_mode": {}
    }

    for file_name in file_names:
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                print(f"Processing file: {file_name}")
                data = json.load(file)

                # Copy non-message fields if they exist
                if "participants" in data:
                    combined_data["participants"].extend(data["participants"])
                combined_data["title"] = data.get("title", combined_data["title"])
                combined_data["is_still_participant"] = data.get("is_still_participant", combined_data["is_still_participant"])
                combined_data["thread_path"] = data.get("thread_path", combined_data["thread_path"])
                combined_data["magic_words"].extend(data.get("magic_words", []))
                combined_data["image"] = data.get("image", combined_data["image"])
                combined_data["joinable_mode"] = data.get("joinable_mode", combined_data["joinable_mode"])

                # Process messages
                for message in data.get("messages", []):
                    if "content" in message and message["content"]:
                        cleaned_content = clean_message_content(message["content"])
                        if cleaned_content is not None:
                            message["content"] = cleaned_content
                            combined_data["messages"].append(message)
                    else:
                        # Keep messages without content (like shared media or reactions)
                        combined_data["messages"].append(message)
                        
                base_name = os.path.basename(file_name)
                output_filename = os.path.join(output_folder, 'cleaned_json_to_json.json')
                save_to_json(output_filename, data)

        except FileNotFoundError:
            print(f"File not found: {file_name}")
        except json.JSONDecodeError:
            print(f"Error reading JSON in file: {file_name}")

    # Save the combined and cleaned data into one JSON file
    save_to_json(output_filename, combined_data)


def save_to_json(filename, data):
    """Saves the data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=True, indent=4)
    print(f"JSON file '{filename}' saved successfully.")


def export_chat_data(file_names, output_folder='messages/messages_dev/cleaned_messages'):
    """Main function to process chat files and save consolidated JSON."""
    process_chat_files_to_cleaned_json(file_names, output_folder)

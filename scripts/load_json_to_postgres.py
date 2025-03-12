import os
import json
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection settings
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Folder containing JSON files
INPUT_FOLDER = "/Users/carolinetwyman/Desktop/apps/puppygirlhackerpolycule_6868692056483270/data/messages/messages_dev/cleaned_messages/"

def connect_db():
    """ Establish a connection to the PostgreSQL database. """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logging.info("✅ Connected to PostgreSQL")
        return conn
    except Exception as e:
        logging.error(f"❌ Database connection failed: {e}")
        exit(1)

def load_json_files(folder):
    """ Load all JSON files in the folder. """
    if not os.path.exists(folder):
        logging.error(f"❌ Folder not found: {folder}")
        exit(1)
    files = sorted([f for f in os.listdir(folder) if f.endswith(".json")])
    return [os.path.join(folder, file) for file in files]

def process_file(file_name, cursor, participant_ids):
    """ Process a single JSON file and insert data into PostgreSQL. """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)

        message_ids = {}

        # Insert Participants
        for participant in data["participants"]:
            cursor.execute(
                "INSERT INTO participants (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id;",
                (participant["name"],)
            )
            result = cursor.fetchone()
            if result:
                participant_ids[participant["name"]] = result[0]

        # Insert Messages
        for message in data["messages"]:
            sender_id = participant_ids.get(message["sender_name"])
            cursor.execute(
                """INSERT INTO messages (sender_id, timestamp_ms, content, 
                                         is_geoblocked_for_viewer, is_unsent_image_by_messenger_kid_parent) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                (sender_id, message["timestamp_ms"], message.get("content"),
                 message.get("is_geoblocked_for_viewer", False),
                 message.get("is_unsent_image_by_messenger_kid_parent", False))
            )
            message_id = cursor.fetchone()[0]
            message_ids[message["timestamp_ms"]] = message_id

            # Insert Reactions
            if "reactions" in message:
                for reaction in message["reactions"]:
                    actor_id = participant_ids.get(reaction["actor"])
                    cursor.execute(
                        "INSERT INTO reactions (message_id, reaction, actor_id) VALUES (%s, %s, %s);",
                        (message_id, reaction["reaction"], actor_id)
                    )

            # Insert Media
            if "photos" in message:
                for photo in message["photos"]:
                    cursor.execute(
                        "INSERT INTO media (message_id, media_uri, creation_timestamp) VALUES (%s, %s, %s);",
                        (message_id, photo["uri"], photo["creation_timestamp"])
                    )

        logging.info(f"✅ Processed file: {file_name}")

    except Exception as e:
        logging.error(f"❌ Error processing {file_name}: {e}")

def main():
    """ Main function to process all JSON files and insert them into the database. """
    conn = connect_db()
    cursor = conn.cursor()

    # Load all JSON files
    file_names = load_json_files(INPUT_FOLDER)

    # Cache for participant IDs to prevent redundant lookups
    participant_ids = {}

    # Process each JSON file
    for file_name in file_names:
        process_file(file_name, cursor, participant_ids)

    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("✅ All data successfully inserted into PostgreSQL!")

if __name__ == "__main__":
    main()
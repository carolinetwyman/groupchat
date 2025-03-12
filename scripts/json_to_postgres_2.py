import os
import json
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection settings
DB_CONFIG = {
    "dbname": "messenger_data",
    "user": "carolinetwyman",
    "password": "securepassword",
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Folder containing JSON files
INPUT_FOLDER = "/Users/carolinetwyman/Desktop/apps/puppygirlhackerpolycule_6868692056483270/data/messages/messages_dev/cleaned_messages/"

def connect_db():
    """ Establish a connection to the PostgreSQL database and ensure indexing. """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create necessary indexes to speed up queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp_ms);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_reactions_message_id ON reactions (message_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_message_id ON media (message_id);")

        conn.commit()
        cursor.close()

        logging.info("✅ Connected to PostgreSQL and ensured indexing.")
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

        # Ensure required keys exist
        if "participants" not in data or "messages" not in data:
            logging.error(f"❌ Skipping {file_name} (missing required keys).")
            return

    except json.JSONDecodeError as e:
        logging.error(f"❌ Error decoding {file_name}: {e}")
        return

    message_ids = {}

    # Insert Participants and retrieve IDs
    for participant in data["participants"]:
        cursor.execute(
            """INSERT INTO participants (name) VALUES (%s) 
               ON CONFLICT (name) DO NOTHING RETURNING id;""",
            (participant["name"],)
        )
        result = cursor.fetchone()
        
        if not result:  # Fetch ID manually if the participant already exists
            cursor.execute("SELECT id FROM participants WHERE name = %s;", (participant["name"],))
            result = cursor.fetchone()

        if result:
            participant_ids[participant["name"]] = result[0]

    # Batch Data for Bulk Insert
    messages_data = []
    reactions_data = []
    media_data = []

    for message in data["messages"]:
        sender_id = participant_ids.get(message["sender_name"])
        messages_data.append((
            sender_id, message["timestamp_ms"], message.get("content"),
            message.get("is_geoblocked_for_viewer", False),
            message.get("is_unsent_image_by_messenger_kid_parent", False)
        ))

        if "reactions" in message:
            for reaction in message["reactions"]:
                actor_id = participant_ids.get(reaction["actor"])
                reactions_data.append((message["timestamp_ms"], reaction["reaction"], actor_id))

        if "photos" in message:
            for photo in message["photos"]:
                media_data.append((message["timestamp_ms"], photo["uri"], photo["creation_timestamp"]))

    # Bulk Insert Messages
    try:
        for message in messages_data:
            cursor.execute(
                """INSERT INTO messages (sender_id, timestamp_ms, content, 
                                         is_geoblocked_for_viewer, is_unsent_image_by_messenger_kid_parent) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
                message
            )
            inserted_id = cursor.fetchone()
            if inserted_id:
                message_ids[message[1]] = inserted_id[0]  # message[1] is timestamp_ms

    except psycopg2.ProgrammingError as e:
        logging.error(f"❌ No messages were inserted for {file_name}: {e}")
        message_ids = {}

    # Bulk Insert Reactions
    if reactions_data:
        cursor.executemany(
            "INSERT INTO reactions (message_id, reaction, actor_id) VALUES (%s, %s, %s);",
            [(message_ids.get(timestamp, None), reaction, actor_id) for timestamp, reaction, actor_id in reactions_data if timestamp in message_ids]
        )

    # Bulk Insert Media
    if media_data:
        cursor.executemany(
            "INSERT INTO media (message_id, media_uri, creation_timestamp) VALUES (%s, %s, %s);",
            [(message_ids.get(timestamp, None), uri, creation_timestamp) for timestamp, uri, creation_timestamp in media_data if timestamp in message_ids]
        )

    logging.info(f"✅ Processed file: {file_name}")

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
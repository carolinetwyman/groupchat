import os
import pandas as pd
import json

# Folder containing JSON files
INPUT_FOLDER = "/Users/carolinetwyman/Desktop/apps/puppygirlhackerpolycule_6868692056483270/data/messages/messages_dev/cleaned_messages/"
OUTPUT_FOLDER = "/Users/carolinetwyman/Desktop/apps/puppygirlhackerpolycule_6868692056483270/data/messages/messages_dev/csv_files/"

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_json_to_csv(input_folder, output_folder):
    """ Convert all JSON files in the input folder to CSV files in the output folder. """
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename.replace(".json", ".csv"))

            # Load JSON file
            with open(input_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Convert JSON to DataFrame
            df = pd.json_normalize(data)  # Flattens nested JSON

            # Save as CSV
            df.to_csv(output_file_path, index=False, encoding="utf-8")

            print(f"✅ {filename} converted to CSV successfully!")

if __name__ == "__main__":
    convert_json_to_csv(INPUT_FOLDER, OUTPUT_FOLDER)
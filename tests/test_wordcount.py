import unittest
import json
import os
from collections import defaultdict
from io import StringIO
import csv


# Function to count words in a string
def count_words(text):
    return len(text.split()) if text else 0


class TestWordCount(unittest.TestCase):

    def test_count_words(self):
        """Test the count_words function with different inputs."""
        self.assertEqual(count_words("Hello world"), 2)
        self.assertEqual(count_words(""), 0)
        self.assertEqual(count_words("One"), 1)
        self.assertEqual(count_words("How many words are here?"), 5)
        self.assertEqual(count_words("  Leading and trailing spaces   "), 4)

    def test_json_parsing(self):
        """Test parsing JSON and counting words per user."""
        # Mock JSON data
        mock_data = {
            "messages": [
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093859989,
                    "content": "Just present it to the class by 6 tomorrow",
                    "is_geoblocked_for_viewer": False,
                    "is_unsent_image_by_messenger_kid_parent": False,
                },
                {
                    "sender_name": "Matty Merritt",
                    "timestamp_ms": 1740093849028,
                    "content": "Oh thanks for handling that, Caroline!",
                    "is_geoblocked_for_viewer": False,
                    "is_unsent_image_by_messenger_kid_parent": False,
                },
                {
                    "sender_name": "Miles Neilson",
                    "timestamp_ms": 1740093773073,
                    "content": "i literally might know how but it\u00e2\u0080\u0099s gonna take a day",
                    "is_geoblocked_for_viewer": False,
                    "is_unsent_image_by_messenger_kid_parent": False,
                },
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093564158,
                    "content": "I thought it was going to be longer tbh",
                    "reactions": [
                        {"reaction": "\u00e2\u009d\u00a4", "actor": "Matty Merritt"}
                    ],
                    "is_geoblocked_for_viewer": False,
                    "is_unsent_image_by_messenger_kid_parent": False,
                },
                {
                    "sender_name": "Miles Neilson",
                    "timestamp_ms": 1736895510901,
                    "content": "I love how everyone is releasing their pictures with the Sidekicks minion from Bruce/aaron\u00e2\u0080\u0099s karaoke party on a different day. Really is making the minion feel alive.",
                    "reactions": [
                        {
                            "reaction": "\u00e2\u009d\u00a4",
                            "actor": "Jonah Eggleston",
                            "timestamp": 1736896826,
                        },
                        {
                            "reaction": "\u00f0\u009f\u0092\u00af",
                            "actor": "Matty Merritt",
                            "timestamp": 1736897577,
                        },
                    ],
                    "is_geoblocked_for_viewer": False,
                    "is_unsent_image_by_messenger_kid_parent": False,
                },
            ]
        }

        # Simulate word count calculation
        user_word_count = defaultdict(int)
        for message in mock_data["messages"]:
            sender_name = message.get("sender_name", "Unknown")
            content = message.get("content", "")
            user_word_count[sender_name] += count_words(content)

        # ✅ Fixed assertions within a method
        self.assertEqual(user_word_count["Jonah Eggleston"], 18)  # Correct word count (2 + 4)
        self.assertEqual(user_word_count["Matty Merritt"], 6)
        self.assertEqual(user_word_count.get("Unknown", 0), 0)

    def test_csv_output(self):
        """Test that the results are correctly written to CSV."""
        # Mock word count data
        user_word_count = {"Jonah Eggleston": 18, "Matty Merritt": 6, "Miles Neilson": 38}
        sorted_user_word_count = sorted(
            user_word_count.items(), key=lambda x: x[1], reverse=True
        )

        # Simulate CSV writing
        output_file = "test_user_word_count.csv"
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["User Name", "Total Word Count"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user, count in sorted_user_word_count:
                writer.writerow({"User Name": user, "Total Word Count": count})

        # Verify CSV content
        with open(output_file, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0]["User Name"], "Miles Neilson")
            self.assertEqual(rows[0]["Total Word Count"], "38")
            self.assertEqual(rows[1]["User Name"], "Jonah Eggleston")
            self.assertEqual(rows[1]["Total Word Count"], "18")
            self.assertEqual(rows[2]["User Name"], "Matty Merritt")
            self.assertEqual(rows[2]["Total Word Count"], "6")

        # Clean up
        os.remove(output_file)


if __name__ == "__main__":
    unittest.main()

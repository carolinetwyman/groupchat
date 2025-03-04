import unittest
from unittest.mock import mock_open, patch
import json
from utils.chat_utils import clean_message_content, process_chat_files_to_cleaned_json, save_to_json


class TestChatUtils(unittest.TestCase):

    def setUp(self):
        """Set up test data and expected output."""
        self.input_data = {
            "participants": [{"name": "Mitchell Potts"}, {"name": "Bruce Kesselring"}],
            "messages": [
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093859989,
                    "content": "Just present it to the class by 6 tomorrow",
                    "is_geoblocked_for_viewer": False
                },
                {
                    "sender_name": "Matty Merritt",
                    "timestamp_ms": 1740093849028,
                    "content": "Oh thanks for handling that, Caroline!"
                },
                {
                    "sender_name": "Miles Neilson",
                    "timestamp_ms": 1740093773073,
                    "content": "i literally might know how but it\u00e2\u0080\u0099s gonna take a day"
                },
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093564158,
                    "content": "I thought it was going to be longer tbh",
                    "reactions": [
                        {
                            "reaction": "\u00e2\u009d\u00a4",
                            "actor": "Matty Merritt"
                        }
                    ]
                }
            ],
            "title": "puppygirl hacker polycule"
        }

        self.expected_output = {
            "participants": [{"name": "Mitchell Potts"}, {"name": "Bruce Kesselring"}],
            "messages": [
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093859989,
                    "content": "Just present it to the class by 6 tomorrow",
                    "is_geoblocked_for_viewer": False
                },
                {
                    "sender_name": "Matty Merritt",
                    "timestamp_ms": 1740093849028,
                    "content": "Oh thanks for handling that, Caroline!"
                },
                {
                    "sender_name": "Miles Neilson",
                    "timestamp_ms": 1740093773073,
                    "content": "i literally might know how but it's gonna take a day"
                },
                {
                    "sender_name": "Jonah Eggleston",
                    "timestamp_ms": 1740093564158,
                    "content": "I thought it was going to be longer tbh",
                    "reactions": [
                        {
                            "reaction": "\u00e2\u009d\u00a4",
                            "actor": "Matty Merritt"
                        }
                    ]
                }
            ],
            "title": "puppygirl hacker polycule"
        }

    # ------------------------------------------------------
    # Test: clean_message_content
    # ------------------------------------------------------
    def test_clean_message_content(self):
        """Test the cleaning of message content."""
        self.assertEqual(clean_message_content("It's gonna take a day"), "Its gonna take a day")
        self.assertEqual(clean_message_content("Oh thanks for handling that, Caroline!"), "Oh thanks for handling that Caroline")
        self.assertEqual(clean_message_content(""), "")
        self.assertIsNone(clean_message_content("This is related to your message"))
        self.assertEqual(clean_message_content("https://example.com"), "")

    # ------------------------------------------------------
    # Test: process_chat_files_to_cleaned_json
    # ------------------------------------------------------
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({
        "participants": [{"name": "Mitchell Potts"}, {"name": "Bruce Kesselring"}],
        "messages": [
            {
                "sender_name": "Miles Neilson",
                "content": "i literally might know how but it\u00e2\u0080\u0099s gonna take a day"
            }
        ],
        "title": "puppygirl hacker polycule"
    }))
    @patch("utils.chat_utils.save_to_json")
    def test_process_chat_files_to_cleaned_json(self, mock_save_to_json, mock_file):
        """Test that chat files are processed and cleaned correctly."""
        process_chat_files_to_cleaned_json(["dummy.json"], "output.json")
        
        # Extract saved JSON data from the mock
        saved_data = mock_save_to_json.call_args[0][1]  # Second argument of save_to_json

        self.assertEqual(saved_data["messages"][0]["content"], "i literally might know how but it's gonna take a day")
        self.assertEqual(saved_data["title"], "puppygirl hacker polycule")

    # ------------------------------------------------------
    # Test: save_to_json (Unicode Escapes)
    # ------------------------------------------------------
    @patch("builtins.open", new_callable=mock_open)
    def test_save_to_json(self, mock_file):
        """Test that save_to_json outputs Unicode-escaped characters."""
        save_to_json("output.json", self.expected_output)

        # Verify that the JSON was written correctly
        written_data = mock_file().write.call_args[0][0]
        self.assertIn("\\u00e2\\u009d\\u00a4", written_data)  # ❤ as escaped Unicode
        self.assertIn("it's gonna take a day", written_data)

    # ------------------------------------------------------
    # Edge Case: No Messages
    # ------------------------------------------------------
    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({"messages": []}))
    @patch("utils.chat_utils.save_to_json")
    def test_no_messages(self, mock_save_to_json, mock_file):
        """Test processing files with no messages."""
        process_chat_files_to_cleaned_json(["dummy.json"], "output.json")
        saved_data = mock_save_to_json.call_args[0][1]
        self.assertEqual(len(saved_data["messages"]), 0)


if __name__ == "__main__":
    unittest.main()
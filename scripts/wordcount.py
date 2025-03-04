import json
import os

folder_path = '../data/messages/messages_dev/cleaned_messages/'
# Count files
file_count = len([file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))])
# List of filenames to read
file_names = [f'{folder_path}message_{i}.json' for i in range(1, file_count + 1)]

# Initialize a list to store all messages
all_messages = []

# Function to count words in a string
def count_words(text):
    return len(text.split()) if text else 0

# Load each file and extract messages
for file_name in file_names:
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            all_messages.extend(data.get("messages", []))
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except json.JSONDecodeError:
        print(f"Error reading JSON in file: {file_name}")

# Count total words in the "content" field of each message
total_word_count = sum(count_words(message.get("content", "")) for message in all_messages)

print(total_word_count)

# 🎯 **Calculate Word Count Per User**
st.subheader("📝 User Word Count Analysis")

# Initialize word count dictionary
user_word_count = defaultdict(int)

# Function to count words in a string
def count_words(text):
    return len(text.split()) if isinstance(text, str) else 0

# Count words for each user
for _, row in df.iterrows():
    sender_name = row.get("sender_name", "Unknown")
    content = row.get("content", "")
    user_word_count[sender_name] += count_words(content)

# Sort users by word count
sorted_user_word_count = sorted(user_word_count.items(), key=lambda x: x[1], reverse=True)

# Display word count ranking in Streamlit
st.title("📊 User Word Count Ranking")

if sorted_user_word_count:
    st.write("💡 **Users ranked by total words sent in messages:**")

    for idx, (user, count) in enumerate(sorted_user_word_count, start=1):
        st.write(f"**{idx}. {user}** — {count} words")
else:
    st.warning("⚠️ No valid messages found. Ensure the dataset contains messages.")

# 🎯 **Compare Total Word Count to Famous Authors**
st.subheader("📚 Chat vs. Famous Authors' Word Count")

# Calculate total word count of chat
total_chat_word_count = sum(user_word_count.values())

# Famous authors' word counts (approximate values)
famous_authors = {
    "William Shakespeare (Complete Works)": 884_647,
    "J.K. Rowling (Harry Potter Series)": 1_084_170,
    "Leo Tolstoy (War and Peace)": 587_287,
    "George R.R. Martin (A Song of Ice and Fire)": 1_770_000,
    "Stephen King (The Stand)": 471_485,
    "J.R.R. Tolkien (Lord of the Rings)": 481_103,
    "Fyodor Dostoevsky (The Brothers Karamazov)": 364_153,
    "Jane Austen (Complete Works)": 681_520,
    "Homer (The Iliad & The Odyssey)": 347_100,
    "Charles Dickens (A Tale of Two Cities)": 135_420
}

# Create DataFrame for visualization
comparison_df = pd.DataFrame(list(famous_authors.items()), columns=['Author/Work', 'Word Count'])
comparison_df.loc[len(comparison_df)] = ["💬 Your Chat", total_chat_word_count]  # Append chat data

# Sort DataFrame
comparison_df = comparison_df.sort_values(by="Word Count", ascending=False)

# Display the ranking
st.write(f"🔢 **Total Chat Word Count:** {total_chat_word_count:,} words")

for idx, row in comparison_df.iterrows():
    st.write(f"**{row['Author/Work']}** — {row['Word Count']:,} words")

# 📊 **Bar Chart: Chat vs. Famous Authors**
fig = px.bar(comparison_df, x="Word Count", y="Author/Work", orientation="h",
             title="Chat Word Count vs. Famous Authors", text_auto=True,
             color="Word Count", color_continuous_scale="blues")

st.plotly_chart(fig)
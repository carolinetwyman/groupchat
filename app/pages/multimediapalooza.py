import streamlit as st
import requests

# Check if the user is authenticated
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("🔒 You must sign in to view this section.")
    st.stop()

st.title("🎵 Multimedia Playback")

# S3 URLs
AUDIO_URL = "https://groupchat-deux.s3.us-east-1.amazonaws.com/audio.mp4"
VIDEO_URL = "https://groupchat-deux.s3.us-east-1.amazonaws.com/video.mp4"
COLLAGE_URL = "https://groupchat-deux.s3.us-east-1.amazonaws.com/collage.png"

# 📸 **Photo Collage Display**
st.subheader("🖼️ Chat Photo Collage")
st.image(COLLAGE_URL, caption="📷 Group Chat Collage", use_container_width=True)

# 🎵 **Audio Playback**
st.subheader("🎵 Listen to Merged Audio")
st.audio(AUDIO_URL, format="audio/mp4")

# 🔽 **Download Audio File**
audio_file = requests.get(AUDIO_URL).content
st.download_button(label="⬇️ Download Merged Audio", data=audio_file, file_name="merged_audio.mp4", mime="audio/mp4")

# 🎬 **Video Playback**
st.subheader("🎬 Watch Merged Video")
st.video(VIDEO_URL)

# 🔽 **Download Video File**
video_file = requests.get(VIDEO_URL).content
st.download_button(label="⬇️ Download Merged Video", data=video_file, file_name="merged_video.mp4", mime="video/mp4")

st.success("✅ Multimedia Loaded!")
import streamlit as st
import os

st.title("🎵 Multimedia Playback")

# Audio & Video Paths
AUDIO_PATH = os.path.join(os.path.dirname(__file__), '..','..', 'data/audio/merged/output.mp4')
VIDEO_PATH = os.path.join(os.path.dirname(__file__), '..','..', 'data/videos/merged/output.mp4')
# Path to the collage image
COLLAGE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "data", "photos", "prod", "collage.png")

# 📸 **Photo Collage Display**
st.subheader("🖼️ Chat Photo Collage")

# Check if the file exists and display it
if os.path.exists(COLLAGE_PATH):
    st.image(COLLAGE_PATH, caption="📷 Group Chat Collage", use_container_width=True)
else:
    st.warning("⚠️ No collage found. Please generate one in `../data/photos/prod/`.")

# Audio Playback
st.subheader("🎵 Listen to Merged Audio")
if os.path.exists(AUDIO_PATH):
    st.video(AUDIO_PATH)
    with open(AUDIO_PATH, "rb") as file:
        st.download_button(label="⬇️ Download Merged Audio", data=file, file_name="merged_audio.mp4", mime="video/mp4")
else:
    st.error("🚨 Merged Audio Not Found!")

# Video Playback
st.subheader("🎬 Watch Merged Video")
if os.path.exists(VIDEO_PATH):
    st.video(VIDEO_PATH)
    with open(VIDEO_PATH, "rb") as file:
        st.download_button(label="⬇️ Download Merged Video", data=file, file_name="merged_video.mp4", mime="video/mp4")
else:
    st.error("🚨 Merged Video Not Found!")

st.success("✅ Multimedia Loaded!")
import streamlit as st

st.set_page_config(page_title="Messenger Chat Analysis", layout="wide")
st.title("💬 Messenger Chat Analysis")

# Ensure user is logged in
if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please log in first.")
    st.page_link("./pages/sign_in.py", label="🫥 Go to Sign In", icon="🫥")
    st.stop()

st.subheader("Welcome to Messenger Chat Analysis!")
st.write("Select a page from the sidebar to begin exploring!")

# Navigation buttons
st.markdown("### 🔍 Explore Data")
st.page_link("./pages/original_chat_logs.py", label="📊 Original Chat Logs", icon="📊")
st.page_link("./pages/crazy_visuals.py", label="🎨 Crazy Visuals", icon="📈")
st.page_link("./pages/crazier_visual.py", label="🌐 Even Crazier Visual That Takes a Lot to Load", icon="🌍")
st.page_link("./pages/multimediapalooza.py", label="🎵 MSM Won't Show This", icon="🎵")
st.page_link("./pages/sentiment_analysis.py", label="🙃 Sentiment Analysis", icon="🙃")

st.success("🚀 Click a section to get started!")
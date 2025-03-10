import streamlit as st
import requests
import webbrowser

# Set Page Config
st.set_page_config(page_title="Messenger Chat Analysis", layout="wide")

st.title("💬 Messenger Chat Analysis")
st.subheader("Explore your Messenger conversations with insane visualizations! 🚀")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def authenticate_oauth(provider):
    auth_url = "http://127.0.0.1:5000/api/auth/google" # ✅ Redirect through Flask backend
    st.success("Redirecting to Google Sign-In...")
    webbrowser.open(auth_url)  # ✅ Open the authentication link in the browser
    st.info("Waiting for authentication... Please complete the sign-in process in your browser.")


if not st.session_state.authenticated:
    st.title("🔑 Sign In to Messenger Chat Analysis")
    
    st.markdown("### Choose a sign-in method:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign in with Google"):
            authenticate_oauth("google")

    with col2:
        if st.button("Sign in with GitHub"):
            authenticate_oauth("github")

    # ✅ Corrected Query Parameter Handling
if not st.session_state.authenticated:
    # Check if user is already authenticated in Flask
    try:
        response = requests.get("http://127.0.0.1:5000/api/auth/status")  # Check authentication status
        if response.status_code == 200:
            user_data = response.json()
            st.success(f"Signed in as {user_data.get('email', 'Unknown User')}")
            st.session_state.authenticated = True
    except requests.exceptions.ConnectionError:
        st.error("Error connecting to authentication service.")

st.write("Select a page from the sidebar to begin exploring!")


# Navigation buttons
st.markdown("### 🔍 Explore Data")
st.page_link("./pages/original_chat_logs.py", label="📊 Original Chat Logs", icon="📊")
st.page_link("./pages/crazy_visuals.py", label="🎨 Crazy Visuals", icon="📈")
st.page_link("./pages/crazier_visual.py", label="🌐 Even Crazier Visual That Takes a Lot to Load", icon="🌍")
st.page_link("./pages/multimediapalooza.py", label="🎵 MSM Won't Show This", icon="🎵")
st.page_link("./pages/sentiment_analysis.py", label="🙃 Sentiment Analysis", icon="🙃")
st.page_link("./pages/sign_in.py", label="🫥 Sign In", icon="🫥")

st.success("🚀 Click a section to get started!")
import streamlit as st
import requests

st.set_page_config(page_title="Messenger Chat Analysis", layout="wide")

st.title("💬 Messenger Chat Analysis")
st.subheader("Explore your Messenger conversations with insane visualizations! 🚀")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def authenticate_oauth(provider):
    auth_url = f"http://127.0.0.1:5000/api/auth/{provider}"
    st.success(f"{provider.capitalize()} OAuth initiated. Please complete sign-in in the new window.")
    st.experimental_set_query_params(auth_provider=provider)
    st.experimental_rerun()

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

    query_params = st.experimental_get_query_params()
    if "auth_provider" in query_params:
        provider = query_params["auth_provider"][0]
        response = requests.get(f"http://127.0.0.1:5000/api/auth/status")
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.success(f"Signed in successfully using {provider.capitalize()}!")
            st.experimental_rerun()  # Rerun the app to update the session state
        else:
            st.error("Authentication failed. Please try again.")
    
    st.stop()  # Stop rendering dashboard until login is successful

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
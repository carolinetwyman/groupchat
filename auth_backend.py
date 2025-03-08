from flask import Flask, redirect, request, session, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from flask_session import Session  # ✅ Import Flask-Session

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY")

# ✅ Configure Flask-Session to Store Sessions Properly
app.config["SESSION_TYPE"] = "filesystem"  # Store sessions in the local filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True  # Sign session cookies for security
Session(app)  # Initialize Flask-Session

# Google OAuth Config (now loaded from environment)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
GOOGLE_AUTH_URL = os.getenv("GOOGLE_AUTH_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
USER_INFO_URL = os.getenv("USER_INFO_URL")

@app.route("/api/auth/google")
def google_login():
    auth_url = (
        f"{GOOGLE_AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=openid%20email%20profile"
        f"&access_type=offline&prompt=consent"
    )
    return redirect(auth_url)

@app.route("/api/auth/status")
def auth_status():
    if "user" in session:
        return jsonify(session["user"]), 200
    return jsonify({"error": "Not authenticated"}), 401

@app.route("/api/auth/callback")
def google_callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed", 400

    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(TOKEN_URL, data=data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        error_message = token_json.get("error_description", "Unknown error")
        return f"Failed to get access token: {error_message}", 400

    user_info_response = requests.get(USER_INFO_URL, headers={"Authorization": f"Bearer {token_json['access_token']}"})
    user_info = user_info_response.json()

    session["user"] = user_info  # ✅ Store user session persistently
    return redirect("http://localhost:8502")  # ✅ Redirects user back to Streamlit

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
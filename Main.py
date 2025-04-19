import streamlit as st
from datetime import datetime
import os
import pandas as pd
from PIL import Image
import base64

# Ensure session state for login is initialized
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "music_enabled" not in st.session_state:
    st.session_state["music_enabled"] = False

# Music playback
def play_music():
    music_file = "utils/music.mp3"
    if os.path.exists(music_file):
        with open(music_file, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""
            <audio autoplay loop>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

# Load custom CSS (optional)
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("utils/style.css")

# Login Page
def login():
    st.title("💖 Welcome to Our Memory Space")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == "PerfectlyYours" and password == "Ourdump":
                st.session_state.logged_in = True
                st.success("Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")

# Upload Memory Page
def upload_page():
    st.title("📸 Upload Your Memory")
    st.session_state.music_enabled = st.toggle("🎵 Background Music", value=st.session_state.music_enabled)
    if st.session_state.music_enabled:
        play_music()

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_container_width=True)

        date_uploaded = st.date_input("Date of Capture", datetime.today())
        caption = st.text_input("Enter a caption for this memory")

        if st.button("Save Memory"):
            save_memory(uploaded_file, date_uploaded, caption)
            st.success("Memory saved successfully!")

# Save image and details
def save_memory(uploaded_file, date_uploaded, caption):
    os.makedirs("data", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    csv_path = 'data/memories.csv'

    if not os.path.exists(csv_path) or os.stat(csv_path).st_size == 0:
        df = pd.DataFrame(columns=["Image", "Date", "Caption"])
    else:
        df = pd.read_csv(csv_path)

    img_name = uploaded_file.name
    new_row = {"Image": img_name, "Date": date_uploaded, "Caption": caption}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(csv_path, index=False)

    img_path = os.path.join("images", img_name)
    with open(img_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

# Memories (Timeline Style)
def memories_page():
    st.title("🖼️ Your Memories")
    st.session_state.music_enabled = st.toggle("🎵 Background Music", value=st.session_state.music_enabled)
    if st.session_state.music_enabled:
        play_music()

    if os.path.exists('data/memories.csv'):
        try:
            df = pd.read_csv('data/memories.csv')

            if not df.empty:
                selected_date = st.date_input("Filter by Date", datetime.today())
                df = df[df["Date"] == str(selected_date)]

                if df.empty:
                    st.warning("No memories found for that date.")
                    return

                for _, row in df.iterrows():
                    img_path = os.path.join("images", row["Image"])
                    if os.path.exists(img_path):
                        st.image(img_path, caption=f"📅 {row['Date']} - {row['Caption']}", use_container_width=True)
                        st.write("---")
            else:
                st.info("No memories uploaded yet.")
        except pd.errors.EmptyDataError:
            st.info("No memories uploaded yet.")
    else:
        st.info("No memories saved yet.")

# Memories Dashboard (Grid View)
def dashboard_page():
    st.title("📊 Memories Dashboard")
    st.session_state.music_enabled = st.toggle("🎵 Background Music", value=st.session_state.music_enabled)
    if st.session_state.music_enabled:
        play_music()

    if os.path.exists("data/memories.csv"):
        df = pd.read_csv("data/memories.csv")
        if not df.empty:
            cols = st.columns(3)
            for idx, row in df.iterrows():
                img_path = os.path.join("images", row["Image"])
                if os.path.exists(img_path):
                    with cols[idx % 3]:
                        st.image(img_path, use_container_width=True)
                        st.caption(f"📅 {row['Date']}")
                        st.markdown(f"<div style='color:#6c757d;font-style:italic'>{row['Caption']}</div>", unsafe_allow_html=True)
        else:
            st.info("No memories to show yet.")
    else:
        st.info("No memories found.")

# Main App
if not st.session_state["logged_in"]:
    login()
else:
    page = st.sidebar.selectbox("Go to", ["Upload Memory", "View Memories", "Memories Dashboard", "Logout"])

    if page == "Upload Memory":
        upload_page()
    elif page == "View Memories":
        memories_page()
    elif page == "Memories Dashboard":
        dashboard_page()
    elif page == "Logout":
        st.session_state.logged_in = False
        st.rerun()

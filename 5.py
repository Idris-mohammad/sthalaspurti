import streamlit as st
import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime

# Constants
DB_FILE = "heritage_sites.db"
UPLOAD_FOLDER = "Uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DB Setup
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    category TEXT,
    location TEXT,
    image_path TEXT,
    audio_path TEXT,
    created_at TEXT
)''')
conn.commit()

# Helper to save file
def save_uploaded_file(file, folder):
    extension = file.name.split('.')[-1]
    filename = f"{folder}_{uuid.uuid4()}.{extension}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, "wb") as f:
        f.write(file.read())
    return filepath

# App Title
st.set_page_config("Sthalaspurti - స్థలస్పూర్తి", page_icon="🛕")
st.title("📍 Sthalaspurti - స్థలస్పూర్తి")
st.subheader("Preserve, Present, Participate")

# Form
st.markdown("### 📝 Contribute a Heritage Site")
with st.form("upload_form"):
    name = st.text_input("📛 Site Name")
    description = st.text_area("🧾 Description")
    category = st.selectbox("🏷️ Category", ["Temple", "Fort", "Palace", "Monument", "Other"])
    location = st.text_input("📍 Location")
    image = st.file_uploader("📸 Upload an Image", type=["png", "jpg", "jpeg"])
    audio = st.file_uploader("🎙️ Upload an Audio Description (Optional)", type=["mp3", "wav", "webm"])
    submitted = st.form_submit_button("Submit")

    if submitted:
        if not all([name, description, category, location, image]):
            st.error("Please fill all required fields and upload an image.")
        else:
            image_path = save_uploaded_file(image, "image")
            audio_path = save_uploaded_file(audio, "audio") if audio else None
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            c.execute("INSERT INTO sites (name, description, category, location, image_path, audio_path, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (name, description, category, location, image_path, audio_path, created_at))
            conn.commit()
            st.success("✅ Submission Successful!")

# Gallery
st.markdown("---")
st.markdown("## 🖼️ Heritage Submissions Gallery")
sites = pd.read_sql_query("SELECT * FROM sites ORDER BY created_at DESC", conn)

for _, row in sites.iterrows():
    with st.container():
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(row["image_path"], width=200)
            if row["audio_path"]:
                st.audio(row["audio_path"])
        with cols[1]:
            st.markdown(f"### {row['name']}")
            st.markdown(f"**Category:** {row['category']}  \n**Location:** {row['location']}")
            st.markdown(f"{row['description']}")
            st.markdown(f"*Submitted on:* {row['created_at']}")


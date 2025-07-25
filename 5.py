import streamlit as st
from PIL import Image
import pandas as pd
import os
from streamlit_js_eval import streamlit_js_eval

# Set page config
st.set_page_config(page_title="Sthalaspurti", layout="wide")

# Define tabs
tabs = ["Home", "Upload"]
selection = st.sidebar.radio("Go to", tabs)

if selection == "Upload":
    st.title("📤 Upload a Heritage Place")
    st.write("Share information about a cultural or heritage place.")

    with st.form("Upload Form", clear_on_submit=False):
        name = st.text_input("Place Name")
        description = st.text_area("Description")
        language = st.selectbox("Language", ["English", "Telugu", "Hindi", "Other"])
        image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        audio = st.file_uploader("Upload audio", type=["mp3", "wav"])
        video = st.file_uploader("Upload video", type=["mp4", "mov"])
        document = st.file_uploader("Upload document (optional)", type=["pdf", "docx"])

        # Location Fields (Auto-detect with button)
        st.markdown("#### 📍 Location")
        lat = st.text_input("Latitude", value="", key="lat", disabled=True)
        lng = st.text_input("Longitude", value="", key="lng", disabled=True)

        # Get location using streamlit-js-eval
        location = streamlit_js_eval(
            js_expressions="navigator.geolocation.getCurrentPosition((pos) => ({lat: pos.coords.latitude, lng: pos.coords.longitude}))",
            key="get_user_location", want_output=True
        )

        if st.button("📍 Get Location"):
            if location and isinstance(location, dict):
                st.session_state.lat = f"{location['lat']:.6f}"
                st.session_state.lng = f"{location['lng']:.6f}"
                st.success("✅ Location captured!")
            else:
                st.warning("⚠️ Please allow location access in your browser.")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if name and description:
                data = {
                    "Name": name,
                    "Description": description,
                    "Language": language,
                    "Latitude": st.session_state.get("lat", ""),
                    "Longitude": st.session_state.get("lng", "")
                }

                # Create data directory if not exists
                os.makedirs("heritage_data", exist_ok=True)

                # Save as CSV
                df = pd.DataFrame([data])
                df.to_csv("heritage_data/places.csv", mode="a", header=not os.path.exists("heritage_data/places.csv"), index=False)

                # Save uploaded files
                if image:
                    with open(f"heritage_data/{name}_image.png", "wb") as f:
                        f.write(image.read())
                if audio:
                    with open(f"heritage_data/{name}_audio.mp3", "wb") as f:
                        f.write(audio.read())
                if video:
                    with open(f"heritage_data/{name}_video.mp4", "wb") as f:
                        f.write(video.read())
                if document:
                    with open(f"heritage_data/{name}_doc.pdf", "wb") as f:
                        f.write(document.read())

                st.success("✅ Heritage place uploaded successfully!")
            else:
                st.error("❌ Please fill in the name and description fields.")

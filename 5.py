import streamlit as st
import sqlite3
import os
import uuid
from datetime import datetime
from PIL import Image
from streamlit_js_eval import streamlit_js_eval
import io
import base64
import pandas as pd

# Configuration
UPLOAD_FOLDER = 'Uploads'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webm'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database setup
# Initialize database
def init_db():
    conn = sqlite3.connect('heritage.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS heritage_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            category TEXT,
            image_path TEXT,
            audio_path TEXT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()


# Check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Save uploaded file
def save_file(file, prefix):
    try:
        if file.size > MAX_FILE_SIZE:
            return None, "File size exceeds 5MB limit"
        ext = file.name.rsplit('.', 1)[1].lower() if '.' in file.name else ''
        if not allowed_file(file.name):
            return None, "Invalid file type. Use PNG, JPG, JPEG, GIF, or WebM"
        filename = f"{prefix}_{uuid.uuid4()}.{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(file.read())
        return filename, None
    except Exception as e:
        return None, f"Error saving file: {e}"

# Streamlit app
st.set_page_config(page_title="Sthalaspurti - స్థలస్పూర్తి", layout="wide")
st.title("Sthalaspurti - స్థలస్పూర్తి")
st.subheader("Preserving Heritage, One Story at a Time")

# Tabs
tabs = st.tabs(["📸 Upload", "🗺️ Map", "🏛️ Gallery"])

# Upload Tab
with tabs[0]:
    st.header("Upload Heritage Site")
    st.subheader("Get Your Location")
    if st.button("📍 Get Location"):
        location = streamlit_js_eval(
            js_expressions="navigator.geolocation.getCurrentPosition",
            key="get_location_btn"
        )
    
        if location and "coords" in location:
            lat = location["coords"]["latitude"]
            lng = location["coords"]["longitude"]
    
            st.session_state["latitude"] = f"{lat:.5f}"
            st.session_state["longitude"] = f"{lng:.5f}"
            st.success(f"Location fetched: {lat:.5f}, {lng:.5f}")
        else:
            st.warning("Could not fetch location. Please allow browser location access.")



    with st.form("heritage_form"):
        title = st.text_input("Heritage Site Title / వారసత్వ ప్రదేశం పేరు", max_chars=100)
        photo = st.file_uploader("Photo / ఫోటో", type=['png', 'jpg', 'jpeg', 'gif'])
        
        # Image preview
        if photo:
            try:
                img = Image.open(photo)
                st.image(img, caption="Image Preview", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image preview: {e}")
        
        # Audio recording (embedded HTML/JavaScript)
        st.markdown("### Audio Description / ఆడియో వివరణ")
        audio_html = """
        <button id="recordBtn" class="btn">🎙️ Record</button>
        <button id="stopBtn" class="btn" style="display: none;">🛑 Stop</button>
        <audio id="audioPlayback" controls style="display: none; margin-top: 10px;"></audio>
        <input type="hidden" id="audioBlob" name="audioBlob">
        <style>
            .btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white; border: none; padding: 10px 20px;
                border-radius: 10px; cursor: pointer; margin-right: 10px;
            }
            .btn:hover { transform: translateY(-2px); }
        </style>
        <script>
            let mediaRecorder, audioChunks = [];
            document.getElementById('recordBtn').addEventListener('click', async () => {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const audioUrl = URL.createObjectURL(audioBlob);
                        document.getElementById('audioPlayback').src = audioUrl;
                        document.getElementById('audioPlayback').style.display = 'block';
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = () => {
                            document.getElementById('audioBlob').value = reader.result;
                        };
                    };
                    mediaRecorder.start();
                    document.getElementById('recordBtn').style.display = 'none';
                    document.getElementById('stopBtn').style.display = 'inline-block';
                } catch (err) {
                    alert('Failed to access microphone. Please allow microphone access.');
                }
            });
            document.getElementById('stopBtn').addEventListener('click', () => {
                mediaRecorder.stop();
                document.getElementById('recordBtn').style.display = 'inline-block';
                document.getElementById('stopBtn').style.display = 'none';
            });
        </script>
        """
        st.components.v1.html(audio_html, height=150)
        
        description = st.text_area("Description / వివరణ", max_chars=1000, placeholder="ఈ ప్రదేశం గురించి కథ, చరిత్ర లేదా ప్రాముఖ్యత...")
        category = st.selectbox("Category / వర్గం", [
            "Temple / దేవాలయం", "Monument / స్మారక చిహ్నం", "Sacred Tree / పవిత్ర చెట్టు",
            "Well / బావి", "Statue / విగ్రహం", "Market / మార్కెట్", "Other / ఇతర"
        ])
        category = category.split(' / ')[0].lower()
        
        # Show latitude and longitude input fields (with prefilled values if available)
        latitude = st.text_input("Latitude", value=st.session_state.get("latitude", ""))
        longitude = st.text_input("Longitude", value=st.session_state.get("longitude", ""))

        
        # Geolocation button
        geolocation_html = """
        <button id="getLocationBtn" class="btn">📍 Get Location</button>
        <style>
            .btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white; border: none; padding: 10px 20px;
                border-radius: 10px; cursor: pointer;
            }
            .btn:hover { transform: translateY(-2px); }
        </style>
        <script>
            document.getElementById('getLocationBtn').addEventListener('click', () => {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        position => {
                            window.parent.postMessage({
                                type: 'geolocation',
                                lat: position.coords.latitude,
                                lng: position.coords.longitude
                            }, '*');
                        },
                        error => {
                            alert('Unable to get location. Please try again.');
                        }
                    );
                } else {
                    alert('Geolocation is not supported by this browser.');
                }
            });
        </script>
        """
        st.components.v1.html(geolocation_html, height=60)
        
        # Handle geolocation data
        if 'geolocation' not in st.session_state:
            st.session_state.geolocation = {'lat': None, 'lng': None}
        
        def handle_geolocation():
            if st.session_state.get('geolocation_data'):
                data = st.session_state.geolocation_data
                st.session_state.geolocation['lat'] = data['lat']
                st.session_state.geolocation['lng'] = data['lng']
                st.session_state.lat = f"{data['lat']:.4f}"
                st.session_state.lng = f"{data['lng']:.4f}"
        
        st.components.v1.html("""
        <script>
            window.addEventListener('message', (event) => {
                if (event.data.type === 'geolocation') {
                    window.parent.Streamlit.setComponentValue({
                        lat: event.data.lat,
                        lng: event.data.lng
                    });
                }
            });
        </script>
        """, height=0)
        
        submitted = st.form_submit_button("✨ Share Heritage")
        if submitted:
            if not title or len(title) > 100:
                st.error("Title must be between 1 and 100 characters")
            elif not description or len(description) > 1000:
                st.error("Description must be between 1 and 1000 characters")
            elif not photo:
                st.error("Please upload an image")
            elif not st.session_state.geolocation['lat'] or not st.session_state.geolocation['lng']:
                st.error("Please get location")
            else:
                try:
                    # Save image
                    image_filename, image_error = save_file(photo, 'image')
                    if image_error:
                        st.error(image_error)
                        st.stop()
                    
                    # Save audio
                    audio_filename = None
                    audio_data = st.session_state.get('audioBlob', '')
                    if audio_data and audio_data.startswith('data:audio/webm;base64,'):
                        audio_data = audio_data.replace('data:audio/webm;base64,', '')
                        audio_bytes = base64.b64decode(audio_data)
                        audio_filename = f"audio_{uuid.uuid4()}.webm"
                        with open(os.path.join(UPLOAD_FOLDER, audio_filename), 'wb') as f:
                            f.write(audio_bytes)
                    
                    # Save to database
                    conn = sqlite3.connect('heritage.db')
                    c = conn.cursor()
                    c.execute('INSERT INTO sites (title, description, category, lat, lng, image, audio) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (title, description, category, st.session_state.geolocation['lat'],
                              st.session_state.geolocation['lng'], image_filename, audio_filename))
                    conn.commit()
                    conn.close()
                    st.success("Heritage site uploaded successfully!")
                    st.session_state.geolocation = {'lat': None, 'lng': None}
                    st.session_state.lat = ''
                    st.session_state.lng = ''
                    st.session_state.audioBlob = ''
                except sqlite3.Error as e:
                    st.error(f"Database error: {e}")
                except Exception as e:
                    st.error(f"Error: {e}")

# Map Tab
with tabs[1]:
    st.header("Heritage Map / వారసత్వ మ్యాప్")
    map_html = """
    <div id="map" style="height: 500px; border-radius: 15px;"></div>
    <button id="toggleMapBtn" class="btn">Toggle 2D/3D View</button>
    <div id="cesiumContainer" style="height: 500px; border-radius: 15px; display: none;"></div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css"/>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script src="https://cesium.com/downloads/cesiumjs/releases/1.110/Build/Cesium/Cesium.js"></script>
    <link rel="stylesheet" href="https://cesium.com/downloads/cesiumjs/releases/1.110/Build/Cesium/Widgets/widgets.css"/>
    <style>
        .btn {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white; border: none; padding: 10px 20px;
            border-radius: 10px; cursor: pointer; margin-bottom: 10px;
        }
        .btn:hover { transform: translateY(-2px); }
    </style>
    <script>
        let map, cesiumViewer, is3DView = false;
        function initMap() {
            map = L.map('map').setView([17.3850, 78.4867], 10);
            const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            });
            const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: '© <a href="https://www.esri.com/">Esri</a>'
            });
            const baseLayers = {
                'Standard Map': osmLayer,
                'Satellite Map': satelliteLayer
            };
            osmLayer.addTo(map);
            L.control.layers(baseLayers).addTo(map);
            
            fetch('/sites')
            .then(response => response.json())
            .then(sites => {
                sites.forEach(site => {
                    if (site.lat && site.lng) {
                        L.marker([site.lat, site.lng])
                        .bindPopup(`
                            <div style="max-width: 200px;">
                                <img src="/Uploads/${site.image}" style="width: 100%; height: 80px; object-fit: cover;">
                                <h4>${site.title}</h4>
                                <p>${site.description.substring(0, 50)}...</p>
                                ${site.audio ? `<audio controls src="/Uploads/${site.audio}"></audio>` : ''}
                            </div>
                        `)
                        .addTo(map);
                    }
                });
            })
            .catch(error => console.error('Error loading sites:', error));
        }
        
        function initCesium() {
            Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIzN2Y0M2VhMS1iMDc3LTQ0YzAtYjVhNS1iYTNiNzVhY2UzM2UiLCJpZCI6MjQ3MjE4LCJpYXQiOjE3MzAzOTY4MTN9.4f4F8tD3D6-5z3o8K0jV5pN6rW9qX2yZ1gH8kL7mN0Q'; // Replace with your Cesium Ion token
            cesiumViewer = new Cesium.Viewer('cesiumContainer', {
                terrainProvider: Cesium.createWorldTerrain(),
                imageryProvider: Cesium.createWorldImagery(),
                baseLayerPicker: true
            });
            
            fetch('/sites')
            .then(response => response.json())
            .then(sites => {
                sites.forEach(site => {
                    if (site.lat && site.lng) {
                        cesiumViewer.entities.add({
                            position: Cesium.Cartesian3.fromDegrees(site.lng, site.lat, 100),
                            billboard: {
                                image: '/Uploads/' + site.image,
                                width: 64,
                                height: 64
                            },
                            label: {
                                text: site.title,
                                font: '14pt Arial',
                                fillColor: Cesium.Color.WHITE,
                                outlineColor: Cesium.Color.BLACK,
                                style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                                verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
                                pixelOffset: new Cesium.Cartesian2(0, -70)
                            },
                            description: `
                                <div style="max-width: 200px;">
                                    <img src="/Uploads/${site.image}" style="width: 100%; height: 80px; object-fit: cover;">
                                    <h4>${site.title}</h4>
                                    <p>${site.description.substring(0, 50)}...</p>
                                    ${site.audio ? `<audio controls src="/Uploads/${site.audio}"></audio>` : ''}
                                </div>
                            `
                        });
                    }
                });
            });
        }
        
        function toggleMapView() {
            is3DView = !is3DView;
            document.getElementById('map').style.display = is3DView ? 'none' : 'block';
            document.getElementById('cesiumContainer').style.display = is3DView ? 'block' : 'none';
            if (is3DView && !cesiumViewer) initCesium();
            else if (!is3DView && !map) initMap();
        }
        
        document.addEventListener('DOMContentLoaded', () => {
            initMap();
            document.getElementById('toggleMapBtn').addEventListener('click', toggleMapView);
        });
    </script>
    """
    st.components.v1.html(map_html, height=600)

# Gallery Tab
with tabs[2]:
    st.header("Heritage Gallery / వారసత్వ గ్యాలరీ")
    search = st.text_input("Search by title or category...")
    
    try:
        conn = sqlite3.connect('heritage.db')
        sites = pd.read_sql_query('SELECT * FROM sites ORDER BY created_at DESC', conn)
        conn.close()
        
        if search:
            sites = sites[sites['title'].str.lower().str.contains(search.lower()) |
                          sites['category'].str.lower().str.contains(search.lower())]
        
        items_per_page = 6
        total_pages = max(1, (len(sites) + items_per_page - 1) // items_per_page)
        page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        start = (page - 1) * items_per_page
        end = start + items_per_page
        paginated_sites = sites[start:end]
        
        for _, site in paginated_sites.iterrows():
            st.markdown(f"### {site['title']}")
            col1, col2 = st.columns([1, 2])
            with col1:
                try:
                    st.image(os.path.join(UPLOAD_FOLDER, site['image']), use_column_width=True)
                except:
                    st.error("Image not found")
            with col2:
                st.write(f"**Description**: {site['description']}")
                st.write(f"**Category**: {site['category']}")
                st.write(f"**Date**: {pd.to_datetime(site['created_at']).strftime('%Y-%m-%d')}")
                if site['audio']:
                    try:
                        st.audio(os.path.join(UPLOAD_FOLDER, site['audio']))
                    except:
                        st.error("Audio not found")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

# Serve uploaded files
@st.cache_data
def get_file(filename):
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'rb') as f:
            return f.read()
    except FileNotFoundError:
        return None

# Expose /Uploads endpoint for map popups

    from flask import Flask, send_from_directory
    flask_app = Flask(__name__)
    
    @flask_app.route('/Uploads/<filename>')
    def uploaded_file(filename):
        try:
            return send_from_directory(UPLOAD_FOLDER, filename)
        except FileNotFoundError:
            return {"success": False, "message": "File not found"}, 404
    
    if __name__ == '__main__':
        flask_app.run(port=5001)

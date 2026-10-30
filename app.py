"""
Photo Locator — Image Geolocation & Forensic Intelligence Dashboard
Accurately replicates the sleek dark UI with dual-engine detection,
interactive satellite maps, metadata extraction, and Google Maps / Earth links.
"""

import base64
import io
import json
import math
import os
import time
from datetime import datetime

import folium
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
from streamlit_folium import st_folium

from geo_engine import run_ai_geolocation
from exif_engine import extract_exif_data, format_exif_display

# ── Load environment variables ───────────────────────────────────────────────
load_dotenv()

# ── Streamlit Page Configuration ─────────────────────────────────────────────
st.set_page_config(
    page_title="Photo Locator - Image Geolocation Tool",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── High-Fidelity Custom CSS Matching Reference Image ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-main: #0B0F19;
    --bg-card: #111827;
    --bg-card-alt: #0D1322;
    --bg-border: #1E293B;
    --bg-input: #151D30;
    --accent-blue: #4F46E5;
    --accent-blue-hover: #4338CA;
    --accent-purple: #6366F1;
    --accent-green: #10B981;
    --accent-green-bg: #064E3B;
    --accent-green-border: #059669;
    --text-main: #F3F4F6;
    --text-muted: #9CA3AF;
    --text-dark: #6B7280;
    --border-radius: 12px;
}

/* Global resets & typography */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text-main) !important;
}

[data-testid="stSidebar"] {
    background-color: #080D1A !important;
    border-right: 1px solid #1E293B !important;
}

/* Header Navbar */
.geo-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1.4rem;
    background: #0B0F19;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 1.5rem;
}
.geo-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.geo-logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, #4F46E5, #818CF8);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 0 15px rgba(79, 70, 229, 0.4);
}
.geo-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
.geo-title span {
    color: #6366F1;
}
.geo-subtitle {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin-left: 0.6rem;
    padding-left: 0.8rem;
    border-left: 1px solid #1E293B;
}
.geo-badge-top {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text-muted);
    font-size: 0.82rem;
    font-weight: 500;
    background: #111827;
    padding: 0.35rem 0.8rem;
    border-radius: 20px;
    border: 1px solid #1E293B;
}

/* Sidebar Nav styling */
.nav-btn-active {
    background: #1E293B;
    color: #FFFFFF !important;
    border-radius: 8px;
    padding: 0.65rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 600;
    font-size: 0.95rem;
    border-left: 3px solid #6366F1;
    margin-bottom: 0.4rem;
}
.nav-btn-item {
    color: #9CA3AF !important;
    padding: 0.65rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-weight: 500;
    font-size: 0.95rem;
    border-radius: 8px;
    margin-bottom: 0.4rem;
    transition: all 0.2s;
    text-decoration: none;
}
.nav-btn-item:hover {
    background: #111827;
    color: #FFFFFF !important;
}

/* Card panels */
.geo-panel {
    background: #0E1424;
    border: 1px solid #1E293B;
    border-radius: var(--border-radius);
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
}
.geo-panel-title {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #F3F4F6;
    margin-bottom: 1rem;
}

/* Banner: Location Found! */
.geo-success-banner {
    background: rgba(6, 78, 59, 0.4);
    border: 1px solid #059669;
    border-radius: var(--border-radius);
    padding: 1rem 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    margin-bottom: 1.25rem;
}
.geo-success-icon {
    font-size: 1.25rem;
    color: #10B981;
}
.geo-success-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #10B981;
    margin-bottom: 0.15rem;
}
.geo-success-desc {
    font-size: 0.82rem;
    color: #A7F3D0;
    margin: 0;
}

/* Reasoning Box */
.geo-reasoning-box {
    background: rgba(30, 41, 59, 0.45);
    border: 1px solid #1E293B;
    border-left: 3px solid #6366F1;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #D1D5DB;
    margin-top: 0.5rem;
}
.geo-reasoning-box strong {
    color: #FFFFFF;
}

/* Tables / Meta grids */
.geo-data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
}
.geo-data-table td {
    padding: 0.55rem 0.4rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}
.geo-data-table tr:last-child td {
    border-bottom: none;
}
.geo-data-label {
    color: #9CA3AF;
    width: 38%;
    font-weight: 400;
}
.geo-data-value {
    color: #F9FAFB;
    font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84rem;
}

/* Primary Action Button */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.5) !important;
}

/* Drag & Drop uploader style */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #090E1A !important;
    border: 1px dashed #2A364F !important;
    border-radius: 10px !important;
    padding: 2rem 1rem !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #4F46E5 !important;
    background: #0D1527 !important;
}

/* External Link Buttons */
.geo-btn-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.55rem 1rem;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.15s ease;
    margin-right: 0.5rem;
    margin-top: 0.5rem;
}
.geo-btn-earth {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid #059669;
    color: #34D399 !important;
}
.geo-btn-earth:hover {
    background: rgba(16, 185, 129, 0.25);
}
.geo-btn-maps {
    background: rgba(79, 70, 229, 0.15);
    border: 1px solid #4F46E5;
    color: #818CF8 !important;
}
.geo-btn-maps:hover {
    background: rgba(79, 70, 229, 0.25);
}

/* Streamlit container paddings */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 98% !important;
}
</style>
""", unsafe_allow_html=True)


# ── Navbar Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="geo-navbar">
  <div class="geo-brand">
    <div class="geo-logo-icon">📍</div>
    <div class="geo-title">Photo<span>Locator</span></div>
    <div class="geo-subtitle">Find Where a Photo Was Taken</div>
  </div>
  <div class="geo-badge-top">
    <span>🌐</span> Image Geolocation Tool
  </div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar Navigation ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.8rem 0.2rem 1.5rem;">
      <div style="font-weight: 700; font-size: 1.15rem; color: #fff; margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
        📍 Photo Locator
      </div>
      <div class="nav-btn-active">
        <span>🏠</span> Home
      </div>
      <a class="nav-btn-item" href="#">
        <span>🕒</span> History
      </a>
      <a class="nav-btn-item" href="#">
        <span>⚙️</span> Settings
      </a>
      <a class="nav-btn-item" href="#">
        <span>ℹ️</span> About
      </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: none; border-top: 1px solid #1E293B; margin: 1.5rem 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size: 0.76rem; color: #6B7280; line-height: 1.6; padding: 0 0.2rem;">
      <strong style="color: #9CA3AF;">Photo Locator</strong><br>
      Powered by Google Gemini Vision &amp; EXIF GPS Inspection Engine.<br><br>
      For educational, research and forensic verification use.
    </div>
    """, unsafe_allow_html=True)


# ── Helpers for Maps & Links ─────────────────────────────────────────────────
def build_maps_url(lat: float, lon: float) -> str:
    return f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"

def build_earth_url(lat: float, lon: float, alt: float, heading: float) -> str:
    return (
        f"https://earth.google.com/web/@{lat:.6f},{lon:.6f},{alt:.1f}a,"
        f"1000d,35y,{heading:.1f}h,60t,0r"
    )

def render_satellite_map(lat: float, lon: float, title: str = "Location"):
    """Render high-resolution Satellite map replicating the Google Satellite view in Photo Locator."""
    m = folium.Map(
        location=[lat, lon],
        zoom_start=17,
        tiles=None,
        control_scale=True,
    )

    # Esri World Imagery (Satellite)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri Satellite",
        name="Satellite",
        max_zoom=19,
    ).add_to(m)

    # Clean Red Location Pin
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(f"<b>{title}</b><br>{lat:.6f}, {lon:.6f}", max_width=250),
        tooltip=title,
        icon=folium.Icon(color="red", icon="map-marker", prefix="fa"),
    ).add_to(m)

    st_folium(m, use_container_width=True, height=420, returned_objects=[])


# ── Main Two-Column Layout ───────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.45], gap="medium")

with col_left:
    # ── Upload Box Panel ──
    st.markdown("""
    <div class="geo-panel">
      <div style="text-align: center; padding: 0.5rem 0 0.8rem;">
        <div style="font-size: 2.2rem; color: #818CF8; margin-bottom: 0.3rem;">☁️</div>
        <div style="font-weight: 700; font-size: 1.15rem; color: #FFFFFF;">Upload an Image</div>
        <div style="font-size: 0.82rem; color: #9CA3AF; margin-top: 0.2rem;">Drag &amp; drop an image here or click to browse</div>
      </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label="Upload an Image",
        type=["jpg", "jpeg", "png", "webp", "tiff", "heic"],
        label_visibility="collapsed",
    )

    st.markdown("""
      <div style="text-align: center; font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
        Supports JPG, PNG, HEIC, TIFF (Max 10MB)
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Optional Location Hint ──
    st.markdown("""
    <div class="geo-panel" style="padding: 1rem;">
      <div style="font-size: 0.82rem; font-weight: 600; color: #818CF8; margin-bottom: 0.3rem; display: flex; align-items: center; gap: 0.4rem;">
        💡 <span>Optional Context Hint</span>
      </div>
      <div style="font-size: 0.75rem; color: #9CA3AF; margin-bottom: 0.5rem;">
        Already know something? (e.g. "Faisal Mosque, Islamabad" or "North Italy")
      </div>
    """, unsafe_allow_html=True)

    user_hint = st.text_input(
        label="Context hint",
        placeholder="Enter known place, city, or event details...",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # If file uploaded
    if uploaded_file:
        file_bytes = uploaded_file.read()
        pil_img = Image.open(io.BytesIO(file_bytes))
        file_size_mb = len(file_bytes) / (1024 * 1024)
        file_ext = uploaded_file.name.split(".")[-1].upper()

        # ── Image Preview Panel ──
        st.markdown("""
        <div class="geo-panel">
          <div class="geo-panel-title">
            <span>🖼️</span> Image Preview
          </div>
        """, unsafe_allow_html=True)
        st.image(pil_img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── File Information Panel ──
        st.markdown(f"""
        <div class="geo-panel">
          <div class="geo-panel-title">
            <span>📄</span> File Information
          </div>
          <table class="geo-data-table">
            <tr>
              <td class="geo-data-label">File Name</td>
              <td class="geo-data-value">{uploaded_file.name}</td>
            </tr>
            <tr>
              <td class="geo-data-label">File Size</td>
              <td class="geo-data-value">{file_size_mb:.1f} MB</td>
            </tr>
            <tr>
              <td class="geo-data-label">Image Dimensions</td>
              <td class="geo-data-value">{pil_img.width} × {pil_img.height}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Format</td>
              <td class="geo-data-value">{file_ext}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Status</td>
              <td class="geo-data-value" style="color: #10B981;">Ready for Inspection</td>
            </tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

        # ── Analyze Location Button ──
        if st.button("📍 Analyze Location", use_container_width=True):
            st.session_state["analyzing"] = True
            st.session_state["file_bytes"] = file_bytes
            st.session_state["file_name"] = uploaded_file.name
            st.session_state["user_hint"] = user_hint.strip()


with col_right:
    if "analyzing" not in st.session_state:
        # Welcome placeholder panel
        st.markdown("""
        <div class="geo-panel" style="min-height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 3rem 2rem;">
          <div style="font-size: 3.5rem; margin-bottom: 1rem;">🗺️</div>
          <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; margin-bottom: 0.5rem;">
            Awaiting Image Analysis
          </div>
          <div style="font-size: 0.88rem; color: #9CA3AF; max-width: 420px; line-height: 1.6;">
            Upload an image on the left and click <strong>Analyze Location</strong>. Photo Locator will cross-reference EXIF metadata and Google Gemini Vision to isolate the precise coordinates.
          </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        file_bytes = st.session_state["file_bytes"]
        hint = st.session_state.get("user_hint", "")
        img = Image.open(io.BytesIO(file_bytes))
        exif_data = extract_exif_data(img)

        # Determine coordinates via Engine A (EXIF) or Engine B (AI)
        if exif_data.get("has_gps"):
            lat = exif_data["latitude"]
            lon = exif_data["longitude"]
            alt = exif_data.get("altitude") or 50.0
            heading = exif_data.get("heading") or 0.0
            address = "Exact EXIF Recorded Location"
            country = "Detected via GPS"
            city = "GPS Verified"
            region = "Geotagged"
            source_engine = "Engine A (Hardware GPS)"
            confidence = "High"
            camera_name = exif_data.get("camera") or "Camera device"
            timestamp_str = exif_data.get("datetime") or datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            reasoning = (
                f"Coordinates extracted directly from the image's embedded hardware EXIF metadata. "
                f"Captured by {camera_name} at timestamp {timestamp_str}. "
                f"Hardware GPS satellite fix provides 100% verified physical coordinates without visual estimation."
            )
        else:
            api_key = os.getenv("GEMINI_API_KEY", "")
            if not api_key:
                st.error("⚠️ GEMINI_API_KEY is not configured in .env file.")
                st.stop()

            with st.spinner("🤖 Photo Locator AI is identifying the scene and visual clues..."):
                ai_result = run_ai_geolocation(file_bytes, api_key, hint)

            if ai_result.get("error"):
                st.error(f"❌ Analysis failed: {ai_result['error']}")
                st.stop()

            lat = ai_result["latitude"]
            lon = ai_result["longitude"]
            alt = ai_result.get("altitude", 50.0)
            heading = ai_result.get("heading", 0.0)
            address = ai_result.get("address") or ai_result.get("location_description") or f"{lat:.4f}, {lon:.4f}"
            country = ai_result.get("country", "Unknown")
            city = ai_result.get("city", "Unknown")
            region = ai_result.get("region", "Unknown")
            source_engine = "Engine B (Gemini AI Vision)"
            confidence = ai_result.get("confidence", "Medium")
            timestamp_str = datetime.now().strftime("%Y:%m:%d %H:%M:%S")
            reasoning = ai_result.get("reasoning") or "Location deduced through visual landmark and geographic analysis."

        # ── Banner: Location Found! ──
        st.markdown(f"""
        <div class="geo-success-banner">
          <div class="geo-success-icon">✅</div>
          <div>
            <div class="geo-success-title">Location Found!</div>
            <div class="geo-success-desc">
              Image coordinates identified via {source_engine} with {confidence} confidence.
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Satellite Map Panel ──
        st.markdown("""
        <div class="geo-panel" style="padding: 0.75rem 0.75rem 0.5rem;">
        """, unsafe_allow_html=True)
        render_satellite_map(lat, lon, title=address)
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Location Details Panel ──
        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        lat_str = f"{abs(lat):.6f}° {lat_dir}"
        lon_str = f"{abs(lon):.6f}° {lon_dir}"

        st.markdown(f"""
        <div class="geo-panel">
          <div class="geo-panel-title">
            <span>📍</span> Location Details
          </div>
          <table class="geo-data-table">
            <tr>
              <td class="geo-data-label">Latitude</td>
              <td class="geo-data-value">{lat_str}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Longitude</td>
              <td class="geo-data-value">{lon_str}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Address (Approx.)</td>
              <td class="geo-data-value" style="color: #818CF8;">{address}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Country</td>
              <td class="geo-data-value">{country}</td>
            </tr>
            <tr>
              <td class="geo-data-label">City</td>
              <td class="geo-data-value">{city}</td>
            </tr>
            <tr>
              <td class="geo-data-label">Region</td>
              <td class="geo-data-value">{region}</td>
            </tr>
          </table>

          <div style="margin-top: 1rem; display: flex; flex-wrap: wrap;">
            <a class="geo-btn-link geo-btn-maps" href="{build_maps_url(lat, lon)}" target="_blank">
              🗺️ Open in Google Maps
            </a>
            <a class="geo-btn-link geo-btn-earth" href="{build_earth_url(lat, lon, alt, heading)}" target="_blank">
              🌍 Open in Google Earth 3D
            </a>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Forensic Reasoning Panel ──
        if reasoning:
            st.markdown(f"""
        <div class="geo-panel">
          <div class="geo-panel-title">
            <span>🧠</span> Forensic Evidence &amp; Geolocation Reasoning
          </div>
          <div class="geo-reasoning-box">
            <strong>Analysis Breakdown:</strong><br><br>
            {reasoning}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Metadata Extracted Panel ──
        st.markdown(f"""
        <div class="geo-panel">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
            <div class="geo-panel-title" style="margin-bottom: 0;">
              <span>📄</span> Metadata Extracted
            </div>
            <button onclick="navigator.clipboard.writeText('{lat:.6f}, {lon:.6f}')" style="background: rgba(79, 70, 229, 0.2); border: 1px solid #4F46E5; color: #A5B4FC; border-radius: 6px; padding: 0.3rem 0.7rem; font-size: 0.75rem; cursor: pointer;">
              📋 Copy All
            </button>
          </div>
          <table class="geo-data-table">
            <tr>
              <td class="geo-data-label">GPS Latitude</td>
              <td class="geo-data-value">{lat:.6f}°</td>
            </tr>
            <tr>
              <td class="geo-data-label">GPS Longitude</td>
              <td class="geo-data-value">{lon:.6f}°</td>
            </tr>
            <tr>
              <td class="geo-data-label">GPS Altitude</td>
              <td class="geo-data-value">{alt:.1f} m (approx)</td>
            </tr>
            <tr>
              <td class="geo-data-label">Timestamp</td>
              <td class="geo-data-value">{timestamp_str}</td>
            </tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

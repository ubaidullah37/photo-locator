# 📍 Photo Locator

> **Find where in the world any photo was taken — powered by Hardware EXIF GPS and Multimodal AI Vision.**

Photo Locator is a local, privacy-first geolocation and digital forensic dashboard. It utilizes a **dual-engine intelligence pipeline** to uncover exact coordinates or deduce location from visual clues.

---

## ⚡ Dual-Engine Geolocation

| Engine | Method | Accuracy | When Used |
|---|---|---|---|
| **Engine A** 🛰️ | **Hardware EXIF GPS** | Pinpoint (~5 meters) | Automatic when original photo contains embedded camera GPS tags |
| **Engine B** 🤖 | **Gemini AI Vision** | Sub-meter to City/Region | When GPS metadata is missing, stripped by social media, or unavailable |

---

## ✨ Features

- 📤 **Drag & Drop Upload:** Supports JPG, JPEG, PNG, WEBP, TIFF, and HEIC files.
- 🛰️ **Hardware EXIF Extraction:** Automatically detects latitude, longitude, altitude, camera model, and original capture timestamp.
- 🤖 **AI Visual Landmark Analysis:** Identifies architecture, mountain ridges, vegetation, road markings, language scripts, and sun angles.
- 💡 **Optional Context Hint:** Have a hunch? Input city, region, or trip context to help the AI lock in precise coordinates.
- 🧠 **Forensic Evidence & Reasoning Breakdown:** Provides complete, transparent reasoning explaining which visual clues led to the deduced location.
- 🗺️ **Interactive Satellite Map:** High-resolution satellite imagery with custom markers and responsive viewport.
- 🌍 **Google Earth 3D Deep Link:** Jump directly into Google Earth 3D with camera heading, tilt, and altitude.
- 🗺️ **Google Maps Direct Link:** Instantly view roadmaps, terrain, and directions in Google Maps.
- 📋 **One-Click Metadata Copy:** Copy decimal pairs or full metadata coordinates directly to your clipboard.
- 🎨 **Dark Forensic Cyber UI:** Sleek modern interface built with Streamlit and Folium.

---

## 🚀 Quick Start (Windows)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ubaidullah37/photo-locator.git
   cd photo-locator
   ```

2. **Add your Gemini API Key:**
   - Copy `.env.example` to `.env`:
     ```bash
     copy .env.example .env
     ```
   - Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey) and paste it into `.env`:
     ```env
     GEMINI_API_KEY=your_actual_key_here
     ```

3. **Run the App:**
   - Simply double-click **`run.bat`**
   - The script will automatically create a Python virtual environment, install requirements, and open **http://localhost:8501** in your browser.

---

## 💻 Manual Setup (macOS / Linux / Developers)

```bash
# 1. Clone repository
git clone https://github.com/ubaidullah37/photo-locator.git
cd photo-locator

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: .\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY

# 5. Launch the app
streamlit run app.py
```

---

## 📁 Project Structure

```
photo-locator/
├── app.py              # Main Streamlit dashboard & UI
├── exif_engine.py      # Engine A: Hardware EXIF GPS extraction
├── geo_engine.py       # Engine B: Gemini AI visual geolocation & reasoning
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git exclusion rules (keeps API keys safe)
├── run.bat             # One-click Windows launcher
├── run.sh              # One-click macOS/Linux launcher
└── README.md           # Documentation
```

---

## 🔐 Privacy & Security

- **Strictly Local Execution:** Your photos, files, and GPS coordinates are processed on your local machine.
- **Never Commits API Keys:** The `.env` file is excluded in `.gitignore` to prevent secret leaks.
- **Defensive & Ethical Focus:** Designed for digital forensics, open-source intelligence (OSINT), and travel photo organization.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

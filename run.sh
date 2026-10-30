#!/usr/bin/env bash
# ============================================================
#  Photo Locator — macOS/Linux Quick-Start Script
#  Run: bash run.sh
# ============================================================

set -e

VENV_DIR="venv"
APP_FILE="app.py"
PORT=8501

echo ""
echo "  ============================================"
echo "    Photo Locator — Starting up..."
echo "  ============================================"
echo ""

# ── 1. Verify Python ──────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "  ERROR: python3 not found."
    echo "  Install it from https://www.python.org or via your package manager."
    exit 1
fi

PYTHON=$(command -v python3)
echo "  [1/4] Using Python: $($PYTHON --version)"

# ── 2. Create virtual environment ─────────────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "  [2/4] Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    echo "  [2/4] Done."
else
    echo "  [2/4] Virtual environment already exists, skipping creation."
fi

# ── 3. Activate and install deps ──────────────────────────────────────────
source "$VENV_DIR/bin/activate"
echo "  [3/4] Installing / updating dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
echo "  [3/4] Done."

# ── 4. Check for .env file ────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo ""
    echo "  NOTICE: No .env file found."
    echo "  A template .env file has been created — please add your GEMINI_API_KEY."
    echo "  Get a free key at: https://aistudio.google.com/app/apikey"
    echo ""
    cp .env.example .env
    echo "  Edit .env then re-run this script."
    exit 0
fi

# ── 5. Launch the app ─────────────────────────────────────────────────────
echo "  [4/4] Launching GeoSnap Locator..."
echo ""
echo "  Open your browser at: http://localhost:$PORT"
echo "  Press Ctrl+C to stop."
echo ""

# Open browser in background on macOS or Linux
if command -v open &>/dev/null; then
    sleep 1.5 && open "http://localhost:$PORT" &
elif command -v xdg-open &>/dev/null; then
    sleep 1.5 && xdg-open "http://localhost:$PORT" &
fi

streamlit run "$APP_FILE" \
    --server.port "$PORT" \
    --server.headless false \
    --browser.gatherUsageStats false

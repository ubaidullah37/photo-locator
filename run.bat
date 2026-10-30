@echo off
title Photo Locator
echo.
echo  ============================================
echo    Photo Locator -- Starting up...
echo  ============================================
echo.

:: Use absolute path to venv python.exe -- avoids broken launcher issue
set "VENV_PYTHON=%~dp0venv\Scripts\python.exe"
set "APP=%~dp0app.py"
set "REQS=%~dp0requirements.txt"

:: Step 1: Create venv if missing
if not exist "%VENV_PYTHON%" (
    echo  [1/3] Creating virtual environment...
    python -m venv "%~dp0venv"
    if errorlevel 1 (
        echo  ERROR: Could not create virtual environment.
        echo         Make sure Python 3.9+ is installed and on PATH.
        pause
        exit /b 1
    )
) else (
    echo  [1/3] Virtual environment found.
)

:: Step 2: Install / update dependencies
echo  [2/3] Installing dependencies...
"%VENV_PYTHON%" -m pip install -r "%REQS%" --quiet --disable-pip-version-check
echo  [2/3] Done.

:: Step 3: Launch app
echo  [3/3] Launching Photo Locator in your browser...
echo.
echo   Press Ctrl+C in this window to stop the app.
echo.

:: Open browser after a short delay
start "" timeout /t 2 /nobreak >nul
start "" "http://localhost:8501"

:: Run streamlit via python -m (bypasses broken .exe launchers)
"%VENV_PYTHON%" -m streamlit run "%APP%" --server.headless false --browser.gatherUsageStats false

pause

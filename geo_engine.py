"""
geo_engine.py — Engine B: Gemini AI Visual Geolocation
Uses Google Gemini multimodal models to estimate geographic location
from visual cues in a photo (landmarks, terrain, signage, architecture, etc.).
"""

import json
import os
import re
import time
from typing import Optional, Any

from google import genai
from google.genai import types


# ── System instructions ────────────────────────────────────────────────────────

_BASE_CLUES = """
Analyse EVERY visual clue thoroughly:
- Recognisable landmarks, mountains, distinctive buildings, bridges, mosques, monuments, skyline silhouettes
- Architectural styles, roof design, window grilles, brickwork, and local construction materials
- Text, road signs, billboards, scripts, languages, vehicle number plate formats
- Flora and vegetation (species, palm trees, conifer forests, foliage, climate type)
- Geomorphology and terrain (soil color, rock formations, mountain ridges, coastlines)
- Road infrastructure: traffic direction (LHT/RHT), lane markings, curb colors, road surface
- Lighting, shadow angles, and sun direction to determine camera heading
- Surrounding utility poles, electrical socket types, fencing, water towers

Always provide your best estimate with precise decimal coordinates.
Provide detailed, transparent reasoning explaining EXACTLY which visual clues led to this location conclusion, what features ruled in or ruled out other areas, and if confidence is limited, why.

Format your answer strictly as a JSON object with:
- latitude (float, decimal degrees)
- longitude (float, decimal degrees)
- altitude_meters (float, estimated meters above sea level)
- heading_degrees (float, estimated camera facing compass heading 0-360)
- confidence ("High", "Medium", or "Low")
- reasoning (comprehensive, multi-sentence step-by-step forensic reasoning explaining every visual and contextual clue that led to this suggested location)
- location_description (human-readable specific place name, e.g. "Faisal Mosque, Islamabad, Pakistan")
- address (approximate specific address/place name, e.g. "Faisal Mosque, Islamabad, Pakistan")
- country (string, e.g. "Pakistan")
- city (string, e.g. "Islamabad")
- region (string, administrative state or province, e.g. "Islamabad Capital Territory")
"""

SYSTEM_INSTRUCTION = (
    "You are Photo Locator AI, an expert digital forensics and image geolocation analyst.\n\n"
    "Your task is to examine a photograph and accurately estimate the geographic location where it was taken.\n"
    + _BASE_CLUES
)


def _build_system_instruction(user_hint: str) -> str:
    """Return system instruction, optionally injecting the user's hint."""
    hint = user_hint.strip()
    if not hint:
        return SYSTEM_INSTRUCTION

    return (
        "You are Photo Locator AI, an expert digital forensics and image geolocation analyst.\n\n"
        "Your task is to examine a photograph and accurately estimate the geographic location where it was taken.\n\n"
        "*** IMPORTANT — The user has provided a contextual hint about this photo: ***\n"
        f"    \"{hint}\"\n\n"
        "Use this hint as a strong geographic anchor:\n"
        "  • Narrow your search to the area, country, region, or landmark mentioned.\n"
        "  • Use visual clues inside the image to pin down the precise sub-location.\n"
        "  • If the hint names a specific well-known place, prioritise exact coordinates for that place.\n"
        "  • In your reasoning, explain clearly how the hint influenced your estimate.\n\n"
        + _BASE_CLUES
    )


# ── Model cascade ──────────────────────────────────────────────────────────────

MODELS_CASCADE = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]


# ── Public API ─────────────────────────────────────────────────────────────────

def run_ai_geolocation(img_bytes: bytes, api_key: str, user_hint: str = "") -> dict:
    """
    Call Gemini Multimodal Vision API with the image and return a geolocation result dict.

    Parameters
    ----------
    img_bytes : raw image bytes
    api_key   : Gemini API key
    user_hint : optional text hint provided by user

    Keys returned:
      latitude, longitude, altitude, heading, confidence, reasoning,
      location_description, address, country, city, region, error (if any)
    """
    try:
        client = genai.Client(api_key=api_key)
        mime_type = _detect_mime(img_bytes)

        hint = user_hint.strip()
        if hint:
            prompt = (
                f"USER CONTEXT HINT: {hint}\n\n"
                "With this context, analyse the photograph carefully and determine its precise geographic location. "
                "Identify landmarks, mountains, signs, architectural details, vegetation, or cityscapes. "
                "Provide detailed, in-depth reasoning explaining every piece of visual evidence that supports this deduction. "
                "Return precise coordinates, altitude, heading, address, country, city, region, confidence, and reasoning in JSON."
            )
        else:
            prompt = (
                "Analyse this photograph carefully and determine its precise geographic location. "
                "Identify landmarks, mountains, signs, architectural details, vegetation, or cityscapes. "
                "Provide detailed, in-depth reasoning explaining every piece of visual evidence that supports this deduction. "
                "Return precise coordinates, altitude, heading, address, country, city, region, confidence, and reasoning in JSON."
            )

        system_instr = _build_system_instruction(hint)

        config = types.GenerateContentConfig(
            system_instruction=system_instr,
            response_mime_type="application/json",
            temperature=0.2,
        )

        last_error = None
        for model_name in MODELS_CASCADE:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=img_bytes, mime_type=mime_type),
                            prompt,
                        ],
                        config=config,
                    )

                    raw_text = response.text
                    if not raw_text:
                        continue

                    parsed = _parse_and_normalize(raw_text)
                    if parsed:
                        parsed["model_used"] = model_name
                        return parsed
                except Exception as model_err:
                    last_error = model_err
                    err_str = str(model_err)
                    if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str:
                        time.sleep(1.5)
                        continue
                    break

        if last_error:
            return {"error": f"Gemini API request failed: {last_error}"}
        return {"error": "Could not determine location from image."}

    except Exception as exc:
        return {"error": str(exc)}


def _detect_mime(data: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"\x89PNG":
        return "image/png"
    if data[:4] in (b"RIFF", b"WEBP") or b"WEBP" in data[:12]:
        return "image/webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    return "image/jpeg"


def _parse_and_normalize(raw_text: str) -> Optional[dict]:
    """Parse JSON and normalize fields to expected schema."""
    try:
        obj = json.loads(raw_text)
        return _normalize_dict(obj)
    except Exception:
        match = re.search(r"(\[.*\]|\{.*\})", raw_text, re.DOTALL)
        if match:
            try:
                obj = json.loads(match.group(1))
                return _normalize_dict(obj)
            except Exception:
                pass
    return None


def _normalize_dict(data: Any) -> Optional[dict]:
    if isinstance(data, list) and len(data) > 0:
        data = data[0]

    if not isinstance(data, dict):
        return None

    if "latitude" not in data or "longitude" not in data:
        return None

    try:
        lat = float(data["latitude"])
        lon = float(data["longitude"])
        alt = float(data.get("altitude_meters", data.get("altitude", 50.0)))
        hdg = float(data.get("heading_degrees", data.get("heading", 0.0))) % 360

        conf_raw = data.get("confidence", "Medium")
        if isinstance(conf_raw, (int, float)):
            if conf_raw >= 0.8:
                conf = "High"
            elif conf_raw >= 0.5:
                conf = "Medium"
            else:
                conf = "Low"
        else:
            conf_str = str(conf_raw).strip().capitalize()
            conf = conf_str if conf_str in ("High", "Medium", "Low") else "Medium"

        reasoning = str(data.get("reasoning", "Location determined from visual analysis."))
        loc_desc = str(data.get("location_description", f"{lat:.4f}, {lon:.4f}"))
        address = str(data.get("address", loc_desc))
        country = str(data.get("country", "Unknown"))
        city = str(data.get("city", "Unknown"))
        region = str(data.get("region", "Unknown"))

        return {
            "latitude": lat,
            "longitude": lon,
            "altitude": alt,
            "heading": hdg,
            "confidence": conf,
            "reasoning": reasoning,
            "location_description": loc_desc,
            "address": address,
            "country": country,
            "city": city,
            "region": region,
            "error": None,
        }
    except Exception:
        return None

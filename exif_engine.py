"""
exif_engine.py — Engine A: Hardware EXIF GPS Extractor
Extracts GPS coordinates, heading, altitude, camera info from image EXIF metadata.
"""

import io
from typing import Any

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


def _get_if_exist(data: dict, key: str) -> Any:
    return data[key] if key in data else None


def _convert_to_degrees(value) -> float:
    """Convert GPS DMS rational to float decimal degrees."""
    d, m, s = value
    return float(d) + float(m) / 60.0 + float(s) / 3600.0


def extract_exif_data(img: Image.Image) -> dict:
    """
    Extract all EXIF tags and GPS info from a PIL Image.

    Returns a dict with keys:
      has_gps      : bool
      latitude     : float | None
      longitude    : float | None
      altitude     : float | None
      heading      : float | None
      datetime     : str | None
      camera       : str | None
      all_tags     : dict of human-readable EXIF tags
    """
    result = {
        "has_gps": False,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "heading": 0.0,
        "datetime": None,
        "camera": None,
        "all_tags": {},
    }

    try:
        raw_exif = img._getexif()
    except Exception:
        raw_exif = None

    if not raw_exif:
        return result

    exif: dict = {}
    gps_info: dict = {}

    for tag_id, value in raw_exif.items():
        tag = TAGS.get(tag_id, str(tag_id))
        if tag == "GPSInfo":
            for gps_tag_id, gps_val in value.items():
                gps_tag = GPSTAGS.get(gps_tag_id, str(gps_tag_id))
                gps_info[gps_tag] = gps_val
        else:
            exif[tag] = value

    # ── All human-readable tags for the inspector ──────────────────────────
    readable: dict = {}
    for k, v in exif.items():
        try:
            str_v = str(v)
            if len(str_v) < 300:
                readable[k] = str_v
        except Exception:
            pass
    for k, v in gps_info.items():
        try:
            str_v = str(v)
            if len(str_v) < 300:
                readable[f"GPS.{k}"] = str_v
        except Exception:
            pass
    result["all_tags"] = readable

    # ── Camera / device info ───────────────────────────────────────────────
    make  = exif.get("Make", "")
    model = exif.get("Model", "")
    if make or model:
        result["camera"] = f"{make} {model}".strip()

    # ── Datetime ───────────────────────────────────────────────────────────
    result["datetime"] = exif.get("DateTimeOriginal") or exif.get("DateTime")

    # ── GPS ────────────────────────────────────────────────────────────────
    if not gps_info:
        return result

    gps_lat  = _get_if_exist(gps_info, "GPSLatitude")
    gps_lat_ref = _get_if_exist(gps_info, "GPSLatitudeRef")
    gps_lon  = _get_if_exist(gps_info, "GPSLongitude")
    gps_lon_ref = _get_if_exist(gps_info, "GPSLongitudeRef")

    if gps_lat and gps_lat_ref and gps_lon and gps_lon_ref:
        lat = _convert_to_degrees(gps_lat)
        lon = _convert_to_degrees(gps_lon)

        if gps_lat_ref == "S":
            lat = -lat
        if gps_lon_ref == "W":
            lon = -lon

        result["has_gps"] = True
        result["latitude"]  = round(lat, 8)
        result["longitude"] = round(lon, 8)

    # ── Altitude ───────────────────────────────────────────────────────────
    gps_alt = _get_if_exist(gps_info, "GPSAltitude")
    if gps_alt is not None:
        try:
            alt_val = float(gps_alt)
            gps_alt_ref = _get_if_exist(gps_info, "GPSAltitudeRef")
            if gps_alt_ref == 1:
                alt_val = -alt_val  # below sea level
            result["altitude"] = round(alt_val, 2)
        except Exception:
            result["altitude"] = 0.0
    else:
        result["altitude"] = 0.0

    # ── Heading / ImgDirection ─────────────────────────────────────────────
    for hdg_key in ("GPSImgDirection", "GPSTrack"):
        gps_hdg = _get_if_exist(gps_info, hdg_key)
        if gps_hdg is not None:
            try:
                result["heading"] = float(gps_hdg) % 360
                break
            except Exception:
                pass

    return result


def format_exif_display(exif_data: dict) -> dict:
    """Format EXIF GPS fields for table display."""
    rows = {}

    if exif_data.get("latitude") is not None:
        lat = exif_data["latitude"]
        rows["Latitude"] = f"{abs(lat):.8f}° {'N' if lat >= 0 else 'S'}"

    if exif_data.get("longitude") is not None:
        lon = exif_data["longitude"]
        rows["Longitude"] = f"{abs(lon):.8f}° {'E' if lon >= 0 else 'W'}"

    if exif_data.get("altitude") is not None:
        rows["Altitude"] = f"{exif_data['altitude']:.2f} m"

    if exif_data.get("heading") is not None:
        rows["Camera Heading"] = f"{exif_data['heading']:.2f}°"

    if exif_data.get("datetime"):
        rows["Date / Time"] = exif_data["datetime"]

    if exif_data.get("camera"):
        rows["Camera"] = exif_data["camera"]

    return rows

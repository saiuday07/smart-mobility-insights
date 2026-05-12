import time
import requests

OSRM_BASE = "http://router.project-osrm.org"
NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
_last_nominatim = 0


def geocode(query):
    global _last_nominatim
    now = time.time()
    if now - _last_nominatim < 1.0:
        time.sleep(1.0 - (now - _last_nominatim))
    url = f"{NOMINATIM_BASE}/search"
    params = {"q": query, "format": "json", "limit": 5, "addressdetails": 1}
    resp = requests.get(url, params=params, headers={"User-Agent": "SmartMobility/1.0"}, timeout=10)
    _last_nominatim = time.time()
    resp.raise_for_status()
    return resp.json()


def reverse_geocode(lat, lng):
    url = f"{NOMINATIM_BASE}/reverse"
    params = {"lat": lat, "lon": lng, "format": "json"}
    resp = requests.get(url, params=params, headers={"User-Agent": "SmartMobility/1.0"}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_routes(origin_lat, origin_lng, dest_lat, dest_lng):
    coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
    url = f"{OSRM_BASE}/route/v1/driving/{coords}"
    params = {
        "alternatives": "true",
        "overview": "full",
        "geometries": "geojson",
        "steps": "false",
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

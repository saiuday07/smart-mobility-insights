import os
from datetime import datetime, timedelta

import requests

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
CACHE_TTL = timedelta(minutes=30)
_cache = {}

FACTORS = {
    "thunderstorm": 0.9,
    "severe_thunderstorm": 1.2,
    "drizzle": 0.1,
    "rain_light": 0.15,
    "rain_moderate": 0.35,
    "rain_heavy": 0.6,
    "rain_extreme": 1.0,
    "freezing_rain": 1.2,
    "snow_light": 0.3,
    "snow_heavy": 0.8,
    "fog": 0.2,
    "haze": 0.1,
    "mist": 0.05,
}


def _condition_to_factor(weather_id):
    if 200 <= weather_id < 300:
        return FACTORS["severe_thunderstorm"] if weather_id >= 230 else FACTORS["thunderstorm"]
    if 300 <= weather_id < 400:
        return FACTORS["drizzle"]
    if 500 <= weather_id < 600:
        if weather_id == 500:
            return FACTORS["rain_light"]
        if weather_id == 501:
            return FACTORS["rain_moderate"]
        if weather_id == 511:
            return FACTORS["freezing_rain"]
        if 502 <= weather_id <= 504:
            return FACTORS["rain_extreme"] if weather_id >= 504 else FACTORS["rain_heavy"]
        return FACTORS["rain_moderate"]
    if 600 <= weather_id < 700:
        return FACTORS["snow_heavy"] if weather_id >= 602 else FACTORS["snow_light"]
    if 700 <= weather_id < 800:
        return FACTORS["fog"] if 741 <= weather_id <= 751 else (FACTORS["haze"] if weather_id == 721 else FACTORS["mist"])
    if weather_id == 800:
        return 0.0
    if 800 < weather_id < 900:
        return 0.0
    return 0.0


def get_weather(lat, lng):
    key = f"{lat:.2f},{lng:.2f}"
    if key in _cache:
        ts, val = _cache[key]
        if datetime.now() - ts < CACHE_TTL:
            return val
    if not API_KEY:
        return None, None
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={API_KEY}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        body = resp.json()
        cond_id = body["weather"][0]["id"]
        desc = body["weather"][0]["description"]
        result = (cond_id, desc)
        _cache[key] = (datetime.now(), result)
        return result
    except Exception:
        return None, None


def get_weather_factor(lat, lng):
    cond_id, desc = get_weather(lat, lng)
    if cond_id is None:
        return 0.0, None
    return _condition_to_factor(cond_id), desc

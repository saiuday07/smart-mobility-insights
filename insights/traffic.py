import json
import os
from datetime import datetime


def _load_config():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(path) as f:
        return json.load(f)


def _to_minutes(t):
    parts = t.split(':')
    return int(parts[0]) * 60 + int(parts[1])


def get_time_factor(config):
    now = datetime.now()
    current = now.hour * 60 + now.minute
    tc = config['traffic']

    ms = _to_minutes(tc['peak_hours']['morning']['start'])
    me = _to_minutes(tc['peak_hours']['morning']['end'])
    es = _to_minutes(tc['peak_hours']['evening']['start'])
    ee = _to_minutes(tc['peak_hours']['evening']['end'])

    if (ms <= current <= me) or (es <= current <= ee):
        return tc['congestion_factors']['peak']
    elif current < 360 or current > 1320:
        return tc['congestion_factors']['night']
    elif (me < current < me + 60) or (ee < current < ee + 60):
        return tc['congestion_factors']['shoulder']
    else:
        return tc['congestion_factors']['off_peak']


def get_congestion_level(factor, config):
    th = config['traffic']['congestion_thresholds']
    if factor < th['light']:
        return 'light', '🟢'
    elif factor < th['moderate']:
        return 'moderate', '🟡'
    elif factor < th['heavy']:
        return 'heavy', '🟠'
    else:
        return 'congested', '🔴'


def get_area_factor(origin_name, dest_name, congestion_logs):
    names = [origin_name.lower(), dest_name.lower()]
    count = sum(1 for log in congestion_logs if log['location_name'].lower() in names)
    if count > 20:
        return 2.0
    elif count > 10:
        return 1.5
    elif count > 5:
        return 1.2
    return 1.0


def get_traffic_info(origin_name, dest_name, congestion_logs=None):
    config = _load_config()
    time_factor = get_time_factor(config)
    area_factor = get_area_factor(origin_name, dest_name, congestion_logs or [])
    combined = max(time_factor, area_factor)
    level, icon = get_congestion_level(combined, config)
    return {
        'factor': round(combined, 2),
        'level': level,
        'icon': icon,
        'time_factor': time_factor,
        'area_factor': area_factor,
    }

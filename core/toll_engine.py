import json
import os


def _load_config():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(path) as f:
        return json.load(f)


def calculate_slab_toll(distance):
    config = _load_config()
    tc = config['toll']
    for slab in tc['slabs']:
        if slab['max_km'] is None or distance <= slab['max_km']:
            return slab['rate']
    return tc['slabs'][-1]['rate']


def calculate_dynamic_toll(distance):
    config = _load_config()
    return distance * config['toll']['dynamic_rate_per_km']


def vehicle_multiplier(vehicle):
    config = _load_config()
    return config['toll']['vehicle_multipliers'].get(vehicle.lower(), 1.0)


def choose_pricing_model(distance):
    if distance is None:
        return "slab"
    config = _load_config()
    threshold = config['toll']['decision_threshold_km']
    return "slab" if distance <= threshold else "dynamic"

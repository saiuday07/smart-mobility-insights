import json
import os


def _load_config():
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'config.json')
    with open(path) as f:
        return json.load(f)


def compute_toll(distance_km, vehicle_type):
    if distance_km is None:
        return None, None

    config = _load_config()
    tc = config['toll']

    if distance_km <= tc['decision_threshold_km']:
        pricing_model = "slab"
        base_toll = tc['slabs'][-1]['rate']
        for slab in tc['slabs']:
            if slab['max_km'] is None or distance_km <= slab['max_km']:
                base_toll = slab['rate']
                break
    else:
        pricing_model = "dynamic"
        base_toll = distance_km * tc['dynamic_rate_per_km']

    vehicle = vehicle_type.lower()
    multiplier = tc['vehicle_multipliers'].get(vehicle, 1.0)
    final_toll = round(base_toll * multiplier, 2)
    return final_toll, pricing_model

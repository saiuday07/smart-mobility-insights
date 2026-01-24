# toll_engine.py

def calculate_slab_toll(distance):
    # Slabs increase gradually
    if distance <= 5:
        return 10
    elif distance <= 10:
        return 20
    elif distance <= 15:
        return 30
    elif distance <= 20:
        return 40
    else:
        return 60


def calculate_dynamic_toll(distance):
    rate_per_km = 2
    return distance * rate_per_km


def vehicle_multiplier(vehicle):
    if vehicle == "bike":
        return 0.5
    elif vehicle == "car":
        return 1.0
    elif vehicle == "bus":
        return 1.5
    elif vehicle == "truck":
        return 2.0
    elif vehicle == "ambulance":
        return 0
    else:
        return 1.0

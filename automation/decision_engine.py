
def choose_pricing_model(distance):
    if distance is None:
        return "slab"
    elif distance <= 10:
        return "slab"
    else:
        return "dynamic"

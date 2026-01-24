# Sample road map with distances between entry and exit points

road_map = {
    ("GateA", "GateB"): 5,
    ("GateA", "GateC"): 12,
    ("GateA", "GateD"): 18,
    ("GateB", "GateC"): 7,
    ("GateB", "GateD"): 14,
    ("GateC", "GateD"): 6
}

def get_distance(entry, exit):
    if (entry, exit) in road_map:
        return road_map[(entry, exit)]
    elif (exit, entry) in road_map:
        return road_map[(exit, entry)]
    else:
        return None

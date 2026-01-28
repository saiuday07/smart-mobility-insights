from collections import defaultdict

# Set road type: "city" or "highway"
ROAD_TYPE = "city"

# Base toll rates for highway use
BASE_TOLL = {
    "bike": 0,
    "car": 10,
    "bus": 20,
    "truck": 30
}

# Sample vehicle movement data
vehicle_log = [
    ("GateA", "GateB", "car", 5),
    ("GateA", "GateC", "bus", 8),
    ("GateB", "GateC", "car", 4),
    ("GateA", "GateD", "truck", 12),
    ("GateC", "GateD", "bike", 6),
    ("GateB", "GateD", "car", 10),
]

# Count vehicles passing through each gate
def gate_footfall():
    counts = defaultdict(int)
    for entry, exit, _, _ in vehicle_log:
        counts[entry] += 1
        counts[exit] += 1
    return counts

# Show traffic level at each gate
def display_traffic_summary():
    counts = gate_footfall()
    print("\n--- Traffic Summary ---")
    for gate, num in counts.items():
        if num >= 4:
            congestion = "High"
        elif num >= 2:
            congestion = "Moderate"
        else:
            congestion = "Low"
        print(f"{gate}: {num} vehicles ({congestion})")

# Give safety suggestion based on congestion
def mobility_nudge(entry, exit):
    counts = gate_footfall()
    if counts.get(entry, 0) >= 4 or counts.get(exit, 0) >= 4:
        print("⚠️ Route is crowded. Consider another path or time.")
    else:
        print("✅ Route is clear and safe.")

# Calculate toll only when road is highway
def calculate_toll(vehicle, distance_km):
    if ROAD_TYPE == "city":
        return 0
    return BASE_TOLL.get(vehicle, 0) + distance_km * 2

# Run the command-line dashboard
def run_dashboard():
    print("\nSmart Mobility Insights System")
    print(f"Road Type: {ROAD_TYPE}")

    display_traffic_summary()

    for entry, exit, vehicle, distance in vehicle_log:
        print("\nTrip:", entry, "to", exit)
        mobility_nudge(entry, exit)
        toll = calculate_toll(vehicle, distance)
        print(f"Vehicle: {vehicle}")
        print(f"Distance: {distance} km")
        print(f"Toll: ₹{toll}")

# Start the program
if __name__ == "__main__":
    run_dashboard()

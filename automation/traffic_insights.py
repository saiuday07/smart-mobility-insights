from collections import defaultdict

# Simulated vehicle log: each trip is (entry, exit, vehicle)
vehicle_log = [
    ("GateA", "GateB", "car"),
    ("GateA", "GateC", "bus"),
    ("GateB", "GateC", "car"),
    ("GateA", "GateD", "truck"),
    ("GateC", "GateD", "bike"),
    ("GateB", "GateD", "car"),
]

def gate_footfall():
    counts = defaultdict(int)
    for entry, exit, _ in vehicle_log:
        counts[entry] += 1
        counts[exit] += 1
    return counts


# ASCII bar helper (INLINE, no new file)
def ascii_bar(label, value, scale=1):
    blocks = "█" * (value * scale)
    print(f"{label:<6} | {blocks} ({value})")


def display_traffic_summary():
    counts = gate_footfall()
    print("\n--- TRAFFIC / FOOTFALL DASHBOARD ---")

    for gate, num in counts.items():
        ascii_bar(gate, num)


def mobility_nudge(entry, exit):
    counts = gate_footfall()
    entry_congestion = counts.get(entry, 0)
    exit_congestion = counts.get(exit, 0)

    print("\n💡 Safe-Mobility Nudge:")
    if entry_congestion >= 4 or exit_congestion >= 4:
        print("High congestion detected. Consider alternate gates or off-peak travel.")
    else:
        print("Route looks reasonably clear. Safe to travel.")

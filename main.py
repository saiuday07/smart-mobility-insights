# main.py

from automation.distance_service import get_distance
from automation.decision_engine import choose_pricing_model
from core.toll_engine import (
    calculate_slab_toll,
    calculate_dynamic_toll,
    vehicle_multiplier
)
from automation.traffic_insights import (
    display_traffic_summary,
    mobility_nudge
)

def calculate_toll_flow():
    print("\n--- TOLL CALCULATION ---")
    entry = input("Enter ENTRY gate (GateA/GateB/GateC/GateD): ")
    exit = input("Enter EXIT gate (GateA/GateB/GateC/GateD): ")
    vehicle = input("Enter vehicle (bike/car/bus/truck/ambulance): ")

    distance = get_distance(entry, exit)
    if distance is None:
        print("❌ Invalid route.")
        return

    pricing_model = choose_pricing_model(distance)

    if pricing_model == "slab":
        base_toll = calculate_slab_toll(distance)
    else:
        base_toll = calculate_dynamic_toll(distance)

    multiplier = vehicle_multiplier(vehicle)
    final_toll = base_toll * multiplier

    print("\n--- SYSTEM OUTPUT ---")
    print(f"Distance: {distance} km")
    print(f"Pricing Model: {pricing_model.upper()}")
    print(f"Final Toll: ₹{round(final_toll, 2)}")

def mobility_nudge_flow():
    print("\n--- SAFE MOBILITY NUDGE ---")
    entry = input("Enter ENTRY gate: ")
    exit = input("Enter EXIT gate: ")
    mobility_nudge(entry, exit)

def dashboard():
    while True:
        print("\n===============================")
        print(" SMART MOBILITY INSIGHTS SYSTEM ")
        print("===============================")
        print("1. View Traffic & Footfall Summary")
        print("2. Get Safe Mobility Nudge")
        print("3. Calculate Toll for a Route")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            display_traffic_summary()
        elif choice == "2":
            mobility_nudge_flow()
        elif choice == "3":
            calculate_toll_flow()
        elif choice == "4":
            print("Exiting system. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

# Program entry point
if __name__ == "__main__":
    dashboard()

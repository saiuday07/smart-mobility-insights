from traffic_insights import display_traffic_summary, mobility_nudge

def main():
    print("\nSmart Mobility Insights System")

    while True:
        print("\nMenu:")
        print("1. View Traffic / Footfall Summary")
        print("2. Check Safe Mobility Nudge")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            display_traffic_summary()

        elif choice == "2":
            entry = input("Enter entry gate: ")
            exit = input("Enter exit gate: ")
            mobility_nudge(entry, exit)

        elif choice == "3":
            print("Exiting system.")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()

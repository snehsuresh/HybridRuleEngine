#!/usr/bin/env python3
import csv
import ctypes
import os
import pandas as pd
import matplotlib.pyplot as plt

# Load the shared library (assumes it is in the same directory)
lib_path = os.path.join(os.getcwd(), "librules.dylib")
rules_lib = ctypes.CDLL(lib_path)

# Define the prototype of evaluate_offer
rules_lib.evaluate_offer.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
]
rules_lib.evaluate_offer.restype = ctypes.c_char_p

# Read player data from CSV
data_file = "player_data.csv"
players = []
with open(data_file, newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        players.append(
            {
                "player_id": int(row["player_id"]),
                "level": int(row["level"]),
                "days_since_last_purchase": int(row["days_since_last_purchase"]),
                "matches_lost": int(row["matches_lost"]),
                "has_spent_money": int(row["has_spent_money"]),
            }
        )

# Evaluate offer for each player using the C function
results = []
for player in players:
    offer_bytes = rules_lib.evaluate_offer(
        player["level"],
        player["days_since_last_purchase"],
        player["matches_lost"],
        player["has_spent_money"],
    )
    offer = offer_bytes.decode("utf-8")
    results.append({"player_id": player["player_id"], "offer": offer})

# Save decisions for future analysis
results_file = "offer_decisions.csv"
with open(results_file, "w", newline="") as csvfile:
    fieldnames = ["player_id", "offer"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        writer.writerow(r)

print("Offer decisions saved to", results_file)

# Load results into a pandas DataFrame for visualization
df = pd.DataFrame(results)
offer_counts = df["offer"].value_counts()

# Plot a bar chart of the offer distribution
plt.figure(figsize=(8, 6))
offer_counts.plot(kind="bar")
plt.title("Offer Distribution")
plt.xlabel("Offer")
plt.ylabel("Number of Players")
plt.tight_layout()
plt.savefig("offer_distribution.png")
plt.show()

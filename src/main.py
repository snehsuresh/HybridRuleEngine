#!/usr/bin/env python3
import os
import csv
import json
import ctypes
import pandas as pd
import matplotlib.pyplot as plt
import concurrent.futures
import time

# Define base directory relative to this file.
base_dir = os.path.dirname(__file__)


# Helper to ensure directories exist before writing files.
def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


# Set file paths using relative directories.
data_file = os.path.join(base_dir, "..", "data", "player_data.csv")
lib_path = os.path.join(base_dir, "..", "lib", "librules.dylib")
config_file = os.path.join(base_dir, "..", "config", "rules_config.json")
plot_file = os.path.join(base_dir, "..", "visualizations", "offer_distribution.png")
results_file = os.path.join(base_dir, "..", "data", "offer_decisions.csv")

# Ensure required directories exist.
ensure_directory_exists(plot_file)
ensure_directory_exists(results_file)

# Load rules from JSON (all JSON parsing is now in Python)
with open(config_file, "r") as f:
    rules_data = json.load(f)["rules"]

num_rules = len(rules_data)

# Create ctypes arrays for the rule parameters.
min_levels = (ctypes.c_int * num_rules)(*[r["min_level"] for r in rules_data])
max_levels = (ctypes.c_int * num_rules)(*[r["max_level"] for r in rules_data])
min_days = (ctypes.c_int * num_rules)(
    *[r["min_days_since_last_purchase"] for r in rules_data]
)
max_days = (ctypes.c_int * num_rules)(
    *[r["max_days_since_last_purchase"] for r in rules_data]
)
min_matches = (ctypes.c_int * num_rules)(*[r["min_matches_lost"] for r in rules_data])
max_matches = (ctypes.c_int * num_rules)(*[r["max_matches_lost"] for r in rules_data])
spending_conditions = (ctypes.c_int * num_rules)(
    *[r["has_spent_money"] for r in rules_data]
)
weights = (ctypes.c_double * num_rules)(*[r["weight"] for r in rules_data])

# Load the shared library.
rules_lib = ctypes.CDLL(lib_path)

# Define the C function signature.
rules_lib.evaluate_offer.argtypes = [
    ctypes.c_int,  # level
    ctypes.c_int,  # days_since_last_purchase
    ctypes.c_int,  # matches_lost
    ctypes.c_int,  # has_spent_money
    ctypes.c_int,  # number of rules
    ctypes.POINTER(ctypes.c_int),  # min_levels
    ctypes.POINTER(ctypes.c_int),  # max_levels
    ctypes.POINTER(ctypes.c_int),  # min_days
    ctypes.POINTER(ctypes.c_int),  # max_days
    ctypes.POINTER(ctypes.c_int),  # min_matches
    ctypes.POINTER(ctypes.c_int),  # max_matches
    ctypes.POINTER(ctypes.c_int),  # spending_conditions
    ctypes.POINTER(ctypes.c_double),  # weights
]
rules_lib.evaluate_offer.restype = ctypes.c_char_p

# Load player data.
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


# -------------------------------------------------------------------
# Pure Python Implementation of Rule Evaluation for Comparison
# -------------------------------------------------------------------
def evaluate_offer_py(player, rules):
    best_weight = -1.0
    best_rule_index = -1
    for i, rule in enumerate(rules):
        if player["level"] < rule["min_level"] or player["level"] > rule["max_level"]:
            continue
        if (
            player["days_since_last_purchase"] < rule["min_days_since_last_purchase"]
            or player["days_since_last_purchase"] > rule["max_days_since_last_purchase"]
        ):
            continue
        if (
            player["matches_lost"] < rule["min_matches_lost"]
            or player["matches_lost"] > rule["max_matches_lost"]
        ):
            continue
        if (
            rule["has_spent_money"] != -1
            and rule["has_spent_money"] != player["has_spent_money"]
        ):
            continue
        if rule["weight"] > best_weight:
            best_weight = rule["weight"]
            best_rule_index = i
    if best_rule_index == -1:
        return "default_offer"
    offers = ["discount", "first_purchase_bonus", "regular_offer", "special_reward"]
    return offers[best_rule_index % 4]


# -------------------------------------------------------------------
# C-based Evaluation Function (as before)
def evaluate_player(player):
    offer_bytes = rules_lib.evaluate_offer(
        player["level"],
        player["days_since_last_purchase"],
        player["matches_lost"],
        player["has_spent_money"],
        num_rules,
        min_levels,
        max_levels,
        min_days,
        max_days,
        min_matches,
        max_matches,
        spending_conditions,
        weights,
    )
    offer = offer_bytes.decode("utf-8")
    return {"player_id": player["player_id"], "offer": offer}


# -------------------------------------------------------------------
# Benchmarking Both Methods
# -------------------------------------------------------------------
# Evaluate using the C-based method in parallel.
start_time = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    c_results = list(executor.map(evaluate_player, players))
c_duration = time.time() - start_time

# Evaluate using the pure Python method (single-threaded for simplicity).
start_time = time.time()
py_results = []
for player in players:
    offer = evaluate_offer_py(player, rules_data)
    py_results.append({"player_id": player["player_id"], "offer": offer})
py_duration = time.time() - start_time

print(f"C-based evaluation took {c_duration:.4f} seconds for {len(players)} players.")
print(
    f"Pure Python evaluation took {py_duration:.4f} seconds for {len(players)} players."
)

# Choose one result set to save and visualize (e.g., C-based result)
results = c_results

# Save decisions for future analysis.
with open(results_file, "w", newline="") as csvfile:
    fieldnames = ["player_id", "offer"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print("Offer decisions saved to", results_file)

# Create a bar chart of the offer distribution.
df = pd.DataFrame(results)
plt.figure(figsize=(8, 6))
df["offer"].value_counts().plot(kind="bar")
plt.title("Offer Distribution")
plt.xlabel("Offer")
plt.ylabel("Number of Players")
plt.tight_layout()
plt.savefig(plot_file)
plt.show()

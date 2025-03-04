#!/usr/bin/env python3
import os
import csv
import json
import ctypes
import pandas as pd
import numpy as np
import time
from numba import njit, prange

base_dir = os.path.dirname(__file__)

def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

# File paths
data_file = os.path.join(base_dir, "..", "data", "player_data.csv")
lib_path = os.path.join(base_dir, "..", "lib", "librules.dylib")
config_file = os.path.join(base_dir, "..", "config", "rules_config.json")
results_file = os.path.join(base_dir, "..", "data", "offer_decisions_fast.csv")
metrics_file = os.path.join(base_dir, "..", "data", "evaluation_metrics_full.csv")

ensure_directory_exists(results_file)
ensure_directory_exists(metrics_file)

# Load rules
with open(config_file, "r") as f:
    rules_data = json.load(f)["rules"]

num_rules = len(rules_data)

# Prepare ctypes rule arrays
min_levels = np.array([r["min_level"] for r in rules_data], dtype=np.int32)
max_levels = np.array([r["max_level"] for r in rules_data], dtype=np.int32)
min_days = np.array([r["min_days_since_last_purchase"] for r in rules_data], dtype=np.int32)
max_days = np.array([r["max_days_since_last_purchase"] for r in rules_data], dtype=np.int32)
min_matches = np.array([r["min_matches_lost"] for r in rules_data], dtype=np.int32)
max_matches = np.array([r["max_matches_lost"] for r in rules_data], dtype=np.int32)
spending_conditions = np.array([r["has_spent_money"] for r in rules_data], dtype=np.int32)
weights = np.array([r["weight"] for r in rules_data], dtype=np.float64)

# Load player data
players = pd.read_csv(data_file)

num_players = len(players)

# Convert player fields into numpy arrays
levels = players['level'].values.astype(np.int32)
days_since_last_purchase = players['days_since_last_purchase'].values.astype(np.int32)
matches_lost = players['matches_lost'].values.astype(np.int32)
spent_money = players['has_spent_money'].values.astype(np.int32)

# Load C library
rules_lib = ctypes.CDLL(lib_path)

rules_lib.evaluate_offers_batch_fast.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_double),
    ctypes.POINTER(ctypes.c_int)
]

# Run fast C batch evaluation
offers_c = np.zeros(num_players, dtype=np.int32)
start_time = time.time()

rules_lib.evaluate_offers_batch_fast(
    num_players,
    levels.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    days_since_last_purchase.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    matches_lost.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    spent_money.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    num_rules,
    min_levels.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    max_levels.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    min_days.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    max_days.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    min_matches.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    max_matches.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    spending_conditions.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
    weights.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
    offers_c.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
)

c_duration = time.time() - start_time
print(f"Fast C batch evaluation took {c_duration:.4f} seconds for {num_players} players.")

# -----------------
# Numba Accelerated Python Evaluation
# -----------------
@njit(parallel=True)
def evaluate_offers_numba(levels, days_since_last_purchase, matches_lost, spent_money,
                          min_levels, max_levels, min_days, max_days, min_matches, max_matches, 
                          spending_conditions, weights):
    num_players = len(levels)
    num_rules = len(min_levels)
    offers = np.full(num_players, 4, dtype=np.int32)  # default_offer = 4

    for i in prange(num_players):
        best_weight = -1.0
        for j in range(num_rules):
            if not (min_levels[j] <= levels[i] <= max_levels[j]):
                continue
            if not (min_days[j] <= days_since_last_purchase[i] <= max_days[j]):
                continue
            if not (min_matches[j] <= matches_lost[i] <= max_matches[j]):
                continue
            if spending_conditions[j] != -1 and spending_conditions[j] != spent_money[i]:
                continue
            if weights[j] > best_weight:
                best_weight = weights[j]
                offers[i] = j % 4  # map rule to offer
    return offers

start_time = time.time()
offers_numba = evaluate_offers_numba(
    levels, days_since_last_purchase, matches_lost, spent_money,
    min_levels, max_levels, min_days, max_days, min_matches, max_matches,
    spending_conditions, weights
)
numba_duration = time.time() - start_time
print(f"Numba accelerated evaluation took {numba_duration:.4f} seconds.")

# Map offer IDs to names
offer_names = ["discount", "first_purchase_bonus", "regular_offer", "special_reward", "default_offer"]
results = pd.DataFrame({
    "player_id": players['player_id'],
    "offer": [offer_names[o] for o in offers_c]
})

results.to_csv(results_file, index=False)

# Save metrics
metrics = {
    "num_players": num_players,
    "num_rules": num_rules,
    "c_duration_seconds": c_duration,
    "numba_duration_seconds": numba_duration
}
pd.DataFrame([metrics]).to_csv(metrics_file, index=False)

print(f"Saved results to {results_file}")
print(f"Saved metrics to {metrics_file}")

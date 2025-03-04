#!/usr/bin/env python3
import os
import csv
import json
import ctypes
import pandas as pd
import matplotlib.pyplot as plt
import time

base_dir = os.path.dirname(__file__)


def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


data_file = os.path.join(base_dir, "..", "data", "player_data.csv")
lib_path = os.path.join(base_dir, "..", "lib", "librules.dylib")
config_file = os.path.join(base_dir, "..", "config", "rules_config.json")
plot_file = os.path.join(base_dir, "..", "visualizations", "offer_distribution.png")
results_file = os.path.join(base_dir, "..", "data", "offer_decisions.csv")

ensure_directory_exists(plot_file)
ensure_directory_exists(results_file)

with open(config_file, "r") as f:
    rules_data = json.load(f)["rules"]

num_rules = len(rules_data)

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

rules_lib = ctypes.CDLL(lib_path)

rules_lib.evaluate_offers_batch.argtypes = [
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_double),
    ctypes.c_char_p,
]

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

num_players = len(players)

levels = (ctypes.c_int * num_players)(*[p["level"] for p in players])
days_since_last_purchase = (ctypes.c_int * num_players)(
    *[p["days_since_last_purchase"] for p in players]
)
matches_lost = (ctypes.c_int * num_players)(*[p["matches_lost"] for p in players])
spent_money = (ctypes.c_int * num_players)(*[p["has_spent_money"] for p in players])

offers = (ctypes.c_char * 32 * num_players)()

start_time = time.time()

rules_lib.evaluate_offers_batch(
    num_players,
    levels,
    days_since_last_purchase,
    matches_lost,
    spent_money,
    num_rules,
    min_levels,
    max_levels,
    min_days,
    max_days,
    min_matches,
    max_matches,
    spending_conditions,
    weights,
    offers,
)

duration = time.time() - start_time
print(f"C batch evaluation took {duration:.4f} seconds for {num_players} players.")

results = [
    {"player_id": players[i]["player_id"], "offer": offers[i].value.decode("utf-8")}
    for i in range(num_players)
]

with open(results_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["player_id", "offer"])
    writer.writeheader()
    writer.writerows(results)

df = pd.DataFrame(results)
df["offer"].value_counts().plot(kind="bar")
plt.tight_layout()
plt.savefig(plot_file)
plt.show()

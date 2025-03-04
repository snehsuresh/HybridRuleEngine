#!/usr/bin/env python3
import os
import csv
import time
import pandas as pd
from evaluate import evaluate_offers_c, evaluate_offers_python
from rules_loader import load_rules
from visualize import plot_offer_distribution, save_metrics

base_dir = os.path.dirname(__file__)


def ensure_directory_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


# File paths
data_file = os.path.join(base_dir, "..", "data", "player_data.csv")
results_file = os.path.join(base_dir, "..", "data", "offer_decisions.csv")
metrics_file = os.path.join(base_dir, "..", "data", "evaluation_metrics.csv")
plot_file = os.path.join(base_dir, "..", "visualizations", "offer_distribution.png")

ensure_directory_exists(results_file)
ensure_directory_exists(plot_file)

# Load rules
rules = load_rules(os.path.join(base_dir, "..", "config", "rules_config.json"))

# Load players
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

# Evaluate offers using C (batch)
start = time.time()
c_results = evaluate_offers_c(players, rules)
c_duration = time.time() - start
print(f"C batch evaluation took {c_duration:.4f} seconds for {len(players)} players.")

# Evaluate offers using Python (baseline comparison)
start = time.time()
py_results = evaluate_offers_python(players, rules)
py_duration = time.time() - start
print(
    f"Pure Python evaluation took {py_duration:.4f} seconds for {len(players)} players."
)

# Save offer decisions (we’ll use C results for output)
with open(results_file, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["player_id", "offer"])
    writer.writeheader()
    writer.writerows(c_results)

# Plot and save metrics
plot_offer_distribution(c_results, plot_file)
save_metrics(metrics_file, c_duration, py_duration, len(players), rules)

print(f"Offer decisions saved to {results_file}")

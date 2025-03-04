#!/usr/bin/env python3
import csv
import random

NUM_PLAYERS = 1000000

with open("player_data.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Write header
    writer.writerow(
        [
            "player_id",
            "level",
            "days_since_last_purchase",
            "matches_lost",
            "has_spent_money",
        ]
    )
    # Generate player profiles with realistic distributions.
    for i in range(NUM_PLAYERS):
        player_id = i + 1
        level = random.randint(1, 50)
        days_since_last_purchase = random.randint(0, 30)
        matches_lost = random.randint(0, 10)
        has_spent_money = random.choice([0, 1])
        writer.writerow(
            [player_id, level, days_since_last_purchase, matches_lost, has_spent_money]
        )

print(f"Generated player_data.csv with {NUM_PLAYERS} players.")

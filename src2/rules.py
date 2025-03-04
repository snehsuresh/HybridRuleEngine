#!/usr/bin/env python3
import json

NUM_RULES = 150
rules = []

for i in range(NUM_RULES):
    rule = {
        "min_level": (i % 10) + 1,  # 1 to 10
        "max_level": ((i % 10) + 1) + 10,  # 11 to 20, etc.
        "min_days_since_last_purchase": (i % 5) * 2,  # 0,2,4,6,8
        "max_days_since_last_purchase": ((i % 5) * 2) + 5,  # 5-day window
        "min_matches_lost": i % 3,  # 0,1,2
        "max_matches_lost": (i % 3) + 3,  # window of 3
        "has_spent_money": 1 if (i % 3 == 0) else (0 if (i % 3 == 1) else -1),
        "offer": (
            "discount"
            if (i % 4 == 0)
            else (
                "first_purchase_bonus"
                if (i % 4 == 1)
                else ("regular_offer" if (i % 4 == 2) else "special_reward")
            )
        ),
        "weight": 1.0 + (i % 10) * 0.1,  # weight between 1.0 and 1.9
        "start_time": 0,  # always active for demo
        "end_time": 9999999999,
    }
    rules.append(rule)

config = {"rules": rules}

with open("rules_config.json", "w") as f:
    json.dump(config, f, indent=4)

print(f"Generated rules_config.json with {NUM_RULES} rules.")

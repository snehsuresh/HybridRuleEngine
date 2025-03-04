import ctypes
import os

base_dir = os.path.dirname(__file__)
lib_path = os.path.join(base_dir, "..", "lib", "librules.dylib")
rules_lib = ctypes.CDLL(lib_path)


def evaluate_offers_c(players, rules):
    num_players = len(players)
    num_rules = len(rules)

    # Convert to ctypes arrays
    levels = (ctypes.c_int * num_players)(*[p["level"] for p in players])
    days_since = (ctypes.c_int * num_players)(
        *[p["days_since_last_purchase"] for p in players]
    )
    matches_lost = (ctypes.c_int * num_players)(*[p["matches_lost"] for p in players])
    spent_money = (ctypes.c_int * num_players)(*[p["has_spent_money"] for p in players])

    min_levels = (ctypes.c_int * num_rules)(*[r["min_level"] for r in rules])
    max_levels = (ctypes.c_int * num_rules)(*[r["max_level"] for r in rules])
    min_days = (ctypes.c_int * num_rules)(
        *[r["min_days_since_last_purchase"] for r in rules]
    )
    max_days = (ctypes.c_int * num_rules)(
        *[r["max_days_since_last_purchase"] for r in rules]
    )
    min_matches = (ctypes.c_int * num_rules)(*[r["min_matches_lost"] for r in rules])
    max_matches = (ctypes.c_int * num_rules)(*[r["max_matches_lost"] for r in rules])
    spending_conditions = (ctypes.c_int * num_rules)(
        *[r["has_spent_money"] for r in rules]
    )
    weights = (ctypes.c_double * num_rules)(*[r["weight"] for r in rules])

    offers = (ctypes.c_char * 32 * num_players)()

    # Define signature
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
        ctypes.POINTER(ctypes.c_char),
    ]

    rules_lib.evaluate_offers_batch(
        num_players,
        levels,
        days_since,
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
        ctypes.cast(offers, ctypes.POINTER(ctypes.c_char)),
    )

    return [
        {"player_id": players[i]["player_id"], "offer": offers[i].value.decode("utf-8")}
        for i in range(num_players)
    ]


def evaluate_offers_python(players, rules):
    results = []
    for player in players:
        offer = evaluate_offer_py(player, rules)
        results.append({"player_id": player["player_id"], "offer": offer})
    return results


def evaluate_offer_py(player, rules):
    best_weight = -1.0
    best_offer = "default_offer"
    for rule in rules:
        if not (rule["min_level"] <= player["level"] <= rule["max_level"]):
            continue
        if not (
            rule["min_days_since_last_purchase"]
            <= player["days_since_last_purchase"]
            <= rule["max_days_since_last_purchase"]
        ):
            continue
        if not (
            rule["min_matches_lost"]
            <= player["matches_lost"]
            <= rule["max_matches_lost"]
        ):
            continue
        if (
            rule["has_spent_money"] != -1
            and rule["has_spent_money"] != player["has_spent_money"]
        ):
            continue
        if rule["weight"] > best_weight:
            best_weight = rule["weight"]
            best_offer = [
                "discount",
                "first_purchase_bonus",
                "regular_offer",
                "special_reward",
            ][rules.index(rule) % 4]
    return best_offer

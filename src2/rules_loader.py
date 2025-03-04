import json


def load_rules(filepath):
    with open(filepath, "r") as f:
        return json.load(f)["rules"]

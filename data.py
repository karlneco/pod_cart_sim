import json

def load_products():
    with open("products.json", "r") as f:
        return json.load(f)
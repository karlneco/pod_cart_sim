# discounts/whole_order.py
from . import register

VERB = "whole_order"
CATEGORY = "price"

def parse(line: str) -> dict:
    # "whole_order: 10"
    _, rest = line.split(":", 1)
    value = float(rest.strip())
    return {"verb": VERB, "value": value}

def apply(cart, products, rule) -> float:
    subtotal = sum(products[k]["price"] * q for k, q in cart.items())
    return subtotal * (rule["value"] / 100.0)

register(globals())

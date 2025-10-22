# discounts/min_total.py
from . import register

VERB = "min_total"
CATEGORY = "price"

def parse(line: str) -> dict:
    # "min_total: 100=10"
    _, rest = line.split(":", 1)
    min_total, percent = [x.strip() for x in rest.split("=")]
    return {"verb": VERB, "min_total": float(min_total), "percent": float(percent)}

def apply(cart, products, rule) -> float:
    subtotal = sum(products[k]["price"] * q for k, q in cart.items())
    if subtotal >= rule["min_total"]:
        return subtotal * (rule["percent"] / 100.0)
    return 0.0

register(globals())

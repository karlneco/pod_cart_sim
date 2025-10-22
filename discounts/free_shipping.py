# discounts/free_shipping.py
from . import register

VERB = "free_shipping"
CATEGORY = "shipping"

def parse(line: str) -> dict:
    # "free_shipping: 75"
    _, rest = line.split(":", 1)
    return {"verb": VERB, "min_total": float(rest.strip())}

def apply(cart, products, rule) -> float:
    # Shipping effects are handled in core simulate_cart (returns price discount = 0)
    return 0.0

register(globals())

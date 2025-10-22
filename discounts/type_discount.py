# discounts/type_discount.py
from . import register

VERB = "type_discount"
CATEGORY = "price"

def parse(line: str) -> dict:
    # "type_discount: tee,10"
    _, rest = line.split(":", 1)
    ptype, percent = [x.strip() for x in rest.split(",")]
    return {"verb": VERB, "product_type": ptype, "percent": float(percent)}

def apply(cart, products, rule) -> float:
    disc = 0.0
    for key, qty in cart.items():
        if products[key]["type"] == rule["product_type"]:
            disc += products[key]["price"] * qty * (rule["percent"] / 100.0)
    return disc

register(globals())

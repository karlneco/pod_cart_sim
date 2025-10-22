# discounts/cart_quantity_discount.py
from . import register

VERB = "cart_quantity_discount"
CATEGORY = "price"

def parse(line: str) -> dict:
    # "cart_quantity_discount: 5,10"
    _, rest = line.split(":", 1)
    qty, percent = [x.strip() for x in rest.split(",")]
    return {"verb": VERB, "min_qty": int(qty), "percent": float(percent)}

def apply(cart, products, rule) -> float:
    total_qty = sum(cart.values())
    if total_qty >= rule["min_qty"]:
        subtotal = sum(products[k]["price"] * q for k, q in cart.items())
        return subtotal * (rule["percent"] / 100.0)
    return 0.0

register(globals())

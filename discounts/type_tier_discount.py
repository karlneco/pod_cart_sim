# discounts/type_tier_discount.py
from . import register

VERB = "type_tier_discount"
CATEGORY = "price"

def parse(line: str) -> dict:
    # "type_tier_discount: tee, 3=3, 5=5"
    _, rest = line.split(":", 1)
    parts = [p.strip() for p in rest.split(",")]
    product_type, tiers = parts[0], parts[1:]
    thresholds = {}
    for t in tiers:
        if "=" in t:
            count, amount = [x.strip() for x in t.split("=")]
            if amount.endswith("%"):
                thresholds[int(count)] = ("percent", float(amount[:-1]))
            else:
                thresholds[int(count)] = ("amount", float(amount))
    return {"verb": VERB, "product_type": product_type, "thresholds": thresholds}

def apply(cart, products, rule) -> float:
    ptype = rule["product_type"]
    thresholds = rule["thresholds"]
    total_qty = sum(q for k, q in cart.items() if products[k]["type"] == ptype)
    applicable = 0.0
    for th, spec in thresholds.items():
        if total_qty >= th:
            dtype, value = spec
            if dtype == "percent":
                discount = 0.0
                for k, q in cart.items():
                    if products[k]["type"] == ptype:
                        discount += products[k]["price"] * q * (value / 100.0)
            else:
                discount = value * total_qty
            applicable = max(applicable, discount)
    return applicable

register(globals())

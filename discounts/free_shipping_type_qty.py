# discounts/free_shipping_type_qty.py
from . import register

VERB = "free_shipping_type_qty"
CATEGORY = "shipping"

# free_shipping_type_qty: type, qty

def parse(line: str) -> dict:
    _, rest = line.split(":", 1)
    ptype, qty = [x.strip() for x in rest.split(",", 1)]
    return {"verb": VERB, "product_type": ptype, "min_qty": int(qty)}


def apply(cart, products, rule) -> float:
    return 0.0


def apply_shipping(cart, products, rule, original_price, store_shipping) -> float:
    target_type = rule["product_type"]
    min_qty = int(rule["min_qty"])
    qty_total = sum(qty for key, qty in cart.items() if products[key]["type"] == target_type)
    if qty_total < min_qty:
        return 0.0

    type_shipping = 0.0
    for key, qty in cart.items():
        product = products[key]
        if product["type"] != target_type:
            continue

        per_product_real_ship = 0.0
        if qty >= 1:
            per_product_real_ship += product["real_shipping_first"]
        if qty > 1:
            per_product_real_ship += product["real_shipping_additional"] * (qty - 1)

        if product["use_real_shipping"]:
            type_shipping += per_product_real_ship
        else:
            type_shipping += product["store_shipping"]

    return type_shipping


register(globals())

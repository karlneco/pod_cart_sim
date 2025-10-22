# discounts/bogo.py
from . import register
from decimal import Decimal, ROUND_HALF_UP

VERB = "bogo"  # buy_x_get_y_free
CATEGORY = "price"
LABEL = "Buy X Get Y Free"


def _round_cents(x: float) -> float:
    """Round to nearest cent with half-up logic (e.g., 14.995 -> 15.00)."""
    return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse(line: str) -> dict:
    # Example: "bogo: tee,2,1" or "bogo: ,3,1" (blank = any type)
    _, rest = line.split(":", 1)
    ptype, buy_qty, free_qty = [x.strip() for x in rest.split(",")]
    return {
        "verb": VERB,
        "product_type": ptype if ptype else None,
        "buy_qty": int(buy_qty),
        "free_qty": int(free_qty),
    }


def apply(cart, products, rule):
    buy_qty = rule["buy_qty"]
    free_qty = rule["free_qty"]
    ptype = rule.get("product_type")

    eligible = []
    for key, qty in cart.items():
        product = products[key]
        if (ptype is None) or (product["type"] == ptype):
            eligible.extend([product["price"]] * qty)

    eligible.sort()  # cheapest first
    total_items = len(eligible)
    group_size = buy_qty + free_qty
    num_free = (total_items // group_size) * free_qty
    raw_amount = sum(eligible[:num_free])
    amount = _round_cents(raw_amount)

    # Dynamic label
    if ptype:
        label = f"Buy {buy_qty} of {ptype}, get {free_qty} free"
    else:
        label = f"Buy {buy_qty}, get {free_qty} free"

    return amount, label


register(globals())

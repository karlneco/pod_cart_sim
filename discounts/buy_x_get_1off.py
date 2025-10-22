# discounts/buy_x_get_1off.py
from . import register
from decimal import Decimal, ROUND_HALF_UP

VERB = "buy_x_get_1off"
CATEGORY = "price"
LABEL = "Buy X Get 1 at % Off"


def _round_cents(x: float) -> float:
    return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse(line: str) -> dict:
    # "buy_x_get_1off: 3,50"
    _, rest = line.split(":", 1)
    buy_qty, percent = [x.strip() for x in rest.split(",")]
    return {"verb": VERB, "buy_qty": int(buy_qty), "percent": float(percent)}


def apply(cart, products, rule):
    buy_qty = rule["buy_qty"]
    percent = rule["percent"]

    all_items = []
    for key, qty in cart.items():
        all_items.extend([products[key]["price"]] * qty)

    all_items.sort()  # cheapest first
    group_size = buy_qty + 1
    discounted_items = len(all_items) // group_size

    raw_amount = sum(all_items[:discounted_items]) * (percent / 100.0)
    amount = _round_cents(raw_amount)

    # Return (amount, label) so the UI can show a friendly line
    return amount, f"Buy {buy_qty} Get 1 at {percent}% Off"


register(globals())

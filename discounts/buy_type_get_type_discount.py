# discounts/buy_type_get_type_discount.py
from . import register
from decimal import Decimal, ROUND_HALF_UP

VERB = "buy_type_get_type_discount"
CATEGORY = "price"
LABEL = "Buy Type Get Type Discount"


def _round_cents(x: float) -> float:
    """Round to nearest cent with half-up logic (e.g., 14.995 -> 15.00)."""
    return float(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def parse(line: str) -> dict:
    # Example: "buy_type_get_type_discount: hoodie, tee, 15"
    _, rest = line.split(":", 1)
    from_type, to_type, percent = [x.strip() for x in rest.split(",")]
    return {
        "verb": VERB,
        "from_type": from_type,
        "to_type": to_type,
        "percent": float(percent),
    }


def apply(cart, products, rule):
    from_type = rule["from_type"]
    to_type = rule["to_type"]
    percent = rule["percent"]

    from_count = 0
    to_items = []

    # Count how many "from" items, and collect all "to" item prices
    for key, qty in cart.items():
        p = products[key]
        if p["type"] == from_type:
            from_count += qty
        elif p["type"] == to_type:
            to_items.extend([p["price"]] * qty)

    eligible = min(from_count, len(to_items))
    to_items.sort()  # cheapest discounted first

    raw_amount = sum(to_items[:eligible]) * (percent / 100.0)
    amount = _round_cents(raw_amount)

    # Return both amount and a descriptive label for the breakdown list
    return amount, f"Buy {from_type} → Get {to_type} {percent}% Off"


register(globals())

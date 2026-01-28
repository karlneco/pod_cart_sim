import os
from discounts import REGISTRY, load_all
from typing import Tuple, Union, List, Dict, Any

# auto-discover discount plugins on import
load_all()


def parse_discount_grammar(command_text):
    """
    Each line is like "verb: args". We dispatch to the plugin's parse().
    Unknown verbs are ignored (let you keep experiments in the textarea).
    """
    discount_rules = []
    for raw in command_text.strip().splitlines():
        line = raw.strip()
        if not line or ":" not in line:
            continue
        verb = line.split(":", 1)[0].strip()
        mod = REGISTRY.get(verb)
        if not mod:
            # unknown verb, skip gracefully
            continue
        try:
            rule = mod.parse(line)
            rule["verb"] = verb  # ensure verb present
            discount_rules.append(rule)
        except Exception:
            # parsing error -> skip that line
            continue
    return discount_rules


def _normalize_apply_result(result: Union[float, Tuple[float, str], None], default_label: str) -> Tuple[float, str]:
    if result is None:
        return 0.0, default_label
    if isinstance(result, tuple):
        amount, label = result
        return float(amount or 0.0), (label or default_label)
    return float(result or 0.0), default_label


def apply_discounts(cart, products, discount_rules):
    """
    Run PRICE-category verbs and return:
      - total USD discount (float)
      - breakdown list: [{verb, label, amount}, ...]
    """
    discount_total = 0.0
    breakdown: List[Dict[str, Any]] = []

    for rule in discount_rules:
        verb = rule.get("verb")
        mod = REGISTRY.get(verb)
        if not mod:
            continue
        if getattr(mod, "CATEGORY", "price") != "price":
            continue

        label_default = getattr(mod, "LABEL", verb.replace("_", " "))
        amount, label = _normalize_apply_result(mod.apply(cart, products, rule), label_default)

        if amount:
            breakdown.append({"verb": verb, "label": label, "amount": amount})
            discount_total += amount

    return discount_total, breakdown


def simulate_cart(cart, products, discount_rules=[]):
    total_price = 0.0
    total_cogs = 0.0
    store_shipping = 0.0
    cogs_shipping_total = 0.0

    # Merchandise + COGS + real shipping accumulation
    for key, qty in cart.items():
        product = products[key]
        total_price += product["price"] * qty
        total_cogs   += product["cogs"] * qty

        per_product_real_ship = 0.0
        if qty >= 1:
            per_product_real_ship += product["real_shipping_first"]
        if qty > 1:
            per_product_real_ship += product["real_shipping_additional"] * (qty - 1)

        cogs_shipping_total += per_product_real_ship
        if product["use_real_shipping"]:
            store_shipping += per_product_real_ship
        else:
            store_shipping += product["store_shipping"]

    original_price = total_price

    # Apply price discounts (only)
    discount_total, discount_breakdown = apply_discounts(cart, products, discount_rules)
    total_price -= discount_total
    order_total = total_price  # merchandise after price discounts

    # Handle shipping verbs (e.g., free_shipping)
    store_shipping_discount = 0.0
    for rule in discount_rules:
        mod = REGISTRY.get(rule.get("verb"))
        if not mod:
            continue
        if getattr(mod, "CATEGORY", "price") != "shipping":
            continue
        if rule["verb"] == "free_shipping":
            if order_total >= float(rule["min_total"]):
                store_shipping_discount = store_shipping
                break

    total_price += (store_shipping - store_shipping_discount)

    # ---- Economics knobs (envs for flexibility) ----
    EXCHANGE_RATE = float(os.getenv("EXCHANGE_RATE", "1.44"))  # USD -> CAD
    COGS_TAX_RATE = float(os.getenv("COGS_TAX_RATE", "0.07"))

    FEE_PCT_1 = float(os.getenv("FEE_PCT_1", "0.035"))
    FEE_FIXED = float(os.getenv("FEE_FIXED", "0.30"))
    FEE_PCT_2 = float(os.getenv("FEE_PCT_2", "0.02"))
    # -----------------------------------------------

    order_value_cad = total_price * EXCHANGE_RATE
    store_fee = (order_value_cad * FEE_PCT_1 + FEE_FIXED) + (
        (order_value_cad - (order_value_cad * FEE_PCT_1 + FEE_FIXED)) * FEE_PCT_2
    )
    store_payout = order_value_cad - store_fee

    all_tax = (total_cogs + cogs_shipping_total) * COGS_TAX_RATE
    profit = total_price - total_cogs - cogs_shipping_total - all_tax
    cogs_total_cad = (total_cogs + cogs_shipping_total + all_tax) * EXCHANGE_RATE
    total_expenses_cad = cogs_total_cad + store_fee
    profit_cad = order_value_cad - total_expenses_cad

    return {
        "original_price": original_price,
        "order_total": order_total,
        "customer_total": total_price,
        "total_cogs": total_cogs,
        "real_shipping_total": cogs_shipping_total,
        "cogs_tax": all_tax,
        "order_value_cad": order_value_cad,
        "store_fee_cad": store_fee,
        "store_payout_cad": store_payout,
        "cogs_total_cad": cogs_total_cad,
        "total_expenses_cad": total_expenses_cad,
        "profit": profit,
        "discount_total": discount_total,
        "discount_breakdown": discount_breakdown,                 # NEW
        "total_discount_incl_shipping": discount_total + store_shipping_discount,  # NEW
        "profit_cad": profit_cad,
        "exchange_rate": EXCHANGE_RATE,
        "store_shipping_total": store_shipping,
        "store_shipping_discount": store_shipping_discount,
    }

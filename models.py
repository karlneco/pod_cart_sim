def apply_discounts(cart, products, discount_rules):
    discount_total = 0

    for rule in discount_rules:
        rule_type = rule.get("type")

        if rule_type == "percentage_off_total":
            # Blanket discount on all items (based on product prices only, not shipping)
            subtotal = sum(products[k]["price"] * q for k, q in cart.items())
            discount_total += subtotal * (rule["value"] / 100)

        elif rule_type == "category_discount":
            for key, qty in cart.items():
                if products[key]["type"] == rule["product_type"]:
                    discount_total += products[key]["price"] * qty * (rule["percent"] / 100)

        elif rule_type == "order_minimum_discount":
            subtotal = sum(products[k]["price"] * q for k, q in cart.items())
            if subtotal >= rule["min_total"]:
                discount_total += subtotal * (rule["percent"] / 100)
        elif rule_type == "buy_x_get_y_free":
            buy_qty = rule["buy_qty"]
            free_qty = rule["free_qty"]
            product_type = rule.get("product_type")

            eligible_items = []

            for key, qty in cart.items():
                product = products[key]
                if product_type is None or product["type"] == product_type:
                    eligible_items.extend([product["price"]] * qty)

            eligible_items.sort()  # cheapest items first
            total_items = len(eligible_items)
            group_size = buy_qty + free_qty
            num_free = (total_items // group_size) * free_qty

            discount_total += sum(eligible_items[:num_free])

        elif rule_type == "buy_any_get_one_discounted":
            buy_qty = rule["buy_qty"]
            percent = rule["percent"]

            all_items = []
            for key, qty in cart.items():
                price = products[key]["price"]
                all_items.extend([price] * qty)

            all_items.sort()  # cheapest items first
            groups = len(all_items) // (buy_qty)
            discounted_items = groups
            discount_total += sum(all_items[:discounted_items]) * (percent / 100)

        elif rule_type == "type_tier_discount":
            product_type = rule["product_type"]
            thresholds = rule["thresholds"]

            total_qty = 0
            total_price = 0

            for key, qty in cart.items():
                if products[key]["type"] == product_type:
                    total_qty += qty
                    total_price += products[key]["price"] * qty

            applicable_discount = 0
            for threshold, amount in thresholds.items():
                if total_qty >= threshold:
                    applicable_discount = max(applicable_discount, amount)

            discount_total += applicable_discount * total_qty

        elif rule_type == "buy_type_get_type_discount":
            from_type = rule["from_type"]
            to_type = rule["to_type"]
            percent = rule["percent"]

            from_count = 0
            to_items = []

            for key, qty in cart.items():
                product = products[key]
                if product["type"] == from_type:
                    from_count += qty
                elif product["type"] == to_type:
                    to_items.extend([product["price"]] * qty)

            eligible = min(from_count, len(to_items))
            to_items.sort()  # Discount cheapest first
            discount_total += sum(to_items[:eligible]) * (percent / 100)
    return discount_total

def parse_discount_grammar(command_text):
    discount_rules = []
    lines = command_text.strip().splitlines()
    for line in lines:
        line = line.strip()

        if line.startswith("whole_order:"):
            try:
                value = float(line.split(":", 1)[1].strip())
                discount_rules.append({
                    "type": "percentage_off_total",
                    "value": value
                })
            except ValueError:
                continue

        elif line.startswith("type_discount:"):
            try:
                _, rest = line.split(":", 1)
                product_type, percent = rest.split("=")
                discount_rules.append({
                    "type": "category_discount",
                    "product_type": product_type.strip(),
                    "percent": float(percent.strip())
                })
            except ValueError:
                continue

        elif line.startswith("min_total:"):
            try:
                _, rest = line.split(":", 1)
                min_total, percent = rest.split("=")
                discount_rules.append({
                    "type": "order_minimum_discount",
                    "min_total": float(min_total.strip()),
                    "percent": float(percent.strip())
                })
            except ValueError:
                continue

        elif line.startswith("free_shipping:"):
            try:
                value = float(line.split(":", 1)[1].strip())
                discount_rules.append({
                    "type": "free_shipping_over",
                    "min_total": value
                })
            except ValueError:
                continue
        elif line.startswith("bogo:"):
            try:
                _, rest = line.split(":", 1)
                parts = rest.split(",")
                if len(parts) == 3:
                    product_type = parts[0].strip()
                    buy_qty = int(parts[1].strip())
                    free_qty = int(parts[2].strip())
                    discount_rules.append({
                        "type": "buy_x_get_y_free",
                        "product_type": product_type if product_type else None,
                        "buy_qty": buy_qty,
                        "free_qty": free_qty
                    })
            except ValueError:
                continue
        elif line.startswith("buy_x_get_1off:"):
            try:
                _, rest = line.split(":", 1)
                parts = rest.split(",")
                if len(parts) == 2:
                    buy_qty = int(parts[0].strip())
                    percent = float(parts[1].strip())
                    discount_rules.append({
                        "type": "buy_any_get_one_discounted",
                        "buy_qty": buy_qty,
                        "percent": percent
                    })
            except ValueError:
                continue
        elif line.startswith("type_tier_discount:"):
            try:
                _, rest = line.split(":", 1)
                product_type, *tiers = rest.split(",")

                thresholds = {}
                for t in tiers:
                    if "=" in t:
                        count, amount = t.strip().split("=")
                        thresholds[int(count.strip())] = float(amount.strip())

                discount_rules.append({
                    "type": "type_tier_discount",
                    "product_type": product_type.strip(),
                    "thresholds": thresholds
                })
            except ValueError:
                continue
        elif line.startswith("buy_type_get_type_discount:"):
            try:
                _, rest = line.split(":", 1)
                from_type, to_type, percent = rest.split(",")
                discount_rules.append({
                    "type": "buy_type_get_type_discount",
                    "from_type": from_type.strip(),
                    "to_type": to_type.strip(),
                    "percent": float(percent.strip())
                })
            except ValueError:
                continue
    return discount_rules

def simulate_cart(cart, products, discount_rules=[]):
    total_price = 0
    total_cogs = 0
    store_shipping = 0
    cogs_shipping_total = 0

    for key, qty in cart.items():
        product = products[key]
        total_price += product["price"] * qty
        total_cogs += product["cogs"] * qty

        # calculate COGS shipping
        if qty >= 1:
            cogs_shipping_total += product["real_shipping_first"]
        if qty > 1:
            cogs_shipping_total += product["real_shipping_additional"] * (qty - 1)

        if product["use_real_shipping"]:
            store_shipping += cogs_shipping_total
        else:
            store_shipping += product["store_shipping"]


    original_price = total_price
    discount_total = apply_discounts(cart, products, discount_rules)
    total_price -= discount_total
    order_total = total_price

    store_shipping_discount = 0
    for rule in discount_rules:
        if rule.get("type") == "free_shipping_over":
            if total_price >= rule["min_total"]:
                store_shipping_discount = store_shipping
                break
    total_price += (store_shipping - store_shipping_discount)

    # Currency conversion
    exchange_rate = 1.44  # USD to CAD
    order_value_cad = total_price * exchange_rate

    # Store fee formula
    store_fee = (order_value_cad * 0.035 + 0.3) + ((order_value_cad - (order_value_cad * 0.035 + 0.3)) * 0.02)
    store_payout = order_value_cad - store_fee

    # Tax on COGS and shipping only
    all_tax = (total_cogs + cogs_shipping_total) * 0.07  # 7% tax on COGS and shipping - in USD
    profit = total_price - total_cogs - cogs_shipping_total - all_tax
    cogs_total_cad = (total_cogs + cogs_shipping_total + all_tax) * exchange_rate
    profit_cad = store_payout - cogs_total_cad
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
        "profit": profit,
        "discount_total": discount_total,
        "profit_cad": profit_cad,
        "exchange_rate": exchange_rate,
        "store_shipping_total": store_shipping,
        "store_shipping_discount": store_shipping_discount,
    }


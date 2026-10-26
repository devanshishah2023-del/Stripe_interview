# Shipping Cost Calculator Part 1
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")                                   # CHANGED: .get
    if country not in shipping_cost:                                 # NEW: unknown country
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = product_info["cost"]
    total = 0
    for item in order.get("items", []):                              # CHANGED: .get
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                  # NEW: unknown product
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:            # NEW: bad quantity
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        total += quantity * cost_map[product]

    return total


# Shipping Cost Calculator Part 2
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")
    if country not in shipping_cost:                                 # NEW
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = sorted(                  # CHANGED: sort tiers
            product_info["costs"], key=lambda t: t["minQuantity"]
        )
    total = 0
    for item in order.get("items", []):
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                  # NEW
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:            # NEW
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        covered = 0                                                  # CHANGED: bookmark, replaces 'remaining'
        for tier in cost_map[product]:
            if covered >= quantity:                                  # CHANGED
                break
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            if max_qty is None:
                upper = quantity                                     # CHANGED
            else:
                upper = min(quantity, max_qty)                       # CHANGED: replaces max_qty - min_qty
            tier_units = upper - covered                             # CHANGED
            if tier_units <= 0:                                      # NEW: skip empty tier
                continue

            total += tier_units * cost
            covered = upper                                          # CHANGED: move bookmark

        if covered < quantity:                                       # NEW: tiers ran out
            raise ValueError(f"Tiers don't cover {quantity} units of {product}")

    return total


# Shipping Cost Calculator Part 3
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")
    if country not in shipping_cost:                                 # NEW
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = sorted(                  # CHANGED: sort tiers
            product_info["costs"], key=lambda t: t["minQuantity"]
        )
    total = 0
    for item in order.get("items", []):
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                  # NEW
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:            # NEW
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        covered = 0                                                  # CHANGED
        for tier in cost_map[product]:
            if covered >= quantity:                                  # CHANGED
                break
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            pricing_type = tier.get("type", "incremental")           # CHANGED: default if missing
            if max_qty is None:
                upper = quantity                                     # CHANGED
            else:
                upper = min(quantity, max_qty)                       # CHANGED
            tier_units = upper - covered                             # CHANGED
            if tier_units <= 0:                                      # NEW: no flat fee for an empty tier
                continue

            if pricing_type == "fixed":
                total += cost
            else:  # incremental
                total += tier_units * cost

            covered = upper                                          # CHANGED

        if covered < quantity:                                       # NEW
            raise ValueError(f"Tiers don't cover {quantity} units of {product}")

    return total
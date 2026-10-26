# Shipping Cost Calculator Part 1
def calculate_shipping_cost(order, shipping_cost):
    country = order["country"]
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = product_info["cost"]
    total = 0
    for item in order["items"]:                     
        product = item["product"]
        quantity = item["quantity"]
        total += quantity * cost_map[product]

    return total


# Shipping Cost Calculator Part 2
def calculate_shipping_cost(order, shipping_cost):
    country = order["country"]
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = product_info["costs"]   
    total = 0
    for item in order["items"]:                      
        product = item["product"]
        quantity = item["quantity"]
        remaining = quantity
        for tier in cost_map[product]:
            if remaining <= 0:
                break
            min_qty = tier["minQuantity"]
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            if max_qty is None:
                tier_units = remaining
            else:
                tier_capacity = max_qty - min_qty
                tier_units = min(remaining, tier_capacity)

            total += tier_units * cost
            remaining -= tier_units

    return total


# Shipping Cost Calculator Part 3
def calculate_shipping_cost(order, shipping_cost):
    country = order["country"]
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = product_info["costs"]  
    total = 0
    for item in order["items"]:                     
        product = item["product"]
        quantity = item["quantity"]
        remaining = quantity
        for tier in cost_map[product]:
            if remaining <= 0:
                break
            min_qty = tier["minQuantity"]
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            pricing_type = tier["type"]              
            if max_qty is None:
                tier_units = remaining
            else:
                tier_capacity = max_qty - min_qty
                tier_units = min(remaining, tier_capacity)

            if pricing_type == "fixed":
                total += cost
            else:  # incremental
                total += tier_units * cost

            remaining -= tier_units

    return total                                   
# Shipping Cost Calculator Part 1
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")                                  
    if country not in shipping_cost:                                 
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = product_info["cost"]
    total = 0
    for item in order.get("items", []):                              
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                 
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:           
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        total += quantity * cost_map[product]

    return total


# Shipping Cost Calculator Part 2
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")
    if country not in shipping_cost:                                 
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = sorted(                  
            product_info["costs"], key=lambda t: t["minQuantity"]
        )
    total = 0
    for item in order.get("items", []):
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                  
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:           
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        covered = 0                                                  
        for tier in cost_map[product]:
            if covered >= quantity:                                  
                break
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            if max_qty is None:
                upper = quantity                                    
            else:
                upper = min(quantity, max_qty)                      
            tier_units = upper - covered                            
            if tier_units <= 0:                                      
                continue

            total += tier_units * cost
            covered = upper                                         

        if covered < quantity:                                      
            raise ValueError(f"Tiers don't cover {quantity} units of {product}")

    return total


# Shipping Cost Calculator Part 3
def calculate_shipping_cost(order, shipping_cost):
    country = order.get("country")
    if country not in shipping_cost:                                 
        raise ValueError(f"No shipping rules for country: {country}")
    cost_map = {}
    for product_info in shipping_cost[country]:
        cost_map[product_info["product"]] = sorted(                  
            product_info["costs"], key=lambda t: t["minQuantity"]
        )
    total = 0
    for item in order.get("items", []):
        product = item["product"]
        quantity = item["quantity"]
        if product not in cost_map:                                 
            raise ValueError(f"No shipping rule for product: {product}")
        if not isinstance(quantity, int) or quantity < 0:           
            raise ValueError(f"Invalid quantity for {product}: {quantity}")
        covered = 0                                                 
        for tier in cost_map[product]:
            if covered >= quantity:                                 
                break
            max_qty = tier["maxQuantity"]
            cost = tier["cost"]
            pricing_type = tier.get("type", "incremental")          
            if max_qty is None:
                upper = quantity                                     
            else:
                upper = min(quantity, max_qty)                       
            tier_units = upper - covered                             
            if tier_units <= 0:                                      
                continue

            if pricing_type == "fixed":
                total += cost
            else:  
                total += tier_units * cost

            covered = upper                                          

        if covered < quantity:                                       
            raise ValueError(f"Tiers don't cover {quantity} units of {product}")

    return total
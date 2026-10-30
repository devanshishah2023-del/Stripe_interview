def calculate_fraud_scores(transactions, rules, merchants):

    # STEP 1: starting scores
    score = {}
    for m in merchants:
        name, start = m.split(",")
        score[name.strip()] = int(start)

    # STEP 2: read every payment together with its own rule
    payments = []
    for i in range(len(transactions)):
        merchant, amount, customer, hour = transactions[i].split(",")
        min_amount, mult, add, penalty = rules[i].split(",")
        payments.append({
            "merchant": merchant.strip(),
            "customer": customer.strip(),
            "amount": int(amount),
            "hour": int(hour),
            "min_amount": int(min_amount),
            "mult": int(mult),
            "add": int(add),
            "penalty": int(penalty),
        })

    # RULE 1: big payment -> multiply
    for p in payments:
        if p["amount"] > p["min_amount"]:
            score[p["merchant"]] *= p["mult"]

    # RULE 2: same customer 3+ times -> add
    groups = {}
    for p in payments:
        key = (p["merchant"], p["customer"])
        if key not in groups:
            groups[key] = []
        groups[key].append(p["add"])

    for (merchant, customer), adds in groups.items():
        if len(adds) >= 3:
            score[merchant] += sum(adds)

    # RULE 3: same customer, same hour, 3+ times -> penalty
    groups = {}
    for p in payments:
        key = (p["merchant"], p["customer"], p["hour"])
        if key not in groups:
            groups[key] = []
        groups[key].append(p["penalty"])

    for (merchant, customer, hour), penalties in groups.items():
        if len(penalties) >= 3:
            if 12 <= hour <= 17:
                score[merchant] += sum(penalties)
            elif 9 <= hour <= 11 or 18 <= hour <= 21:
                score[merchant] -= sum(penalties)

    # STEP 3: answer sorted by shop name
    result = []
    for name in sorted(score):
        result.append(f"{name},{score[name]}")
    return result

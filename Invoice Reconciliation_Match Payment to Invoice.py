# ==============================================================================
# PART 1: match by the invoice ID written in the memo
# ==============================================================================
def reconcile_part1(payment, invoices):
    # 1. Cut the payment into pieces: "payment-001, 1000, Paying off: inv-123"
    parts = [p.strip() for p in payment.split(",")]
    if len(parts) < 3:
        return "Invalid payment"                 # something is missing
    pay_id = parts[0]                            # "payment-001"
    pay_amount = int(parts[1])                   # 1000
    memo = ", ".join(parts[2:])                  # "Paying off: inv-123" (memo may have commas)

    # 2. Find the invoice ID written after "paying for:" or "paying off:"
    wanted_id = None
    memo_lower = memo.lower()                    # so "Paying" and "PAYING" both work
    for phrase in ["paying for:", "paying off:"]:
        if phrase in memo_lower:
            start = memo_lower.find(phrase) + len(phrase)   # position right after the colon
            words = memo[start:].split()                    # words after the colon
            if words:
                wanted_id = words[0].strip(".,;:!?")        # first word, without punctuation
            break

    # 3. Look for that ID in the invoices
    if wanted_id:
        for line in invoices:
            inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
            if inv_id.lower() == wanted_id.lower():
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    return f"Payment {pay_id} could not be matched to any invoice"


# ==============================================================================
# PART 2: ID match, then exact amount (earliest due date wins)
# ==============================================================================
def reconcile_part2(payment, invoices):
    # 1. Cut the payment into pieces
    parts = [p.strip() for p in payment.split(",")]
    if len(parts) < 3:
        return "Invalid payment"
    pay_id = parts[0]
    pay_amount = int(parts[1])
    memo = ", ".join(parts[2:])

    # 2. Find the invoice ID in the memo
    wanted_id = None
    memo_lower = memo.lower()
    for phrase in ["paying for:", "paying off:"]:
        if phrase in memo_lower:
            start = memo_lower.find(phrase) + len(phrase)
            words = memo[start:].split()
            if words:
                wanted_id = words[0].strip(".,;:!?")
            break

    # 3. Tier 1: ID match
    if wanted_id:
        for line in invoices:
            inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
            if inv_id.lower() == wanted_id.lower():
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    # 4. Tier 2: same amount -> keep the one with the earliest date
    best_id = None
    best_date = None
    for line in invoices:
        inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
        if int(inv_amount) == pay_amount:
            if best_date is None or inv_date < best_date:    # first one, or older one
                best_id = inv_id
                best_date = inv_date
    if best_id:
        return f"Payment {pay_id} paid {pay_amount} for invoice {best_id} due on {best_date}"

    return f"Payment {pay_id} could not be matched to any invoice"


# ==============================================================================
# PART 3: ID match, then exact amount, then close amount (forgiveness)
# ==============================================================================
def reconcile_part3(payment, invoices, forgiveness=0):
    # 1. Cut the payment into pieces
    parts = [p.strip() for p in payment.split(",")]
    if len(parts) < 3:
        return "Invalid payment"
    pay_id = parts[0]
    pay_amount = int(parts[1])
    memo = ", ".join(parts[2:])

    # 2. Find the invoice ID in the memo
    wanted_id = None
    memo_lower = memo.lower()
    for phrase in ["paying for:", "paying off:"]:
        if phrase in memo_lower:
            start = memo_lower.find(phrase) + len(phrase)
            words = memo[start:].split()
            if words:
                wanted_id = words[0].strip(".,;:!?")
            break

    # 3. Tier 1: ID match
    if wanted_id:
        for line in invoices:
            inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
            if inv_id.lower() == wanted_id.lower():
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    # 4. Tier 2: same amount -> earliest date
    best_id = None
    best_date = None
    for line in invoices:
        inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
        if int(inv_amount) == pay_amount:
            if best_date is None or inv_date < best_date:
                best_id = inv_id
                best_date = inv_date
    if best_id:
        return f"Payment {pay_id} paid {pay_amount} for invoice {best_id} due on {best_date}"

    # 5. Tier 3: close amount (within forgiveness) -> earliest date
    best_id = None
    best_date = None
    for line in invoices:
        inv_id, inv_date, inv_amount = [p.strip() for p in line.split(",")]
        difference = abs(int(inv_amount) - pay_amount)       # how far apart the amounts are
        if difference <= forgiveness:                        # <= so the edge counts
            if best_date is None or inv_date < best_date:
                best_id = inv_id
                best_date = inv_date
    if best_id:
        return f"Payment {pay_id} paid {pay_amount} for invoice {best_id} due on {best_date}"

    return f"Payment {pay_id} could not be matched to any invoice"


# ==============================================================================
# SAMPLE RUNS (examples from the question)
# ==============================================================================
if __name__ == "__main__":
    print(reconcile_part1("payment-001, 1000, Paying off: inv-123",
                          ["inv-123, 2024-03-15, 1000", "inv-456, 2024-03-20, 1000", "inv-789, 2024-02-10, 500"]))
    # Payment payment-001 paid 1000 for invoice inv-123 due on 2024-03-15

    print(reconcile_part2("payment-002, 500, Monthly subscription",
                          ["inv-001, 2024-03-22, 1000", "inv-002, 2024-02-05, 500",
                           "inv-003, 2024-03-01, 500", "inv-004, 2024-01-15, 500"]))
    # Payment payment-002 paid 500 for invoice inv-004 due on 2024-01-15

    print(reconcile_part3("payment-003, 98, Customer payment",
                          ["inv-100, 2024-03-15, 100", "inv-200, 2024-02-20, 98", "inv-300, 2024-01-10, 102"], 5))
    # Payment payment-003 paid 98 for invoice inv-200 due on 2024-02-20

    print(reconcile_part3("payment-004, 95, Customer payment",
                          ["inv-100, 2024-03-15, 100", "inv-300, 2024-01-10, 97"], 5))
    # Payment payment-004 paid 95 for invoice inv-300 due on 2024-01-10

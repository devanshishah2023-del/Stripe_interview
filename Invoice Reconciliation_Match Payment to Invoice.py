"""
Payment-Invoice Reconciliation: Parts 1, 2 and 3 in one file.

Payment : "payment-id, amount, memo"   (amount in cents)
Invoice : "invoice-id, YYYY-MM-DD, amount"

Part 1: match by the invoice ID written in the memo
Part 2: Part 1, then exact amount (earliest due date wins)
Part 3: Part 2, then close amount within forgiveness (earliest due date wins)
"""


# ==============================================================================
# PART 1: match by invoice ID
# ==============================================================================

def reconcile_payment_part1(payment, invoices):
    # ---- Step 1: parse the payment ----
    parts = [p.strip() for p in payment.split(",")]    # "id, amount, memo" -> pieces, spaces trimmed
    if len(parts) < 3:                                 # missing data?
        return "Invalid payment"                       # fail cleanly instead of crashing
    pay_id = parts[0]                                  # payment ID
    try:
        pay_amount = int(parts[1])                     # amount in cents, as a number
    except ValueError:                                 # e.g. "abc"
        return "Invalid payment"
    memo = ", ".join(parts[2:])                        # rejoin: memo may contain commas

    # ---- Step 2: parse every invoice once ----
    bills = []                                         # list of (id, date, amount) tuples
    for line in invoices:                              # look at each invoice string
        f = [p.strip() for p in line.split(",")]       # cut at commas, trim spaces
        if len(f) != 3:                                # need exactly id, date, amount
            continue                                   # bad line -> skip, don't crash
        try:
            bills.append((f[0], f[1], int(f[2])))      # store amount as a number
        except ValueError:                             # amount wasn't a number
            continue                                   # skip it

    # ---- Step 3: pull the invoice ID out of the memo ----
    wanted_id = None                                   # no ID found yet
    memo_lower = memo.lower()                          # lowercase copy -> case-insensitive search
    for phrase in ("paying for:", "paying off:"):      # the two phrases we accept
        if phrase in memo_lower:                       # phrase found in the note?
            pos = memo_lower.find(phrase) + len(phrase)  # index just after the colon
            rest = memo[pos:].strip()                  # text after the colon
            if rest:                                   # something actually follows
                wanted_id = rest.split()[0].rstrip(".,;:!?")  # first word only, drop punctuation
            break                                      # stop after the first phrase found

    # ---- Tier 1: ID match (strongest clue) ----
    if wanted_id:                                      # only search if we found an ID
        for inv_id, inv_date, inv_amount in bills:     # linear scan
            if inv_id.lower() == wanted_id.lower():    # compare ignoring case
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    return f"Payment {pay_id} could not be matched to any invoice"   # no tier matched


# ==============================================================================
# PART 2: ID match, then exact amount
# ==============================================================================

def reconcile_payment_part2(payment, invoices):
    # ---- Step 1: parse the payment ----
    parts = [p.strip() for p in payment.split(",")]    # "id, amount, memo" -> pieces, spaces trimmed
    if len(parts) < 3:                                 # missing data?
        return "Invalid payment"                       # fail cleanly instead of crashing
    pay_id = parts[0]                                  # payment ID
    try:
        pay_amount = int(parts[1])                     # amount in cents, as a number
    except ValueError:                                 # e.g. "abc"
        return "Invalid payment"
    memo = ", ".join(parts[2:])                        # rejoin: memo may contain commas

    # ---- Step 2: parse every invoice once ----
    bills = []                                         # list of (id, date, amount) tuples
    for line in invoices:                              # look at each invoice string
        f = [p.strip() for p in line.split(",")]       # cut at commas, trim spaces
        if len(f) != 3:                                # need exactly id, date, amount
            continue                                   # bad line -> skip, don't crash
        try:
            bills.append((f[0], f[1], int(f[2])))      # store amount as a number
        except ValueError:                             # amount wasn't a number
            continue                                   # skip it

    # ---- Step 3: pull the invoice ID out of the memo ----
    wanted_id = None                                   # no ID found yet
    memo_lower = memo.lower()                          # lowercase copy -> case-insensitive search
    for phrase in ("paying for:", "paying off:"):      # the two phrases we accept
        if phrase in memo_lower:                       # phrase found in the note?
            pos = memo_lower.find(phrase) + len(phrase)  # index just after the colon
            rest = memo[pos:].strip()                  # text after the colon
            if rest:                                   # something actually follows
                wanted_id = rest.split()[0].rstrip(".,;:!?")  # first word only, drop punctuation
            break                                      # stop after the first phrase found

    # ---- Tier 1: ID match (strongest clue) ----
    if wanted_id:                                      # only search if we found an ID
        for inv_id, inv_date, inv_amount in bills:     # linear scan
            if inv_id.lower() == wanted_id.lower():    # compare ignoring case
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    # ---- Tier 2: exact amount, earliest due date wins ----
    best = None                                        # best invoice so far (none yet)
    for inv_id, inv_date, inv_amount in bills:
        if inv_amount == pay_amount:                   # amount matches exactly
            if best is None or inv_date < best[1]:     # first match, or older than best
                best = (inv_id, inv_date)              # keep it (YYYY-MM-DD sorts as text)
    if best:                                           # found something -> stop here
        return f"Payment {pay_id} paid {pay_amount} for invoice {best[0]} due on {best[1]}"

    return f"Payment {pay_id} could not be matched to any invoice"   # no tier matched


# ==============================================================================
# PART 3: ID match, then exact amount, then close amount
# ==============================================================================

def reconcile_payment_part3(payment, invoices, forgiveness=0):   # default 0 = fuzzy off
    # ---- Step 1: parse the payment ----
    parts = [p.strip() for p in payment.split(",")]    # "id, amount, memo" -> pieces, spaces trimmed
    if len(parts) < 3:                                 # missing data?
        return "Invalid payment"                       # fail cleanly instead of crashing
    pay_id = parts[0]                                  # payment ID
    try:
        pay_amount = int(parts[1])                     # amount in cents, as a number
    except ValueError:                                 # e.g. "abc"
        return "Invalid payment"
    memo = ", ".join(parts[2:])                        # rejoin: memo may contain commas

    # ---- Step 2: parse every invoice once ----
    bills = []                                         # list of (id, date, amount) tuples
    for line in invoices:                              # look at each invoice string
        f = [p.strip() for p in line.split(",")]       # cut at commas, trim spaces
        if len(f) != 3:                                # need exactly id, date, amount
            continue                                   # bad line -> skip, don't crash
        try:
            bills.append((f[0], f[1], int(f[2])))      # store amount as a number
        except ValueError:                             # amount wasn't a number
            continue                                   # skip it

    # ---- Step 3: pull the invoice ID out of the memo ----
    wanted_id = None                                   # no ID found yet
    memo_lower = memo.lower()                          # lowercase copy -> case-insensitive search
    for phrase in ("paying for:", "paying off:"):      # the two phrases we accept
        if phrase in memo_lower:                       # phrase found in the note?
            pos = memo_lower.find(phrase) + len(phrase)  # index just after the colon
            rest = memo[pos:].strip()                  # text after the colon
            if rest:                                   # something actually follows
                wanted_id = rest.split()[0].rstrip(".,;:!?")  # first word only, drop punctuation
            break                                      # stop after the first phrase found

    # ---- Tier 1: ID match (strongest clue) ----
    if wanted_id:                                      # only search if we found an ID
        for inv_id, inv_date, inv_amount in bills:     # linear scan
            if inv_id.lower() == wanted_id.lower():    # compare ignoring case
                return f"Payment {pay_id} paid {pay_amount} for invoice {inv_id} due on {inv_date}"

    # ---- Tier 2: exact amount, earliest due date wins ----
    best = None                                        # best invoice so far (none yet)
    for inv_id, inv_date, inv_amount in bills:
        if inv_amount == pay_amount:                   # amount matches exactly
            if best is None or inv_date < best[1]:     # first match, or older than best
                best = (inv_id, inv_date)              # keep it (YYYY-MM-DD sorts as text)
    if best:                                           # found something -> stop here
        return f"Payment {pay_id} paid {pay_amount} for invoice {best[0]} due on {best[1]}"

    # ---- Tier 3: close amount, earliest due date wins ----
    best = None                                        # reset for this tier
    for inv_id, inv_date, inv_amount in bills:
        if abs(inv_amount - pay_amount) <= forgiveness:  # distance within range (edges count)
            if best is None or inv_date < best[1]:     # same "keep the oldest" logic
                best = (inv_id, inv_date)
    if best:
        return f"Payment {pay_id} paid {pay_amount} for invoice {best[0]} due on {best[1]}"

    return f"Payment {pay_id} could not be matched to any invoice"   # no tier matched


# ==============================================================================
# TESTS (run: python3 reconciliation_all_parts.py)
# ==============================================================================

if __name__ == "__main__":
    # ---- Part 1 ----
    inv1 = ["inv-123, 2024-03-15, 1000", "inv-456, 2024-03-20, 1000", "inv-789, 2024-02-10, 500"]
    assert reconcile_payment_part1("payment-001, 1000, Paying off: inv-123", inv1) == \
        "Payment payment-001 paid 1000 for invoice inv-123 due on 2024-03-15"
    assert "inv-789" in reconcile_payment_part1("p, 500, PAYING FOR: inv-789", inv1)            # phrase in caps
    assert "inv-123" in reconcile_payment_part1("p, 1, Paying for: INV-123", inv1)              # ID in caps
    assert "inv-456" in reconcile_payment_part1("p, 1, Thanks, paying for: inv-456, cheers", inv1)  # extra text
    assert "inv-123" in reconcile_payment_part1("p,1,Paying for:inv-123", inv1)                 # no spaces
    assert "could not be matched" in reconcile_payment_part1("p, 1, Paying for: inv-999", inv1)  # ID not in list
    assert reconcile_payment_part1("p, 1000", inv1) == "Invalid payment"                        # missing data
    assert reconcile_payment_part1("p, abc, hi", inv1) == "Invalid payment"                     # bad amount
    print("Part 1: all tests passed")

    # ---- Part 2 ----
    inv2 = ["inv-001, 2024-03-22, 1000", "inv-002, 2024-02-05, 500",
            "inv-003, 2024-03-01, 500", "inv-004, 2024-01-15, 500"]
    assert reconcile_payment_part2("payment-002, 500, Monthly subscription", inv2) == \
        "Payment payment-002 paid 500 for invoice inv-004 due on 2024-01-15"
    assert "inv-001" in reconcile_payment_part2("p, 500, Paying for: inv-001", inv2)    # ID beats amount
    assert "inv-004" in reconcile_payment_part2("p, 500, Paying for: inv-999", inv2)    # bad ID -> amount
    assert "could not be matched" in reconcile_payment_part2("p, 777, Payment", inv2)   # no amount match
    print("Part 2: all tests passed")

    # ---- Part 3 ----
    assert reconcile_payment_part3("payment-003, 98, Customer payment",
                                   ["inv-100, 2024-03-15, 100", "inv-200, 2024-02-20, 98",
                                    "inv-300, 2024-01-10, 102"], 5) == \
        "Payment payment-003 paid 98 for invoice inv-200 due on 2024-02-20"           # exact beats close
    assert reconcile_payment_part3("payment-004, 95, Customer payment",
                                   ["inv-100, 2024-03-15, 100", "inv-300, 2024-01-10, 97"], 5) == \
        "Payment payment-004 paid 95 for invoice inv-300 due on 2024-01-10"           # older close wins
    assert "inv-100" in reconcile_payment_part3("p, 999, Paying for: inv-100",
                                                ["inv-100, 2024-01-01, 1000", "inv-200, 2024-01-01, 999"], 5)
    assert "inv-100" in reconcile_payment_part3("p, 100, Payment",
                                                ["inv-100, 2024-03-15, 100", "inv-200, 2024-01-10, 98"], 5)
    assert "inv-1" in reconcile_payment_part3("p, 95, x", ["inv-1, 2024-01-01, 100"], 5)               # edge counts
    assert "could not be matched" in reconcile_payment_part3("p, 94, x", ["inv-1, 2024-01-01, 100"], 5)  # past edge
    assert "could not be matched" in reconcile_payment_part3("p, 99, x", ["inv-1, 2024-01-01, 100"])     # no forgiveness
    print("Part 3: all tests passed")

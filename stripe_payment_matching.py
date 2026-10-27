"""
Stripe: Payment Invoice Matching (simple version)

payments: [{'id': '1', 'amount': 100.0, 'date': '2023-01-01'}, {'amount': 150.0, ...}, ...]
invoices: [{'id': '1', 'amount': 100.0, 'date': '2023-01-01'}, ...]
A payment's 'id' (if it has one) is the invoice it is paying.
Each invoice can be paid only once. Returns one result per payment.
"""


# ==============================================================================
# PART 1: match by id only
# ==============================================================================

def match_payments_part1(payments, invoices):
    paid = set()          # ids of bills already paid
    results = []

    for pay in payments:
        found = None

        # Rule 1: same id
        for inv in invoices:
            if inv["id"] not in paid and inv["id"] == pay.get("id"):
                found = inv
                break

        # Save the answer
        if found:
            paid.add(found["id"])
            results.append(found["id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# PART 2: match by id, then by same amount (oldest first)
# ==============================================================================

def match_payments_part2(payments, invoices):
    # Step 1: put the bills in date order, oldest first
    invoices = sorted(invoices, key=lambda inv: inv["date"])

    paid = set()          # ids of bills already paid
    results = []

    for pay in payments:
        found = None

        # Rule 1: same id
        for inv in invoices:
            if inv["id"] not in paid and inv["id"] == pay.get("id"):
                found = inv
                break

        # Rule 2: same amount (list is oldest-first, so first hit = oldest)
        if found is None:
            for inv in invoices:
                if inv["id"] not in paid and inv["amount"] == pay["amount"]:
                    found = inv
                    break

        # Save the answer
        if found:
            paid.add(found["id"])
            results.append(found["id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# PART 3: match by id, then same amount, then close amount (oldest first)
# ==============================================================================

def match_payments_part3(payments, invoices, forgiveness=0):
    # Step 1: put the bills in date order, oldest first
    invoices = sorted(invoices, key=lambda inv: inv["date"])

    paid = set()          # ids of bills already paid
    results = []

    for pay in payments:
        found = None

        # Rule 1: same id
        for inv in invoices:
            if inv["id"] not in paid and inv["id"] == pay.get("id"):
                found = inv
                break

        # Rule 2: same amount (list is oldest-first, so first hit = oldest)
        if found is None:
            for inv in invoices:
                if inv["id"] not in paid and inv["amount"] == pay["amount"]:
                    found = inv
                    break

        # Rule 3: close amount
        if found is None:
            for inv in invoices:
                if inv["id"] not in paid and abs(inv["amount"] - pay["amount"]) <= forgiveness:
                    found = inv
                    break

        # Save the answer
        if found:
            paid.add(found["id"])
            results.append(found["id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# TESTS (run: python3 payment_matching_simple.py)
# ==============================================================================

if __name__ == "__main__":
    # example from the question
    payments = [{"id": "1", "amount": 100.0, "date": "2023-01-01"},
                {"amount": 150.0, "date": "2023-01-02"}]
    invoices = [{"id": "1", "amount": 100.0, "date": "2023-01-01"},
                {"id": "2", "amount": 150.0, "date": "2023-01-02"}]

    # ---- Part 1 ----
    print("Part 1:", match_payments_part1(payments, invoices))
    assert match_payments_part1(payments, invoices) == ["1", "unmatched"]   # 2nd payment has no id

    # ---- Part 2 ----
    print("Part 2:", match_payments_part2(payments, invoices))
    assert match_payments_part2(payments, invoices) == ["1", "2"]
    bills = [{"id": "A", "amount": 50, "date": "2023-03-01"},
             {"id": "B", "amount": 50, "date": "2023-01-01"}]
    assert match_payments_part2([{"amount": 50}], bills) == ["B"]                      # oldest wins
    assert match_payments_part2([{"amount": 50}] * 3, bills) == ["B", "A", "unmatched"]  # each bill used once

    # ---- Part 3 (the dry run from the explanation) ----
    bills = [{"id": "A", "amount": 50, "date": "2023-03-01"},
             {"id": "B", "amount": 50, "date": "2023-01-01"},
             {"id": "C", "amount": 98, "date": "2023-02-01"}]
    pays = [{"id": "A", "amount": 10}, {"amount": 50}, {"amount": 50}, {"amount": 100}]
    print("Part 3:", match_payments_part3(pays, bills, forgiveness=5))
    assert match_payments_part3(pays, bills, forgiveness=5) == ["A", "B", "unmatched", "C"]
    # exact beats an older close match
    bills = [{"id": "X", "amount": 100, "date": "2023-05-01"},
             {"id": "Y", "amount": 98, "date": "2023-01-01"}]
    assert match_payments_part3([{"amount": 100}], bills, forgiveness=5) == ["X"]
    # edge: difference exactly = forgiveness counts
    assert match_payments_part3([{"amount": 95}], [{"id": "Z", "amount": 100, "date": "2023-01-01"}], 5) == ["Z"]
    assert match_payments_part3([{"amount": 94}], [{"id": "Z", "amount": 100, "date": "2023-01-01"}], 5) == ["unmatched"]

    print("all tests passed")

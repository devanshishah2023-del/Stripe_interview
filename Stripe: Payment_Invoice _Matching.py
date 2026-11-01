"""
Stripe - Invoice / Payment Reconciliation (phone-screen variant, 3 parts)

payment : {"reference": "INV-1", "amount": 100.00}     (reference is optional)
invoice : {"invoice_id": "INV-1", "amount": 100.00, "due_date": "2023-01-01"}

Each invoice can be settled only once.
Each function returns one result per payment: the matched invoice_id, or "unmatched".
Amounts are compared in whole cents so decimals like 1.10 - 0.90 work exactly.
"""


# ==============================================================================
# PART 1: match by exact invoice_id == payment reference
# ==============================================================================
def match_part1(payments, invoices):
    paid = set()                                    # invoice_ids already settled
    results = []

    for pay in payments:
        found = None

        # Rule 1: invoice_id equals the payment's reference
        for inv in invoices:
            if inv["invoice_id"] not in paid and inv["invoice_id"] == pay.get("reference"):
                found = inv
                break

        if found:
            paid.add(found["invoice_id"])
            results.append(found["invoice_id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# PART 2: id match, else exact amount (earliest due date first)
# ==============================================================================
def match_part2(payments, invoices):
    invoices = sorted(invoices, key=lambda inv: inv["due_date"])   # oldest first
    paid = set()
    results = []

    for pay in payments:
        found = None
        pay_cents = round(pay["amount"] * 100)

        # Rule 1: id match (wins even if the amount is different)
        for inv in invoices:
            if inv["invoice_id"] not in paid and inv["invoice_id"] == pay.get("reference"):
                found = inv
                break

        # Rule 2: exact amount; list is oldest-first, so first hit = earliest
        if found is None:
            for inv in invoices:
                if inv["invoice_id"] not in paid and round(inv["amount"] * 100) == pay_cents:
                    found = inv
                    break

        if found:
            paid.add(found["invoice_id"])
            results.append(found["invoice_id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# PART 3: id match, else exact amount, else fuzzy amount within forgiveness
# ==============================================================================
def match_part3(payments, invoices, forgiveness=0):
    invoices = sorted(invoices, key=lambda inv: inv["due_date"])   # oldest first
    limit_cents = round(forgiveness * 100)
    paid = set()
    results = []

    for pay in payments:
        found = None
        pay_cents = round(pay["amount"] * 100)

        # Tier 1: id match - highest priority, wins even if the amount is wrong
        for inv in invoices:
            if inv["invoice_id"] not in paid and inv["invoice_id"] == pay.get("reference"):
                found = inv
                break

        # Tier 2: exact amount - always beats a fuzzy match, even an older one
        if found is None:
            for inv in invoices:
                if inv["invoice_id"] not in paid and round(inv["amount"] * 100) == pay_cents:
                    found = inv
                    break

        # Tier 3: fuzzy amount - only if forgiveness > 0; inclusive range; earliest first
        if found is None and limit_cents > 0:
            for inv in invoices:
                inv_cents = round(inv["amount"] * 100)
                if (inv["invoice_id"] not in paid
                        and inv_cents != pay_cents                       # exact belongs to tier 2
                        and abs(inv_cents - pay_cents) <= limit_cents):  # inclusive boundary
                    found = inv
                    break

        if found:
            paid.add(found["invoice_id"])
            results.append(found["invoice_id"])
        else:
            results.append("unmatched")

    return results


# ==============================================================================
# TESTS  (run: python3 invoice_reconciliation.py)
# ==============================================================================
def run_tests():
    tests = []

    def check(name, got, expected):
        ok = got == expected
        tests.append((name, ok, got, expected))
        print(("PASS" if ok else "FAIL"), "|", name, "->", got)

    def inv(i, amount, date):
        return {"invoice_id": i, "amount": amount, "due_date": date}

    # ---------- Part 1 ----------
    invs = [inv("INV-1", 100.0, "2023-01-01"), inv("INV-2", 150.0, "2023-01-02")]
    check("P1: reference matches invoice_id",
          match_part1([{"reference": "INV-1", "amount": 100.0}], invs), ["INV-1"])
    check("P1: no reference -> unmatched",
          match_part1([{"amount": 150.0}], invs), ["unmatched"])
    check("P1: unknown reference -> unmatched",
          match_part1([{"reference": "INV-9", "amount": 5.0}], invs), ["unmatched"])
    check("P1: invoice settled only once",
          match_part1([{"reference": "INV-1", "amount": 100.0}] * 2, invs), ["INV-1", "unmatched"])

    # ---------- Part 2 ----------
    check("P2: falls back to amount",
          match_part2([{"amount": 150.0}], invs), ["INV-2"])
    same = [inv("A", 50.0, "2023-03-01"), inv("B", 50.0, "2023-01-01")]
    check("P2: equal amounts -> earliest date",
          match_part2([{"amount": 50.0}], same), ["B"])
    check("P2: each invoice used once",
          match_part2([{"amount": 50.0}] * 3, same), ["B", "A", "unmatched"])
    check("P2: id beats an older same-amount invoice",
          match_part2([{"reference": "A", "amount": 50.0}], same), ["A"])

    # ---------- Part 3 ----------
    check("P3: id wins even if amount is wrong",
          match_part3([{"reference": "A", "amount": 1.0}],
                      [inv("A", 100.0, "2023-05-01"), inv("B", 1.0, "2023-01-01")], 5), ["A"])
    check("P3: exact beats an OLDER fuzzy match",
          match_part3([{"amount": 100.0}],
                      [inv("X", 100.0, "2023-05-01"), inv("Y", 98.0, "2023-01-01")], 5), ["X"])
    check("P3: bank fee - owes 100, 98 arrives, forgiveness 2",
          match_part3([{"amount": 98.0}], [inv("Z", 100.0, "2023-01-01")], 2), ["Z"])
    check("P3: forgiveness 0 -> no fuzzy",
          match_part3([{"amount": 98.0}], [inv("Z", 100.0, "2023-01-01")], 0), ["unmatched"])
    check("P3: boundary below is inclusive (95, f=5)",
          match_part3([{"amount": 95.0}], [inv("Z", 100.0, "2023-01-01")], 5), ["Z"])
    check("P3: boundary above is inclusive (105, f=5)",
          match_part3([{"amount": 105.0}], [inv("Z", 100.0, "2023-01-01")], 5), ["Z"])
    check("P3: just outside the range (94, f=5)",
          match_part3([{"amount": 94.0}], [inv("Z", 100.0, "2023-01-01")], 5), ["unmatched"])
    check("P3: decimal boundary (1.10 vs 0.90, f=0.20)",
          match_part3([{"amount": 1.10}], [inv("Z", 0.90, "2023-01-01")], 0.20), ["Z"])
    check("P3: fuzzy tier picks earliest date",
          match_part3([{"amount": 100.0}],
                      [inv("NEW", 99.0, "2023-06-01"), inv("OLD", 97.0, "2023-01-01")], 5), ["OLD"])
    full_invs = [inv("A", 50.0, "2023-03-01"), inv("B", 50.0, "2023-01-01"), inv("C", 98.0, "2023-02-01")]
    full_pays = [{"reference": "A", "amount": 10.0}, {"amount": 50.0}, {"amount": 50.0}, {"amount": 100.0}]
    check("P3: full dry-run example",
          match_part3(full_pays, full_invs, 5), ["A", "B", "unmatched", "C"])

    passed = sum(1 for t in tests if t[1])
    print(f"\n{passed}/{len(tests)} tests passed")
    return tests


if __name__ == "__main__":
    run_tests()

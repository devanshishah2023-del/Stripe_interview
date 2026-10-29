
"""
Stripe - Transaction Fee Calculator
Part 1, Part 2 and Part 3 are each complete on their own.
You can copy any single part into an interview editor and it will work.

Run this file to test all parts:
    python3 transaction_fees_all_parts.py
"""

import math


# ==========================================================
# PART 1: Fee depends only on the payment method
# ==========================================================
def part1(csv_data):
    # Price list: method -> (percent, fixed cents)
    fees = {
        "card": (0.029, 30),          # 2.9% + 30 cents
        "klarna": (0.035, 50),        # 3.5% + 50 cents
        "bank_transfer": (0.008, 0),  # 0.8%
    }

    # Cut the text into lines
    # splitlines() handles both "\n" and Windows "\r\n" line endings
    lines = csv_data.strip().splitlines()

    # Empty input: return just the output header
    if not lines:
        return "id,transaction_type,payment_provider,fee"

    # First line = column names. Find each column's position by name.
    header = lines[0].split(",")
    col = {name: i for i, name in enumerate(header)}

    result = ["id,transaction_type,payment_provider,fee"]

    # Go through every payment (skip the header line)
    for line in lines[1:]:
        # Skip empty lines
        if not line.strip():
            continue

        parts = line.split(",")

        tx_id = parts[col["id"]]
        amount = int(parts[col["amount"]])
        tx_type = parts[col["transaction_type"]]
        method = parts[col["payment_provider"]]

        # Look up the price and calculate. math.floor = round down.
        percent, fixed = fees[method]
        fee = math.floor(amount * percent + fixed)

        result.append(f"{tx_id},{tx_type},{method},{fee}")

    return "\n".join(result)


# ==========================================================
# PART 2: Only charge successful payments + Ireland is cheaper
# ==========================================================
def part2(csv_data):
    # Normal prices (same as Part 1)
    normal_fees = {
        "card": (0.029, 30),
        "klarna": (0.035, 50),
        "bank_transfer": (0.008, 0),
    }

    # Special cheaper prices for Ireland
    ireland_fees = {
        "card": (0.019, 20),     # 1.9% + 20 cents
        "klarna": (0.025, 40),   # 2.5% + 40 cents
    }

    # splitlines() handles both "\n" and Windows "\r\n" line endings
    lines = csv_data.strip().splitlines()

    # Empty input: return just the output header
    if not lines:
        return "id,transaction_type,payment_provider,fee"

    header = lines[0].split(",")
    col = {name: i for i, name in enumerate(header)}

    result = ["id,transaction_type,payment_provider,fee"]

    for line in lines[1:]:
        # Skip empty lines
        if not line.strip():
            continue

        parts = line.split(",")

        tx_id = parts[col["id"]]
        amount = int(parts[col["amount"]])
        country = parts[col["buyer_country"]]
        tx_type = parts[col["transaction_type"]]
        method = parts[col["payment_provider"]]
        status = parts[col["status"]]

        # Question 1: did the payment work?
        if status != "payment_completed":
            fee = 0

        # Question 2: is it Ireland, with a special price for this method?
        elif country == "ie" and method in ireland_fees:
            percent, fixed = ireland_fees[method]
            fee = math.floor(amount * percent + fixed)

        # Otherwise: normal price
        else:
            percent, fixed = normal_fees[method]
            fee = math.floor(amount * percent + fixed)

        result.append(f"{tx_id},{tx_type},{method},{fee}")

    return "\n".join(result)


# ==========================================================
# PART 3: Country price table + volume discounts per merchant
# ==========================================================
def part3(csv_data, country_fees):
    # Notebook: merchant -> number of successful payments so far
    count = {}

    # splitlines() handles both "\n" and Windows "\r\n" line endings
    lines = csv_data.strip().splitlines()

    # Empty input: return just the output header
    if not lines:
        return "id,transaction_type,payment_provider,fee"

    header = lines[0].split(",")
    col = {name: i for i, name in enumerate(header)}

    result = ["id,transaction_type,payment_provider,fee"]

    # Go in order - the order of rows matters for the count
    for line in lines[1:]:
        # Skip empty lines
        if not line.strip():
            continue

        parts = line.split(",")

        tx_id = parts[col["id"]]
        amount = int(parts[col["amount"]])
        merchant = parts[col["merchant_id"]]
        country = parts[col["buyer_country"]]
        tx_type = parts[col["transaction_type"]]
        method = parts[col["payment_provider"]]
        status = parts[col["status"]]

        # Failed / pending: no fee, and it does NOT count toward the discount
        if status != "payment_completed":
            fee = 0

        else:
            # Which successful payment is this for the merchant? (1st, 2nd, ... 11th)
            number = count.get(merchant, 0) + 1

            # Pick the discount - check the biggest tier first
            if number >= 101:
                discount = 0.20
            elif number >= 51:
                discount = 0.15
            elif number >= 11:
                discount = 0.10
            else:
                discount = 0

            # Look up the price for this country. If the country (or method)
            # isn't in the table, use "default".
            if country in country_fees and method in country_fees[country]:
                percent, fixed = country_fees[country][method]
            else:
                percent, fixed = country_fees["default"][method]

            # Normal fee -> apply discount -> round down once at the end
            fee = math.floor((amount * percent + fixed) * (1 - discount))

            # Add 1 to this merchant's count (only for successful payments)
            count[merchant] = count.get(merchant, 0) + 1

        result.append(f"{tx_id},{tx_type},{method},{fee}")

    return "\n".join(result)


# ==========================================================
# TESTS - using the examples from the question
# ==========================================================
if __name__ == "__main__":
    HEADER = "id,reference,amount,currency,date,merchant_id,buyer_country,transaction_type,payment_provider,status"

    # ---------- Part 1 ----------
    data1 = f"""{HEADER}
py_1,1,1000,eur,2024-12-24,acct_1,ie,payment,card,payment_completed
py_2,2,2500,eur,2024-12-24,acct_2,de,payment,card,payment_failed
py_3,3,3400,eur,2024-12-25,acct_2,ie,payment,klarna,payment_completed
py_4,4,5000,eur,2024-12-25,acct_1,fr,payment,bank_transfer,payment_completed"""

    expected1 = """id,transaction_type,payment_provider,fee
py_1,payment,card,59
py_2,payment,card,102
py_3,payment,klarna,169
py_4,payment,bank_transfer,40"""

    print("Part 1:", "PASS" if part1(data1) == expected1 else "FAIL")
    print(part1(data1), "\n")

    # ---------- Part 2 ----------
    data2 = data1 + "\npy_5,5,2000,eur,2024-12-26,acct_1,ie,payment,card,payment_pending"

    expected2 = """id,transaction_type,payment_provider,fee
py_1,payment,card,39
py_2,payment,card,0
py_3,payment,klarna,125
py_4,payment,bank_transfer,40
py_5,payment,card,0"""

    print("Part 2:", "PASS" if part2(data2) == expected2 else "FAIL")
    print(part2(data2), "\n")

    # ---------- Part 3 ----------
    country_fees = {
        "ie": {"card": (0.019, 20), "klarna": (0.025, 40), "bank_transfer": (0.006, 0)},
        "de": {"card": (0.025, 25), "klarna": (0.030, 45), "bank_transfer": (0.007, 0)},
        "fr": {"card": (0.027, 28), "klarna": (0.032, 48), "bank_transfer": (0.008, 0)},
        "default": {"card": (0.029, 30), "klarna": (0.035, 50), "bank_transfer": (0.008, 0)},
    }

    # acct_1 makes 10 successful payments, then one failed one,
    # then py_11 and py_12 (should get 10% off)
    rows = [HEADER]
    for i in range(1, 11):
        rows.append(f"py_{i},{i},1500,eur,2024-12-24,acct_1,ie,payment,card,payment_completed")
    rows.append("py_fail,0,1500,eur,2024-12-24,acct_1,ie,payment,card,payment_failed")
    rows.append("py_11,11,1500,eur,2024-12-25,acct_1,ie,payment,card,payment_completed")
    rows.append("py_12,12,1500,eur,2024-12-25,acct_1,ie,payment,card,payment_completed")
    rows.append("py_us,13,1000,usd,2024-12-25,acct_2,us,payment,card,payment_completed")
    data3 = "\n".join(rows)

    expected3 = ["id,transaction_type,payment_provider,fee"]
    expected3 += [f"py_{i},payment,card,48" for i in range(1, 11)]  # 48.5 -> 48
    expected3 += [
        "py_fail,payment,card,0",   # failed -> 0, not counted
        "py_11,payment,card,43",    # 48.5 x 0.9 = 43.65 -> 43
        "py_12,payment,card,43",
        "py_us,payment,card,59",    # "us" not in table -> default
    ]

    print("Part 3:", "PASS" if part3(data3, country_fees) == "\n".join(expected3) else "FAIL")
    print(part3(data3, country_fees))

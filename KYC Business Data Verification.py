"""
Stripe KYC - Business Account Data Verification
All 5 parts in one file. Each part is its own self-contained function,
so you can read (or explain) any part without looking at the others.

Run:  python stripe_kyc_all_parts.py
"""


# ===========================================================================
# PART 1: Check for Missing Info
# A business is VERIFIED only if all 6 fields have text.
# A field with only spaces counts as empty.
# ===========================================================================
def validate_part1(csv_data):
    lines = csv_data.strip().split("\n")
    results = []

    for line in lines[1:]:                      # skip header
        if not line.strip():                    # skip blank lines
            continue
        fields = [f.strip() for f in line.split(",")]
        name = fields[1] if len(fields) > 1 else ""

        if len(fields) == 6 and all(fields):
            status = "VERIFIED"
        else:
            status = "NOT VERIFIED"

        results.append(f"{status}: {name}".rstrip())

    return "\n".join(results)


# ===========================================================================
# PART 2: Check Description Length
# Part 1 + full description (col5) must be 5 to 31 characters (inclusive).
# ===========================================================================
def validate_part2(csv_data):
    MIN_LEN = 5
    MAX_LEN = 31

    lines = csv_data.strip().split("\n")
    results = []

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = [f.strip() for f in line.split(",")]
        name = fields[1] if len(fields) > 1 else ""

        # Check 1: all fields present
        if len(fields) != 6 or not all(fields):
            results.append(f"NOT VERIFIED: {name}".rstrip())
            continue

        # Check 2: col5 length
        full_desc = fields[4]
        if not (MIN_LEN <= len(full_desc) <= MAX_LEN):
            results.append(f"NOT VERIFIED: {name}")
            continue

        results.append(f"VERIFIED: {name}")

    return "\n".join(results)


# ===========================================================================
# PART 3: Block Bad Words
# Parts 1-2 + col5 must not contain a blocked generic term (case-insensitive).
# ===========================================================================
def validate_part3(csv_data):
    MIN_LEN = 5
    MAX_LEN = 31
    BLOCKED_TERMS = {"ONLINE STORE", "ECOMMERCE", "RETAIL", "SHOP", "GENERAL MERCHANDISE"}

    lines = csv_data.strip().split("\n")
    results = []

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = [f.strip() for f in line.split(",")]
        name = fields[1] if len(fields) > 1 else ""

        # Check 1: all fields present
        if len(fields) != 6 or not all(fields):
            results.append(f"NOT VERIFIED: {name}".rstrip())
            continue

        full_desc = fields[4]

        # Check 2: col5 length
        if not (MIN_LEN <= len(full_desc) <= MAX_LEN):
            results.append(f"NOT VERIFIED: {name}")
            continue

        # Check 3: blocked terms (substring match, so "WORKSHOP" contains "SHOP")
        desc_upper = full_desc.upper()
        if any(term in desc_upper for term in BLOCKED_TERMS):
            results.append(f"NOT VERIFIED: {name}")
            continue

        results.append(f"VERIFIED: {name}")

    return "\n".join(results)


# ===========================================================================
# PART 4: Match Business Names
# Parts 1-3 + at least 50% of the name's words (minus LLC/Inc)
# must appear in col4 or col5.
# ===========================================================================
def validate_part4(csv_data):
    MIN_LEN = 5
    MAX_LEN = 31
    BLOCKED_TERMS = {"ONLINE STORE", "ECOMMERCE", "RETAIL", "SHOP", "GENERAL MERCHANDISE"}
    IGNORED_WORDS = {"llc", "inc"}

    def get_words(text):
        """Lowercase, split by whitespace, drop LLC/Inc."""
        return [w for w in text.lower().split() if w not in IGNORED_WORDS]

    def name_matches(name, short_desc, full_desc):
        name_words = set(get_words(name))
        if not name_words:                      # e.g. name was just "Inc"
            return False
        desc_words = set(get_words(short_desc)) | set(get_words(full_desc))
        matches = len(name_words & desc_words)
        return matches / len(name_words) >= 0.5

    lines = csv_data.strip().split("\n")
    results = []

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = [f.strip() for f in line.split(",")]
        name = fields[1] if len(fields) > 1 else ""

        # Check 1: all fields present
        if len(fields) != 6 or not all(fields):
            results.append(f"NOT VERIFIED: {name}".rstrip())
            continue

        short_desc = fields[3]
        full_desc = fields[4]

        # Check 2: col5 length
        if not (MIN_LEN <= len(full_desc) <= MAX_LEN):
            results.append(f"NOT VERIFIED: {name}")
            continue

        # Check 3: blocked terms
        if any(term in full_desc.upper() for term in BLOCKED_TERMS):
            results.append(f"NOT VERIFIED: {name}")
            continue

        # Check 4: name matches descriptions
        if not name_matches(name, short_desc, full_desc):
            results.append(f"NOT VERIFIED: {name}")
            continue

        results.append(f"VERIFIED: {name}")

    return "\n".join(results)


# ===========================================================================
# PART 5: Return Specific Error Codes
# All rules, checked in order; return the code of the FIRST rule that fails.
# ===========================================================================
def validate_part5(csv_data):
    MIN_LEN = 5
    MAX_LEN = 31
    BLOCKED_TERMS = {"ONLINE STORE", "ECOMMERCE", "RETAIL", "SHOP", "GENERAL MERCHANDISE"}
    IGNORED_WORDS = {"llc", "inc"}

    def get_words(text):
        return [w for w in text.lower().split() if w not in IGNORED_WORDS]

    # --- Each check returns True if the row PASSES ---
    def has_all_fields(fields):
        return len(fields) == 6 and all(fields)

    def has_valid_length(fields):
        return MIN_LEN <= len(fields[4]) <= MAX_LEN

    def has_no_blocked_terms(fields):
        desc = fields[4].upper()
        return not any(term in desc for term in BLOCKED_TERMS)

    def name_matches(fields):
        name_words = set(get_words(fields[1]))
        if not name_words:
            return False
        desc_words = set(get_words(fields[3])) | set(get_words(fields[4]))
        return len(name_words & desc_words) / len(name_words) >= 0.5

    # Order matters: first failure wins. Adding a new rule = one new line here.
    RULES = [
        (has_all_fields,       "ERROR_MISSING_FIELDS"),
        (has_valid_length,     "ERROR_INVALID_LENGTH"),
        (has_no_blocked_terms, "ERROR_GENERIC_NAME"),
        (name_matches,         "ERROR_NAME_MISMATCH"),
    ]

    lines = csv_data.strip().split("\n")
    results = []

    for line in lines[1:]:
        if not line.strip():
            continue
        fields = [f.strip() for f in line.split(",")]
        name = fields[1] if len(fields) > 1 else ""

        status = "VERIFIED"
        for check, error_code in RULES:
            if not check(fields):
                status = error_code
                break

        results.append(f"{status}: {name}".rstrip())

    return "\n".join(results)


# ===========================================================================
# TESTS - examples from the problem statement
# ===========================================================================
def run_test(label, func, data, expected):
    output = func(data)
    ok = output == expected
    print(f"===== {label}: {'PASS' if ok else 'FAIL'} =====")
    print(output)
    if not ok:
        print("--- expected ---")
        print(expected)
    print()
    return ok


if __name__ == "__main__":
    all_ok = True

    # ---------------- Part 1 ----------------
    data1 = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,,,Artisan coffee roasters
BIZ003,,,,,
BIZ004,Tech Solutions,techsol.io,Tech,TECH SOLUTIONS,Software consulting"""
    expected1 = """VERIFIED: Pawsome Pets Inc.
NOT VERIFIED: Bean Bliss Coffee
NOT VERIFIED:
VERIFIED: Tech Solutions"""
    all_ok &= run_test("Part 1", validate_part1, data1, expected1)

    # ---------------- Part 2 ----------------
    data2 = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,Bean,Bean,Artisan coffee roasters
BIZ003,Oakridge Furniture,oakridge.com,Oak,OAKRIDGE CUSTOM WOODWORKING AND FURNITURE EMPORIUM,Custom furniture
BIZ004,Tech Solutions,techsol.io,Tech,ITCS,Software consulting"""
    expected2 = """VERIFIED: Pawsome Pets Inc.
NOT VERIFIED: Bean Bliss Coffee
NOT VERIFIED: Oakridge Furniture
NOT VERIFIED: Tech Solutions"""
    all_ok &= run_test("Part 2", validate_part2, data2, expected2)

    # ---------------- Part 3 ----------------
    data3 = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Global Goods Market,globalgoods.com,Global,ONLINE STORE,Various products
BIZ003,Northwest Tech,nwtech.com,NW Tech,NORTHWEST INNOVATION TECH,Technology solutions
BIZ004,Sweet Dreams,sweetdreams.com,Sweet,SWEET DREAMS CREAMERY,Ice cream shop"""
    expected3 = """VERIFIED: Pawsome Pets Inc.
NOT VERIFIED: Global Goods Market
VERIFIED: Northwest Tech
VERIFIED: Sweet Dreams"""
    all_ok &= run_test("Part 3", validate_part3, data3, expected3)

    # ---------------- Part 4 ----------------
    data4 = """col1,col2,col3,col4,col5,col6
BIZ001,land water,landwater.com,land,land water LLC,Environmental services
BIZ002,Acme Global Trading,acme.com,Acme,XYZ ENTERPRISES,Import export services
BIZ003,Maple Ridge Bakery,maplebakery.com,Maple,MAPLE RIDGE BAKERY LLC,Artisan baked goods
BIZ004,Innovation Labs Inc,innovlabs.com,Labs,INNOVATION RESEARCH,R&D services"""
    expected4 = """VERIFIED: land water
NOT VERIFIED: Acme Global Trading
VERIFIED: Maple Ridge Bakery
VERIFIED: Innovation Labs Inc"""
    all_ok &= run_test("Part 4", validate_part4, data4, expected4)

    # ---------------- Part 5 ----------------
    data5 = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,,,Artisan coffee roasters
BIZ003,Short Name,short.com,Short,SHRT,Products
BIZ004,Generic Store,generic.com,Store,RETAIL,Various items
BIZ005,Mismatched Corp,mismatch.com,Wrong,DIFFERENT BUSINESS,Services"""
    expected5 = """VERIFIED: Pawsome Pets Inc.
ERROR_MISSING_FIELDS: Bean Bliss Coffee
ERROR_INVALID_LENGTH: Short Name
ERROR_GENERIC_NAME: Generic Store
ERROR_NAME_MISMATCH: Mismatched Corp"""
    all_ok &= run_test("Part 5", validate_part5, data5, expected5)

    print("All parts passed!" if all_ok else "Some parts failed.")

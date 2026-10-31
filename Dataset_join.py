# ==========================================================
# PART 1: Inner join - keep only customer rows that have a match
# ==========================================================
def join_part1(field_name, customer_file, processor_file, skip_unmatched):
    # Headers (first line of each file)
    customer_header = customer_file[0].split(",")
    processor_header = processor_file[0].split(",")

    # Where is the join column in each file? (can be different positions)
    c_idx = customer_header.index(field_name)
    p_idx = processor_header.index(field_name)

    # Notebook: join value -> processor row
    processor_by_key = {}
    for line in processor_file[1:]:
        p_row = line.split(",")
        processor_by_key[p_row[p_idx]] = p_row

    # Output starts with both headers joined together
    result = [",".join(customer_header + processor_header)]

    for line in customer_file[1:]:
        c_row = line.split(",")
        key = c_row[c_idx]
        if key in processor_by_key:
            p_row = processor_by_key[key]
            result.append(",".join(c_row + p_row))

    return result


# ==========================================================
# PART 2: Left join - unmatched customer rows get empty processor columns
# ==========================================================
def join_part2(field_name, customer_file, processor_file, skip_unmatched):
    customer_header = customer_file[0].split(",")
    processor_header = processor_file[0].split(",")

    c_idx = customer_header.index(field_name)
    p_idx = processor_header.index(field_name)

    processor_by_key = {}
    for line in processor_file[1:]:
        p_row = line.split(",")
        processor_by_key[p_row[p_idx]] = p_row

    # Empty processor columns, e.g. ["", "", ""]
    empty_processor = [""] * len(processor_header)

    result = [",".join(customer_header + processor_header)]

    for line in customer_file[1:]:
        c_row = line.split(",")
        key = c_row[c_idx]
        if key in processor_by_key:
            p_row = processor_by_key[key]
            result.append(",".join(c_row + p_row))
        else:
            result.append(",".join(c_row + empty_processor))

    return result


# ==========================================================
# PART 3: One-to-many - one output row per matching processor row
# ==========================================================
def join_part3(field_name, customer_file, processor_file, skip_unmatched):
    customer_header = customer_file[0].split(",")
    processor_header = processor_file[0].split(",")

    c_idx = customer_header.index(field_name)
    p_idx = processor_header.index(field_name)

    # Notebook: join value -> LIST of processor rows (in file order)
    processor_by_key = {}
    for line in processor_file[1:]:
        p_row = line.split(",")
        key = p_row[p_idx]
        if key not in processor_by_key:
            processor_by_key[key] = []
        processor_by_key[key].append(p_row)

    empty_processor = [""] * len(processor_header)

    result = [",".join(customer_header + processor_header)]

    for line in customer_file[1:]:
        c_row = line.split(",")
        key = c_row[c_idx]
        if key in processor_by_key:
            for p_row in processor_by_key[key]:
                result.append(",".join(c_row + p_row))
        else:
            result.append(",".join(c_row + empty_processor))

    return result


# ==========================================================
# PART 4: skip_unmatched - if True, drop customer rows with no match
# ==========================================================
def join_part4(field_name, customer_file, processor_file, skip_unmatched):
    customer_header = customer_file[0].split(",")
    processor_header = processor_file[0].split(",")

    c_idx = customer_header.index(field_name)
    p_idx = processor_header.index(field_name)

    processor_by_key = {}
    for line in processor_file[1:]:
        p_row = line.split(",")
        key = p_row[p_idx]
        if key not in processor_by_key:
            processor_by_key[key] = []
        processor_by_key[key].append(p_row)

    empty_processor = [""] * len(processor_header)

    result = [",".join(customer_header + processor_header)]

    for line in customer_file[1:]:
        c_row = line.split(",")
        key = c_row[c_idx]
        if key in processor_by_key:
            for p_row in processor_by_key[key]:
                result.append(",".join(c_row + p_row))
        elif not skip_unmatched:
            result.append(",".join(c_row + empty_processor))
        # else: skip_unmatched is True and no match -> drop the row

    return result


# ==========================================================
# TESTS
# ==========================================================
if __name__ == "__main__":
    def check(name, got, expected):
        print(name, "PASS" if got == expected else "FAIL")
        if got != expected:
            print("  expected:", expected)
            print("  got:     ", got)

    # ---- Part 1: every customer has exactly one match ----
    customers = ["payment_id,customer_name,amount", "p_001,Alice,100", "p_002,Bob,200"]
    processors = ["processor_ref,payment_id,status", "r_b1,p_002,FAILED", "r_a1,p_001,SETTLED"]
    check("Part 1", join_part1("payment_id", customers, processors, False), [
        "payment_id,customer_name,amount,processor_ref,payment_id,status",
        "p_001,Alice,100,r_a1,p_001,SETTLED",
        "p_002,Bob,200,r_b1,p_002,FAILED",
    ])

    # ---- Part 2: the example from the question ----
    customers = ["payment_id,customer_name,amount", "p_001,Alice,100", "p_999,Orphan,50"]
    processors = ["processor_ref,payment_id,status", "r_a1,p_001,SETTLED"]
    expected2 = [
        "payment_id,customer_name,amount,processor_ref,payment_id,status",
        "p_001,Alice,100,r_a1,p_001,SETTLED",
        "p_999,Orphan,50,,,",
    ]
    check("Part 2", join_part2("payment_id", customers, processors, False), expected2)

    # ---- Part 3: one customer, many processor rows (ordering example from the question) ----
    customers = ["payment_id,customer_name,amount", "p_001,Alice,100", "p_002,Bob,200"]
    processors = ["processor_ref,payment_id,status",
                  "r_b1,p_002,FAILED", "r_a1,p_001,SETTLED",
                  "r_b2,p_002,SETTLED", "r_a2,p_001,REFUNDED"]
    check("Part 3", join_part3("payment_id", customers, processors, False), [
        "payment_id,customer_name,amount,processor_ref,payment_id,status",
        "p_001,Alice,100,r_a1,p_001,SETTLED",
        "p_001,Alice,100,r_a2,p_001,REFUNDED",
        "p_002,Bob,200,r_b1,p_002,FAILED",
        "p_002,Bob,200,r_b2,p_002,SETTLED",
    ])

    # ---- Part 4: same input as Part 2, but skip_unmatched=True ----
    customers = ["payment_id,customer_name,amount", "p_001,Alice,100", "p_999,Orphan,50"]
    processors = ["processor_ref,payment_id,status", "r_a1,p_001,SETTLED"]
    check("Part 4 (skip=True) ", join_part4("payment_id", customers, processors, True), [
        "payment_id,customer_name,amount,processor_ref,payment_id,status",
        "p_001,Alice,100,r_a1,p_001,SETTLED",
    ])
    check("Part 4 (skip=False)", join_part4("payment_id", customers, processors, False), expected2)

    # ---- Edge: processor file has only a header, skip=True -> only header ----
    check("Edge: empty processor, skip=True", join_part4("payment_id", customers,
          ["processor_ref,payment_id,status"], True),
          ["payment_id,customer_name,amount,processor_ref,payment_id,status"])

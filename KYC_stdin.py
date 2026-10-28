"""
Stripe KYC - Business Data Verification (Standard I/O version)

Reads the whole CSV from stdin, prints VERIFIED / NOT VERIFIED per data row.

Run:  python kyc_stdin.py < input.txt
"""

import sys

NUM_COLUMNS = 6
MIN_LEN = 5
MAX_LEN = 31
FORBIDDEN_WORDS = ["company", "firm", "co.", "corporation", "group"]   # checked in col2
IGNORED_WORDS = {"llc", "inc"}


# ---------- Rule 1: no empty fields ----------
def has_all_fields(fields):
    return len(fields) == NUM_COLUMNS and all(fields)


# ---------- Rule 2: col5 length in [5, 31] ----------
def has_valid_length(fields):
    return MIN_LEN <= len(fields[4]) <= MAX_LEN


# ---------- Rule 3: no forbidden word in col2 (case-insensitive substring) ----------
def has_no_forbidden_words(fields):
    name = fields[1].lower()
    return not any(word in name for word in FORBIDDEN_WORDS)


# ---------- Rule 4: >= 50% of col2 words appear in col4 or col5 ----------
def get_words(text):
    return [w for w in text.lower().split() if w not in IGNORED_WORDS]


def name_matches(fields):
    name_words = get_words(fields[1])
    if not name_words:                      # name was only "LLC"/"Inc"
        return False
    desc_words = set(get_words(fields[3])) | set(get_words(fields[4]))
    matches = sum(1 for w in name_words if w in desc_words)
    return matches / len(name_words) >= 0.5


RULES = [has_all_fields, has_valid_length, has_no_forbidden_words, name_matches]


def verify(csv_text):
    lines = csv_text.splitlines()           # handles \n and \r\n
    results = []
    for line in lines[1:]:                  # skip header
        if not line.strip():                # skip blank lines
            continue
        fields = [f.strip() for f in line.split(",")]
        ok = all(rule(fields) for rule in RULES)   # all() stops at first failure
        results.append("VERIFIED" if ok else "NOT VERIFIED")
    return results


def main():
    csv_text = sys.stdin.read()
    for result in verify(csv_text):
        print(result)


if __name__ == "__main__":
    main()

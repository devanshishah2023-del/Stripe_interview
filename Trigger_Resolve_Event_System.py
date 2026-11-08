"""
Stripe - Incident Monitor (Transaction Alert Trigger / Resolve)
All three parts in one file. Each part is its own complete function.

Input:  list of "timestamp,merchant_id,status_code,count", sorted by timestamp
Output: list of "timestamp,EVENT,merchant_id,status_code",
        sorted by time, shop, code, event ("RESOLVE" before "TRIGGER")
Window: [t-30, t]  (matches the question's examples; confirm with the interviewer)

Run:  python3 incident_monitor_all_parts.py
"""
from collections import defaultdict, deque


# ==========================================================
# PART 1: 5 or more errors of one code in the window -> TRIGGER (once)
# ==========================================================
def part1(logs):
    # ---- Block A: set up empty storage ----
    recent = defaultdict(deque)                      # shop -> queue of (time, status, count)
    counts = defaultdict(lambda: defaultdict(int))   # shop -> {status: total in window}
    active = set()                                   # alarms that are ON: {(shop, code)}
    events = []

    for line in logs:
        # ---- Block B: read the log ----
        t, merchant, status, count = line.split(",")
        t, status, count = int(t), int(status), int(count)

        # ---- Block C: add it to this shop's window ----
        recent[merchant].append((t, status, count))
        counts[merchant][status] += count

        # ---- Block D: remove logs older than the window [t-30, t] ----
        while recent[merchant][0][0] < t - 30:
            old_t, old_status, old_count = recent[merchant].popleft()
            counts[merchant][old_status] -= old_count

        # ---- Block E: check every error code of this shop ----
        for code, errors in counts[merchant].items():
            if code == 200:
                continue                             # a success is not an error
            bad = errors >= 5

            # ---- Block F: turn the alarm on ----
            pair = (merchant, code)
            if bad and pair not in active:
                active.add(pair)
                events.append((t, merchant, code, "TRIGGER"))

    # ---- Block G: sort and format ----
    events.sort()
    return [f"{t},{event},{m},{code}" for t, m, code, event in events]


# ==========================================================
# PART 2: also need errors > 1% of successes (errors * 100 > successes)
# ==========================================================
def part2(logs):
    # ---- Block A: set up empty storage ----
    recent = defaultdict(deque)
    counts = defaultdict(lambda: defaultdict(int))
    active = set()
    events = []

    for line in logs:
        # ---- Block B: read the log ----
        t, merchant, status, count = line.split(",")
        t, status, count = int(t), int(status), int(count)

        # ---- Block C: add it to this shop's window ----
        recent[merchant].append((t, status, count))
        counts[merchant][status] += count

        # ---- Block D: remove logs older than the window [t-30, t] ----
        while recent[merchant][0][0] < t - 30:
            old_t, old_status, old_count = recent[merchant].popleft()
            counts[merchant][old_status] -= old_count

        # ---- Block E: check every error code of this shop ----
        successes = counts[merchant][200]
        for code, errors in counts[merchant].items():
            if code == 200:
                continue
            bad = errors >= 5 and errors * 100 > successes      # NEW in Part 2

            # ---- Block F: turn the alarm on ----
            pair = (merchant, code)
            if bad and pair not in active:
                active.add(pair)
                events.append((t, merchant, code, "TRIGGER"))

    # ---- Block G: sort and format ----
    events.sort()
    return [f"{t},{event},{m},{code}" for t, m, code, event in events]


# ==========================================================
# PART 3: alarm ON and the condition becomes false -> RESOLVE
# ==========================================================
def part3(logs):
    # ---- Block A: set up empty storage ----
    recent = defaultdict(deque)
    counts = defaultdict(lambda: defaultdict(int))
    active = set()
    events = []

    for line in logs:
        # ---- Block B: read the log ----
        t, merchant, status, count = line.split(",")
        t, status, count = int(t), int(status), int(count)

        # ---- Block C: add it to this shop's window ----
        recent[merchant].append((t, status, count))
        counts[merchant][status] += count

        # ---- Block D: remove logs older than the window [t-30, t] ----
        while recent[merchant][0][0] < t - 30:
            old_t, old_status, old_count = recent[merchant].popleft()
            counts[merchant][old_status] -= old_count

        # ---- Block E: check EVERY error code of this shop ----
        # (a new 200 log or a removed old log can change any of them)
        successes = counts[merchant][200]
        for code, errors in counts[merchant].items():
            if code == 200:
                continue
            bad = errors >= 5 and errors * 100 > successes

            # ---- Block F: turn the alarm on or off ----
            pair = (merchant, code)
            if bad and pair not in active:
                active.add(pair)
                events.append((t, merchant, code, "TRIGGER"))
            elif not bad and pair in active:                    # NEW in Part 3
                active.remove(pair)
                events.append((t, merchant, code, "RESOLVE"))

    # ---- Block G: sort and format ----
    events.sort()
    return [f"{t},{event},{m},{code}" for t, m, code, event in events]


# ==========================================================
# TESTS
# ==========================================================
if __name__ == "__main__":
    ex1 = ["10,merchant1,500,2", "10,merchant2,500,1", "15,merchant1,500,2",
           "20,merchant1,500,1", "20,merchant2,500,4"]
    ex2 = ["10,merchant1,200,600", "12,merchant1,500,6",
           "15,merchant2,200,599", "16,merchant2,500,6"]
    ex3 = ["10,merchant1,500,6", "16,merchant2,500,6",
           "45,merchant1,200,1", "46,merchant2,200,1"]

    # ---------- Part 1 ----------
    print("Part 1 output:", part1(ex1))
    assert part1(ex1) == ["20,TRIGGER,merchant1,500", "20,TRIGGER,merchant2,500"]
    assert part1(["1,m,500,9", "2,m,500,9"]) == ["1,TRIGGER,m,500"]     # no duplicate
    assert part1(["1,m,200,99"]) == []                                  # 200 is not an error
    assert part1(["1,m,500,4"]) == []                                   # 4 is not enough
    assert part1(["0,m,500,4", "31,m,500,1"]) == []                     # time 0 dropped out
    print("Part 1: all tests passed\n")

    # ---------- Part 2 ----------
    print("Part 2 output:", part2(ex2))
    assert part2(ex2) == ["16,TRIGGER,merchant2,500"]
    assert part2(["1,m,500,5"]) == ["1,TRIGGER,m,500"]                  # 0 successes
    assert part2(["1,m,200,500", "2,m,500,5"]) == []                    # exactly 1%
    assert part2(["1,m,200,499", "2,m,500,5"]) == ["2,TRIGGER,m,500"]   # just over 1%
    assert part2(["1,m,200,10", "2,m,500,4"]) == []                     # only 4 errors
    print("Part 2: all tests passed\n")

    # ---------- Part 3 ----------
    print("Part 3 output:", part3(ex3))
    assert part3(ex3) == ["10,TRIGGER,merchant1,500", "16,TRIGGER,merchant2,500",
                          "45,RESOLVE,merchant1,500"]
    assert part3(ex1) == part1(ex1)                                     # earlier examples
    assert part3(ex2) == part2(ex2)                                     #   still work
    assert part3(["1,m,500,5", "40,m,200,1", "41,m,500,5"]) == \
        ["1,TRIGGER,m,500", "40,RESOLVE,m,500", "41,TRIGGER,m,500"]     # resolve, then again
    assert part3(["1,m,503,5", "1,m,500,5", "40,m,200,1"]) == \
        ["1,TRIGGER,m,500", "1,TRIGGER,m,503",
         "40,RESOLVE,m,500", "40,RESOLVE,m,503"]                        # two codes, sorted
    assert part3(["1,a,500,5", "100,b,200,1"]) == ["1,TRIGGER,a,500"]   # quiet gap: no change
    assert part3(["1,m,500,5", "2,m,200,1000"]) == \
        ["1,TRIGGER,m,500", "2,RESOLVE,m,500"]                          # many successes
    print("Part 3: all tests passed")

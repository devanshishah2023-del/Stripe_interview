n, WINDOW, THRESHOLD = map(int, input().split())

history = {}   # shop -> list of every (time, count) it ever had
alarm = {}     # shop -> True (ringing) / False (quiet)

for _ in range(n):
    t, merchant, status, count = input().split()
    t = int(t)
    count = int(count)

    shop = (merchant, status)

    # New shop? Start with an empty list and the alarm off
    if shop not in history:
        history[shop] = []
        alarm[shop] = False

    # Remember this log
    history[shop].append((t, count))

    # Add up only the errors from the last WINDOW seconds
    total = 0
    for old_time, old_count in history[shop]:
        if old_time >= t - WINDOW + 1:
            total += old_count

    # Check the alarm
    if total >= THRESHOLD and alarm[shop] == False:
        alarm[shop] = True
        print(t, merchant, status, "TRIGGER", total)
    elif total < THRESHOLD and alarm[shop] == True:
        alarm[shop] = False
        print(t, merchant, status, "RESOLVE", total)

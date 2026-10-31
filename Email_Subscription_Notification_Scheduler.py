# ==========================================================
# TASK 1: every email each user should receive, in time order
# ==========================================================
def send_emails_task1(user_accounts, send_schedule):

    # Last day we need to check = latest end day
    last_day = 0
    for user in user_accounts:
        end = user["account_date"] + user["duration"]
        if end > last_day:
            last_day = end

    # Walk through the calendar one day at a time
    for day in range(last_day + 1):
        for user in user_accounts:
            name = user["name"]
            plan = user["plan"]
            start = user["account_date"]
            end = start + user["duration"]

            for key, title in send_schedule.items():
                if key == "start":
                    send_day = start
                elif key == "end":
                    send_day = end
                else:
                    send_day = end + key          # e.g. -15 -> 15 days before end

                # Skip emails that fall before the user joined
                if send_day < start:
                    continue

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan})")


# ==========================================================
# TASK 2: plan changes -> "Changed" email, later emails show the new plan
# changes = [{"name": "John", "new_plan": "Gold", "change_date": 5}]
# ==========================================================
def send_emails_task2(user_accounts, send_schedule, changes):

    # Each user's CURRENT plan (can change over time)
    plan = {}
    for user in user_accounts:
        plan[user["name"]] = user["plan"]

    # Last day we need to check = latest end day or latest change day
    last_day = 0
    for user in user_accounts:
        end = user["account_date"] + user["duration"]
        if end > last_day:
            last_day = end
    for change in changes:
        if change["change_date"] > last_day:
            last_day = change["change_date"]

    # Walk through the calendar one day at a time
    for day in range(last_day + 1):

        # STEP A: plan changes happening today (BEFORE any email)
        for change in changes:
            if change["change_date"] == day:
                name = change["name"]
                plan[name] = change["new_plan"]
                print(f"{day}: [Changed] Subscription for {name} ({plan[name]})")

        # STEP B: emails for every user (using the CURRENT plan)
        for user in user_accounts:
            name = user["name"]
            start = user["account_date"]
            end = start + user["duration"]          # end date never changes in Task 2

            for key, title in send_schedule.items():
                if key == "start":
                    send_day = start
                elif key == "end":
                    send_day = end
                else:
                    send_day = end + key

                if send_day < start:
                    continue

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan[name]})")


# ==========================================================
# TASK 3: plan changes AND renewals
#   {"name": "John",  "new_plan": "Gold", "change_date": 5}  -> "Changed"
#   {"name": "Alice", "extension": 15,    "change_date": 3}  -> "Renewed"
# ==========================================================
def send_emails_task3(user_accounts, send_schedule, changes):

    # Each user's CURRENT plan, start day and CURRENT end day
    plan = {}
    start = {}
    end = {}
    for user in user_accounts:
        name = user["name"]
        plan[name] = user["plan"]
        start[name] = user["account_date"]
        end[name] = user["account_date"] + user["duration"]

    # Last day we need to check (renewals can push it later)
    last_day = 0
    for name in end:
        if end[name] > last_day:
            last_day = end[name]
    for change in changes:
        if change["change_date"] > last_day:
            last_day = change["change_date"]
    for change in changes:
        if "extension" in change:
            last_day = last_day + change["extension"]

    # Walk through the calendar one day at a time
    for day in range(last_day + 1):

        # STEP A1: plan changes today (first)
        for change in changes:
            if change["change_date"] == day and "new_plan" in change:
                name = change["name"]
                plan[name] = change["new_plan"]
                print(f"{day}: [Changed] Subscription for {name} ({plan[name]})")

        # STEP A2: renewals today (second)
        renewed_today = set()
        for change in changes:
            if change["change_date"] == day and "extension" in change:
                name = change["name"]
                end[name] = end[name] + change["extension"]
                renewed_today.add(name)
                print(f"{day}: [Renewed] Subscription for {name} ({plan[name]})")

        # STEP B: emails for every user (CURRENT plan, CURRENT end)
        for user in user_accounts:
            name = user["name"]

            for key, title in send_schedule.items():
                if key == "start":
                    send_day = start[name]
                else:
                    if key == "end":
                        send_day = end[name]
                    else:
                        send_day = end[name] + key

                    if send_day < start[name]:
                        continue                 # before the user joined
                    if name in renewed_today:
                        continue                 # only emails strictly after a renewal

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan[name]})")


# ==========================================================
# TESTS
# ==========================================================
if __name__ == "__main__":
    send_schedule = {"start": "Welcome", -15: "Upcoming expiration", "end": "Expired"}
    user_accounts = [
        {"name": "John", "plan": "Silver", "account_date": 0, "duration": 30},
        {"name": "Alice", "plan": "Gold", "account_date": 1, "duration": 15},
    ]

    print("=== Task 1 ===")
    send_emails_task1(user_accounts, send_schedule)

    print("\n=== Task 2: John -> Gold on day 5 ===")
    send_emails_task2(user_accounts, send_schedule,
                      [{"name": "John", "new_plan": "Gold", "change_date": 5}])

    print("\n=== Task 3: John -> Gold on day 5, Alice renews +15 on day 3 ===")
    send_emails_task3(user_accounts, send_schedule,
                      [{"name": "John", "new_plan": "Gold", "change_date": 5},
                       {"name": "Alice", "extension": 15, "change_date": 3}])

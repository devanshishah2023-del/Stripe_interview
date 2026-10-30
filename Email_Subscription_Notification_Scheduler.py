# ==========================================================
# TASK 1: basic emails
# ==========================================================
def task1(user_accounts, schedule):

    # Find the last day we need to check
    last_day = 0
    for user in user_accounts:
        end = user["account_date"] + user["duration"]
        if end > last_day:
            last_day = end

    # Go through the calendar one day at a time
    for day in range(last_day + 1):
        for user in user_accounts:
            name = user["name"]
            plan = user["plan"]
            start = user["account_date"]
            end = start + user["duration"]

            for when, title in schedule.items():
                if when == "start":
                    send_day = start
                elif when == "end":
                    send_day = end
                else:
                    send_day = end + when        # -15 -> 15 days before the end

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan})")


# ==========================================================
# TASK 2: plan changes -> "Updated" email, later emails show the new plan
# subscription_changes = [{"change_time": 5, "name": "John", "new_plan": "Gold"}]
# ==========================================================
def task2(user_accounts, schedule, subscription_changes):

    # Each user's CURRENT plan (it can change over time)
    plan = {}
    for user in user_accounts:
        plan[user["name"]] = user["plan"]

    # Find the last day we need to check
    last_day = 0
    for user in user_accounts:
        end = user["account_date"] + user["duration"]
        if end > last_day:
            last_day = end

    # Go through the calendar one day at a time
    for day in range(last_day + 1):
        for user in user_accounts:
            name = user["name"]
            start = user["account_date"]
            end = start + user["duration"]

            # 1. Welcome email
            if day == start:
                print(f"{day}: [{schedule['start']}] Subscription for {name} ({plan[name]})")

            # 2. Any plan change for this user today?
            for change in subscription_changes:
                if change["name"] == name and change["change_time"] == day:
                    plan[name] = change["new_plan"]
                    print(f"{day}: [Updated] Subscription for {name} ({plan[name]})")

            # 3. Upcoming expiry / Expired emails
            for when, title in schedule.items():
                if when == "start":
                    continue                     # Welcome already handled
                elif when == "end":
                    send_day = end
                else:
                    send_day = end + when

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan[name]})")


# ==========================================================
# TASK 3: plan changes AND extensions
#   {"change_time": 5, "name": "John",  "new_plan": "Gold"}    -> "Updated"
#   {"change_time": 3, "name": "Alice", "extension_days": 15}  -> "Renewed"
# ==========================================================
def task3(user_accounts, schedule, subscription_changes):

    # Each user's CURRENT plan and CURRENT end day (both can change)
    plan = {}
    end = {}
    for user in user_accounts:
        plan[user["name"]] = user["plan"]
        end[user["name"]] = user["account_date"] + user["duration"]

    # Find the last day we need to check (extensions can push it later)
    last_day = 0
    for name in end:
        if end[name] > last_day:
            last_day = end[name]
    for change in subscription_changes:
        if "extension_days" in change:
            last_day = last_day + change["extension_days"]

    # Go through the calendar one day at a time
    for day in range(last_day + 1):
        for user in user_accounts:
            name = user["name"]
            start = user["account_date"]

            # 1. Welcome email
            if day == start:
                print(f"{day}: [{schedule['start']}] Subscription for {name} ({plan[name]})")

            # 2. Any change for this user today?
            for change in subscription_changes:
                if change["name"] == name and change["change_time"] == day:

                    if "new_plan" in change:
                        plan[name] = change["new_plan"]
                        print(f"{day}: [Updated] Subscription for {name} ({plan[name]})")

                    if "extension_days" in change:
                        end[name] = end[name] + change["extension_days"]
                        print(f"{day}: [Renewed] Subscription for {name} ({plan[name]})")

            # 3. Upcoming expiry / Expired emails (using the CURRENT end day)
            for when, title in schedule.items():
                if when == "start":
                    continue
                elif when == "end":
                    send_day = end[name]
                else:
                    send_day = end[name] + when

                if day == send_day:
                    print(f"{day}: [{title}] Subscription for {name} ({plan[name]})")


# ==========================================================
# TESTS
# ==========================================================
if __name__ == "__main__":
    schedule = {"start": "Welcome", -15: "Upcoming expiry", "end": "Expired"}
    user_accounts = [
        {"name": "John", "plan": "Silver", "account_date": 0, "duration": 30},
        {"name": "Alice", "plan": "Gold", "account_date": 1, "duration": 15},
    ]

    print("=== Task 1 ===")
    task1(user_accounts, schedule)

    print("\n=== Task 2: John changes to Gold at time 5 ===")
    task2(user_accounts, schedule,
          [{"change_time": 5, "name": "John", "new_plan": "Gold"}])

    print("\n=== Task 3: John changes to Gold at 5, Alice extends 15 days at 3 ===")
    task3(user_accounts, schedule,
          [{"change_time": 5, "name": "John", "new_plan": "Gold"},
           {"change_time": 3, "name": "Alice", "extension_days": 15}])

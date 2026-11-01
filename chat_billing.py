# ==========================================================
# LEVEL 1: Pay-as-you-go only
#   $0.03 per full 100 input tokens, $0.04 per full 100 output tokens
# ==========================================================
def billing_level1(sessions):
    input_total = {}       # user -> total input tokens
    output_total = {}      # user -> total output tokens

    for record in sessions:
        user, input_str, output_str, plan = record.split(",")
        if user not in input_total:
            input_total[user] = 0
            output_total[user] = 0
        input_total[user] += int(input_str)
        output_total[user] += int(output_str)

    result = []
    for user in sorted(input_total):                 # A-Z order
        cost = (input_total[user] // 100) * 0.03 + (output_total[user] // 100) * 0.04
        result.append(f"{user}: ${cost:.2f}")
    return result


# ==========================================================
# LEVEL 2: add the fixed plan
#   $15 per month, includes 40,000 input + 20,000 output tokens
#   Tokens above that are charged at pay-as-you-go rates
# ==========================================================
def billing_level2(sessions):
    payg_in, payg_out = {}, {}       # user -> pay-as-you-go tokens
    fixed_in, fixed_out = {}, {}     # user -> fixed-plan tokens
    fixed_sessions = {}              # user -> number of fixed-plan sessions

    for record in sessions:
        user, input_str, output_str, plan = record.split(",")
        if user not in payg_in:
            payg_in[user] = payg_out[user] = 0
            fixed_in[user] = fixed_out[user] = 0
            fixed_sessions[user] = 0

        if plan == "payg":
            payg_in[user] += int(input_str)
            payg_out[user] += int(output_str)
        else:                                       # "fixed"
            fixed_in[user] += int(input_str)
            fixed_out[user] += int(output_str)
            fixed_sessions[user] += 1

    result = []
    for user in sorted(payg_in):
        # pay-as-you-go part
        cost = (payg_in[user] // 100) * 0.03 + (payg_out[user] // 100) * 0.04

        # fixed part (only if the user has fixed sessions)
        if fixed_sessions[user] > 0:
            extra_in = max(0, fixed_in[user] - 40000)       # tokens above the allowance
            extra_out = max(0, fixed_out[user] - 20000)
            cost += 15.00 + (extra_in // 100) * 0.03 + (extra_out // 100) * 0.04

        result.append(f"{user}: ${cost:.2f}")
    return result


# ==========================================================
# LEVEL 3: plan switching -> shrink the fixed fee and allowances
#   ratio = fixed sessions / all sessions of that user
# ==========================================================
def billing_level3(sessions):
    payg_in, payg_out = {}, {}
    fixed_in, fixed_out = {}, {}
    fixed_sessions = {}
    all_sessions = {}                 # NEW: user -> total number of sessions

    for record in sessions:
        user, input_str, output_str, plan = record.split(",")
        if user not in payg_in:
            payg_in[user] = payg_out[user] = 0
            fixed_in[user] = fixed_out[user] = 0
            fixed_sessions[user] = 0
            all_sessions[user] = 0

        all_sessions[user] += 1
        if plan == "payg":
            payg_in[user] += int(input_str)
            payg_out[user] += int(output_str)
        else:
            fixed_in[user] += int(input_str)
            fixed_out[user] += int(output_str)
            fixed_sessions[user] += 1

    result = []
    for user in sorted(payg_in):
        cost = (payg_in[user] // 100) * 0.03 + (payg_out[user] // 100) * 0.04

        if fixed_sessions[user] > 0:
            ratio = fixed_sessions[user] / all_sessions[user]      # NEW
            fee = 15.00 * ratio                                      # NEW
            allowance_in = 40000 * ratio                             # NEW
            allowance_out = 20000 * ratio                            # NEW

            extra_in = max(0, fixed_in[user] - allowance_in)
            extra_out = max(0, fixed_out[user] - allowance_out)
            cost += fee + (extra_in // 100) * 0.03 + (extra_out // 100) * 0.04

        result.append(f"{user}: ${cost:.2f}")
    return result


# ==========================================================
# TESTS (examples from the question)
# ==========================================================
if __name__ == "__main__":
    def check(name, got, expected):
        print(name, "PASS" if got == expected else "FAIL", got)

    # Level 1 example
    s1 = ["userA,100,120,payg", "userB,150,100,payg", "userB,100,130,payg"]
    check("Level 1 example     ", billing_level1(s1), ["userA: $0.07", "userB: $0.14"])

    # Level 1: user who never reaches a full block still appears with $0.00
    check("Level 1 zero blocks ", billing_level1(["userC,50,99,payg"]), ["userC: $0.00"])

    # Level 2 example: fixed plan, 45,000 input / 22,000 output -> $17.30
    s2 = ["userD,25000,12000,fixed", "userD,20000,10000,fixed"]
    check("Level 2 example     ", billing_level2(s2), ["userD: $17.30"])

    # Level 3 example: 2 payg + 2 fixed -> ratio 0.5 -> $0.14 + $7.50 + $0.07 = $7.71
    s3 = ["userE,100,120,payg", "userE,150,100,payg",
          "userE,10000,5000,fixed", "userE,10100,5100,fixed"]
    check("Level 3 example     ", billing_level3(s3), ["userE: $7.71"])

    # Level 3 gives the same answers as levels 1 and 2 when nobody mixes plans
    check("Level 3 on L1 input ", billing_level3(s1), ["userA: $0.07", "userB: $0.14"])
    check("Level 3 on L2 input ", billing_level3(s2), ["userD: $17.30"])

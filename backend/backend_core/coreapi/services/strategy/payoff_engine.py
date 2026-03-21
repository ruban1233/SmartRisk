# =========================================================
# PAYOFF ENGINE (FINAL PROFESSIONAL VERSION)
# =========================================================

import numpy as np


# =========================================================
# BASIC PAYOFF (CORRECT)
# =========================================================

def call_intrinsic(spot, strike):
    return max(spot - strike, 0)


def put_intrinsic(spot, strike):
    return max(strike - spot, 0)


# =========================================================
# PAYOFF CALCULATION (FIXED CORE LOGIC)
# =========================================================

def calculate_payoff(legs, lot_size=50):

    strikes = [float(leg["strike"]) for leg in legs]

    price_range = np.arange(
        min(strikes) - 1000,
        max(strikes) + 1000,
        50
    )

    result = []

    for price in price_range:

        total_pnl = 0

        for leg in legs:

            strike = float(leg["strike"])
            premium = float(leg["premium"])
            option_type = leg["type"]
            action = leg["action"]

            # =========================
            # INTRINSIC VALUE
            # =========================
            if option_type == "CE":
                intrinsic = call_intrinsic(price, strike)
            else:
                intrinsic = put_intrinsic(price, strike)

            # =========================
            # REAL PAYOFF LOGIC
            # =========================
            if action == "BUY":
                pnl = intrinsic - premium
            else:  # SELL
                pnl = premium - intrinsic

            total_pnl += pnl

        # =========================
        # LOT SIZE MULTIPLIER
        # =========================
        total_pnl = total_pnl * lot_size

        result.append({
            "price": int(price),
            "pnl": round(total_pnl, 2)
        })

    return result


# =========================================================
# SUMMARY (IMPROVED)
# =========================================================

def calculate_summary(payoff):

    pnls = [p["pnl"] for p in payoff]

    max_profit = max(pnls)
    max_loss = min(pnls)

    breakevens = []

    # =========================
    # FIND ZERO CROSSING
    # =========================
    for i in range(1, len(payoff)):

        prev_pnl = payoff[i - 1]["pnl"]
        curr_pnl = payoff[i]["pnl"]

        if prev_pnl == 0:
            breakevens.append(payoff[i - 1]["price"])

        elif (prev_pnl < 0 and curr_pnl > 0) or (prev_pnl > 0 and curr_pnl < 0):
            breakevens.append(payoff[i]["price"])

    return {
        "max_profit": round(max_profit, 2),
        "max_loss": round(max_loss, 2),
        "breakevens": breakevens
    }
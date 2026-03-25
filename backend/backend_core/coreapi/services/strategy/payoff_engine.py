"""
payoff_engine.py
Path: backend/coreapi/services/strategy/payoff_engine.py
✔ Real lot size
✔ Correct intrinsic at expiry
✔ Breakeven detection
✔ Works with strategy legs format (action/type/strike/ltp)
   AND payoff view format (action/type/strike/premium)
"""

import numpy as np
from coreapi.services.strike_engine import get_lot_size


def call_intrinsic(spot, strike):
    return max(float(spot) - float(strike), 0)


def put_intrinsic(spot, strike):
    return max(float(strike) - float(spot), 0)


def calculate_payoff(legs, symbol="NIFTY"):
    if not legs:
        return []

    lot_size = int(get_lot_size(symbol))

    # Support both 'premium' (payoff view) and 'ltp' (strategy engine)
    def get_premium(leg):
        return float(leg.get("premium") or leg.get("ltp") or 0)

    strikes    = [float(l["strike"]) for l in legs]
    avg_strike = sum(strikes) / len(strikes)
    lower      = avg_strike * 0.92
    upper      = avg_strike * 1.08
    step       = max(10, round((upper - lower) / 60))

    price_range = np.arange(lower, upper + step, step)
    results     = []

    for price in price_range:
        total_pnl = 0.0
        for leg in legs:
            strike      = float(leg["strike"])
            premium     = get_premium(leg)
            option_type = leg.get("type") or leg.get("option_type", "CE")
            action      = leg.get("action", "BUY")

            intrinsic = call_intrinsic(price, strike) if option_type == "CE" \
                        else put_intrinsic(price, strike)

            pnl = (intrinsic - premium) if action == "BUY" \
                  else (premium - intrinsic)

            total_pnl += pnl

        results.append({
            "price": round(float(price), 2),
            "pnl":   round(total_pnl * lot_size, 2),
        })

    return results


def calculate_summary(payoff, legs=None):
    if not payoff:
        return {"max_profit": 0, "max_loss": 0, "breakevens": []}

    pnls       = [float(p["pnl"]) for p in payoff]
    max_profit = max(pnls)
    max_loss   = min(pnls)
    breakevens = []

    for i in range(1, len(payoff)):
        p1, p2 = pnls[i - 1], pnls[i]
        if (p1 < 0 and p2 >= 0) or (p1 > 0 and p2 <= 0):
            # Linear interpolation for accurate breakeven
            price1 = payoff[i - 1]["price"]
            price2 = payoff[i]["price"]
            if p2 != p1:
                be = price1 + (0 - p1) * (price2 - price1) / (p2 - p1)
                breakevens.append(round(be, 2))

    return {
        "max_profit": round(max_profit, 2),
        "max_loss":   round(max_loss, 2),
        "breakevens": breakevens,
    }
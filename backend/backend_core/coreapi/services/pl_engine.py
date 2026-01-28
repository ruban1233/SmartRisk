def pl_engine(strategy, strikes, premium_data, lot_size, lots):
    """
    Calculate Max Profit, Max Loss, Breakeven
    premium_data example:
    {
        "buy": 120,
        "sell": 60
    }
    """

    result = {}

    # =======================
    # BUY OPTION
    # =======================
    if strategy == "BUY_OPTION":
        buy_price = premium_data["buy"]
        strike = strikes["strike"]

        max_loss = buy_price * lot_size * lots
        max_profit = "Unlimited"
        breakeven = strike + buy_price

        result = {
            "max_profit": max_profit,
            "max_loss": round(max_loss, 2),
            "breakeven": breakeven
        }

    # =======================
    # DEBIT SPREAD
    # =======================
    elif strategy == "DEBIT_SPREAD":
        buy_price = premium_data["buy"]
        sell_price = premium_data["sell"]

        buy_strike = strikes["buy"]
        sell_strike = strikes["sell"]

        net_debit = buy_price - sell_price
        spread_width = abs(sell_strike - buy_strike)

        max_profit = (spread_width - net_debit) * lot_size * lots
        max_loss = net_debit * lot_size * lots
        breakeven = buy_strike + net_debit

        result = {
            "max_profit": round(max_profit, 2),
            "max_loss": round(max_loss, 2),
            "breakeven": breakeven
        }

    else:
        result = {
            "error": "P/L not implemented for this strategy yet"
        }

    # =======================
    # Risk Reward
    # =======================
    if isinstance(result.get("max_profit"), (int, float)):
        rr = round(result["max_profit"] / result["max_loss"], 2)
    else:
        rr = "N/A"

    result["risk_reward"] = rr

    # =======================
    # Doctor Advice
    # =======================
    if isinstance(result.get("max_loss"), (int, float)) and result["max_loss"] <= 5000:
        advice = "Trade allowed within acceptable risk."
    else:
        advice = "Risk too high for this capital. Avoid trade."

    result["doctor_advice"] = advice

    return result

# coreapi/services/pl_engine.py

def calculate_pl(strategy, strikes, premium_data, lot_size, lots):
    """
    Dynamic P/L calculation engine
    """

    result = {}

    # =========================
    # BUY OPTION
    # =========================
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

    # =========================
    # DEBIT SPREAD
    # =========================
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
            "error": "Strategy not implemented"
        }

    return result
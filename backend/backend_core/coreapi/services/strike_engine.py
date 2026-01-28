def strike_engine(
    symbol,
    spot_price,
    strategy,
    capital,
    risk_percent,
):
    """
    Auto select:
    - expiry type
    - strike prices
    - lot size
    """

    # Lot sizes (can be updated dynamically later)
    lot_sizes = {
        "NIFTY": 50,
        "BANKNIFTY": 15
    }

    lot_size = lot_sizes.get(symbol, 50)

    # Decide expiry
    expiry_type = "WEEKLY" if capital < 100000 else "MONTHLY"

    # Risk amount
    max_risk_amount = capital * (risk_percent / 100)

    # Strike rounding
    step = 50 if symbol == "NIFTY" else 100
    atm = round(spot_price / step) * step

    result = {
        "expiry_type": expiry_type,
        "lot_size": lot_size,
        "lots_allowed": 1,  # default safe
        "strikes": {}
    }

    # Strategy-wise strike logic
    if strategy == "BUY_OPTION":
        result["strikes"] = {
            "type": "ATM",
            "strike": atm
        }

    elif strategy == "DEBIT_SPREAD":
        result["strikes"] = {
            "buy": atm,
            "sell": atm + step
        }

    elif strategy == "CREDIT_SPREAD":
        result["strikes"] = {
            "sell": atm,
            "hedge": atm + (2 * step)
        }

    elif strategy == "IRON_CONDOR":
        result["strikes"] = {
            "sell_call": atm + step,
            "buy_call": atm + (3 * step),
            "sell_put": atm - step,
            "buy_put": atm - (3 * step)
        }

    else:
        result["strikes"] = {}

    return result

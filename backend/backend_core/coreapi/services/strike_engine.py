"""
Strike & Lot Size Engine
------------------------
✔ Lot size
✔ ATM strike
✔ Strategy-based strike selection

Used by SmartRisk AI
"""
# =========================================
# LOT SIZE
# =========================================
def get_lot_size(symbol: str) -> int:

    symbol = symbol.upper()

    if symbol == "NIFTY":
        return 65
    elif symbol == "BANKNIFTY":
        return 30
    elif symbol == "FINNIFTY":
        return 60
    elif symbol == "SENSEX":
        return 20
    elif symbol == "MIDCPNIFTY":
        return 120
    else:
        return 1


# =========================================
# ATM STRIKE
# =========================================
def get_atm_strike(spot: float, symbol: str) -> int:

    symbol = symbol.upper()

    if symbol in ["NIFTY", "FINNIFTY", "MIDCPNIFTY"]:
        step = 50
    elif symbol in ["BANKNIFTY", "SENSEX"]:
        step = 100
    else:
        step = 50

    return int(round(spot / step) * step)


# =========================================
# STRATEGY STRIKES
# =========================================

def iron_condor_strikes(spot, symbol):
    atm = get_atm_strike(spot, symbol)
    step = 50 if symbol == "NIFTY" else 100

    return {
        "sell_pe": atm - 200,
        "buy_pe": atm - 400,
        "sell_ce": atm + 200,
        "buy_ce": atm + 400
    }


def bull_call_spread_strikes(spot, symbol):
    atm = get_atm_strike(spot, symbol)
    step = 50 if symbol == "NIFTY" else 100

    return {
        "buy_ce": atm,
        "sell_ce": atm + step
    }


def bear_put_spread_strikes(spot, symbol):
    atm = get_atm_strike(spot, symbol)
    step = 50 if symbol == "NIFTY" else 100

    return {
        "buy_pe": atm,
        "sell_pe": atm - step
    }


def short_strangle_strikes(spot, symbol):
    atm = get_atm_strike(spot, symbol)

    return {
        "sell_pe": atm - 200,
        "sell_ce": atm + 200
    }


# =========================================
# MASTER SELECTOR
# =========================================
def select_strikes(strategy: str, spot: float, symbol: str):

    strategy = strategy.upper()

    if strategy == "IRON CONDOR":
        return iron_condor_strikes(spot, symbol)

    elif strategy == "BULL CALL SPREAD":
        return bull_call_spread_strikes(spot, symbol)

    elif strategy == "BEAR PUT SPREAD":
        return bear_put_spread_strikes(spot, symbol)

    elif strategy == "SHORT STRANGLE":
        return short_strangle_strikes(spot, symbol)

    elif strategy == "BUY CALL":
        return {"buy_ce": get_atm_strike(spot, symbol)}

    elif strategy == "BUY PUT":
        return {"buy_pe": get_atm_strike(spot, symbol)}

    else:
        return {}


# =========================================
# BACKWARD COMPATIBILITY
# =========================================
def strike_engine(symbol: str) -> int:
    return get_lot_size(symbol)


def lot_size(symbol: str) -> int:
    return get_lot_size(symbol)
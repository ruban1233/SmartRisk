import math

def get_atm_strike(ltp: float, symbol: str) -> int:
    """
    Calculate ATM strike price based on LTP.
    """

    symbol = symbol.upper()

    if symbol == "NIFTY":
        strike_gap = 50
    elif symbol == "BANKNIFTY":
        strike_gap = 100
    else:
        raise ValueError("Unsupported symbol")

    atm = math.ceil(ltp / strike_gap) * strike_gap
    return int(atm)

import math

def get_atm_strike(ltp, symbol):
    if ltp is None:
        return None

    strike_gap = 50 if symbol == "NIFTY" else 100
    atm = math.ceil(ltp / strike_gap) * strike_gap
    return atm

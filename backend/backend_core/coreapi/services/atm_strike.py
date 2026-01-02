# ATM Strike Calculation Service
# Uses live LTP and pure math
# No NSE, no external API

def get_atm_strike(ltp, step=50):
    """
    ltp: live price (float)
    step: strike gap (50 or 100)
    """
    return round(ltp / step) * step

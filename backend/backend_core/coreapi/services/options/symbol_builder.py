def build_option_symbol(symbol, expiry, strike, option_type):
    """
    Convert:
    28MAR2026 → 28MAR26

    Format:
    NIFTY28MAR26C23000
    """

    # Convert expiry
    day = expiry[:2]
    month = expiry[2:5]
    year = expiry[-2:]  # last 2 digits

    short_expiry = f"{day}{month}{year}"

    if option_type == "CE":
        opt = "C"
    else:
        opt = "P"

    return f"{symbol}{short_expiry}{opt}{int(strike)}"
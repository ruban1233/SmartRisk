def get_option_ltp_from_chain(option):
    """
    Extract price from option chain safely
    Works with multiple API formats
    """

    if not option:
        return None

    return (
        option.get("ltp")
        or option.get("lastPrice")
        or option.get("last_price")
        or option.get("close")
        or option.get("tradedPrice")
        or option.get("premium")
    )
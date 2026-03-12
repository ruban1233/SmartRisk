"""
Strike & Lot Size Engine
------------------------
Provides lot size and basic strike utilities.
Used by SmartRisk option advisor.
"""


def get_lot_size(symbol: str) -> int:
    """
    Returns current lot size for index options.

    NOTE:
    Lot sizes changed effective January 2026 to align with SEBI regulations.
    These values reflect the 2026 index derivative revisions.
    """

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
        # Stocks / ETFs vary widely; return 1 is a safe default for non-F&O
        return 1


# ---------------------------------------
# BACKWARD COMPATIBILITY (DO NOT REMOVE)
# ---------------------------------------

def strike_engine(symbol: str) -> int:
    return get_lot_size(symbol)


def lot_size(symbol: str) -> int:
    return get_lot_size(symbol)

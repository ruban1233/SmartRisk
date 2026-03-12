# coreapi/services/symbol_master.py

"""
Central symbol registry for SmartRisk.

Maps trading symbols to Angel One exchange + symbol tokens
required for API calls.
"""


# =========================================================
# INDEX SYMBOLS
# =========================================================

INDEX_SYMBOL_MAP = {

    "NIFTY": {
        "exchange": "NSE",
        "symbol": "NIFTY",
        "token": "99926000",
    },

    "BANKNIFTY": {
        "exchange": "NSE",
        "symbol": "BANKNIFTY",
        "token": "99926009",
    },

}


# =========================================================
# ETF SYMBOLS
# =========================================================

ETF_SYMBOL_MAP = {

    "NIFTYBEES": {
        "exchange": "NSE",
        "symbol": "NIFTYBEES",
        "token": "10576",
    },

    "BANKBEES": {
        "exchange": "NSE",
        "symbol": "BANKBEES",
        "token": "10579",
    },

    "GOLDBEES": {
        "exchange": "NSE",
        "symbol": "GOLDBEES",
        "token": "10577",
    },

    "SILVERBEES": {
        "exchange": "NSE",
        "symbol": "SILVERBEES",
        "token": "10578",
    },

    "ITBEES": {
        "exchange": "NSE",
        "symbol": "ITBEES",
        "token": "10580",
    },

}


# =========================================================
# EQUITY SYMBOLS
# =========================================================

EQUITY_SYMBOL_MAP = {

    "RELIANCE": {
        "exchange": "NSE",
        "symbol": "RELIANCE",
        "token": "2885",
    },

    "TCS": {
        "exchange": "NSE",
        "symbol": "TCS",
        "token": "11536",
    },

    "INFY": {
        "exchange": "NSE",
        "symbol": "INFY",
        "token": "1594",
    },

    "HDFCBANK": {
        "exchange": "NSE",
        "symbol": "HDFCBANK",
        "token": "1333",
    },

    "ICICIBANK": {
        "exchange": "NSE",
        "symbol": "ICICIBANK",
        "token": "4963",
    },

    "ITC": {
        "exchange": "NSE",
        "symbol": "ITC",
        "token": "1660",
    },

    "LT": {
        "exchange": "NSE",
        "symbol": "LT",
        "token": "11483",
    },

    "MRF": {
        "exchange": "NSE",
        "symbol": "MRF",
        "token": "2277",
    },

}


# =========================================================
# COMBINED SYMBOL MASTER
# =========================================================

SYMBOL_MASTER = {
    **INDEX_SYMBOL_MAP,
    **ETF_SYMBOL_MAP,
    **EQUITY_SYMBOL_MAP,
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_symbol_info(symbol: str):
    """
    Return symbol information dictionary.
    """

    if not symbol:
        return None

    symbol = symbol.upper()

    return SYMBOL_MASTER.get(symbol)


def get_exchange(symbol: str):
    """
    Return exchange for a symbol.
    """

    info = get_symbol_info(symbol)

    if not info:
        return None

    return info.get("exchange")


def get_token(symbol: str):
    """
    Return Angel API token.
    """

    info = get_symbol_info(symbol)

    if not info:
        return None

    return info.get("token")


def is_supported_symbol(symbol: str):
    """
    Check if symbol exists in registry.
    """

    if not symbol:
        return False

    symbol = symbol.upper()

    return symbol in SYMBOL_MASTER
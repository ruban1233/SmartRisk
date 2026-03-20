"""
SmartRisk Symbol Master (FINAL VERSION)

Supports:
✔ Index
✔ Equity
✔ ETF
🔥 Options (NFO) via dynamic master file
"""

import requests

# =========================================================
# STATIC SYMBOLS (YOUR OLD CODE - KEEP)
# =========================================================

INDEX_SYMBOL_MAP = {
    "NIFTY": {"exchange": "NSE", "symbol": "NIFTY", "token": "99926000"},
    "BANKNIFTY": {"exchange": "NSE", "symbol": "BANKNIFTY", "token": "99926009"},
}

ETF_SYMBOL_MAP = {
    "NIFTYBEES": {"exchange": "NSE", "symbol": "NIFTYBEES", "token": "10576"},
    "BANKBEES": {"exchange": "NSE", "symbol": "BANKBEES", "token": "10579"},
    "GOLDBEES": {"exchange": "NSE", "symbol": "GOLDBEES", "token": "10577"},
    "SILVERBEES": {"exchange": "NSE", "symbol": "SILVERBEES", "token": "10578"},
    "ITBEES": {"exchange": "NSE", "symbol": "ITBEES", "token": "10580"},
}

EQUITY_SYMBOL_MAP = {
    "RELIANCE": {"exchange": "NSE", "symbol": "RELIANCE", "token": "2885"},
    "TCS": {"exchange": "NSE", "symbol": "TCS", "token": "11536"},
    "INFY": {"exchange": "NSE", "symbol": "INFY", "token": "1594"},
    "HDFCBANK": {"exchange": "NSE", "symbol": "HDFCBANK", "token": "1333"},
    "ICICIBANK": {"exchange": "NSE", "symbol": "ICICIBANK", "token": "4963"},
    "ITC": {"exchange": "NSE", "symbol": "ITC", "token": "1660"},
    "LT": {"exchange": "NSE", "symbol": "LT", "token": "11483"},
    "MRF": {"exchange": "NSE", "symbol": "MRF", "token": "2277"},
}

SYMBOL_MASTER = {
    **INDEX_SYMBOL_MAP,
    **ETF_SYMBOL_MAP,
    **EQUITY_SYMBOL_MAP,
}

# =========================================================
# 🔥 OPTION MASTER (NEW - IMPORTANT)
# =========================================================

SYMBOL_MASTER_URL = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

_option_cache = None


def load_option_master():
    """Load Angel master file (cached)"""
    global _option_cache

    if _option_cache:
        return _option_cache

    try:
        response = requests.get(SYMBOL_MASTER_URL, timeout=10)
        data = response.json()

        # Filter only NFO options
        _option_cache = [
            item for item in data
            if item.get("exch_seg") == "NFO"
        ]

        return _option_cache

    except Exception as e:
        print("Master Load Error:", e)
        return []


def find_option_token(tradingsymbol):
    """
    Find token for option symbol
    Example:
    NIFTY28MAR26C23000
    """

    data = load_option_master()

    for item in data:
        if item.get("symbol") == tradingsymbol:
            return item.get("token")

    return None


# =========================================================
# HELPER FUNCTIONS (OLD + UPDATED)
# =========================================================

def get_symbol_info(symbol: str):
    if not symbol:
        return None
    return SYMBOL_MASTER.get(symbol.upper())


def get_exchange(symbol: str):
    info = get_symbol_info(symbol)
    return info.get("exchange") if info else None


def get_token(symbol: str):
    info = get_symbol_info(symbol)
    return info.get("token") if info else None


def get_symbol_token(symbol: str):
    """
    Smart unified token getter

    ✔ Spot → static map
    🔥 Option → dynamic lookup
    """

    symbol = symbol.upper()

    # Try static first
    token = get_token(symbol)
    if token:
        return token

    # Try option lookup
    token = find_option_token(symbol)
    return token


def is_supported_symbol(symbol: str):
    return symbol.upper() in SYMBOL_MASTER
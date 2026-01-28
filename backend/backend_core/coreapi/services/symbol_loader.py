import requests

SYMBOL_MASTER_URL = (
    "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"
)

_symbol_cache = None


def load_symbol_master():
    global _symbol_cache

    if _symbol_cache is not None:
        return _symbol_cache

    response = requests.get(SYMBOL_MASTER_URL, timeout=15)
    response.raise_for_status()

    _symbol_cache = response.json()
    return _symbol_cache


def find_symbol(symbol_name, exchange="NSE"):
    symbol_name = symbol_name.upper()
    data = load_symbol_master()

    for row in data:
        if (
            row["name"].upper() == symbol_name
            and row["exch_seg"] == exchange
        ):
            return {
                "exchange": row["exch_seg"],
                "tradingsymbol": row["symbol"],
                "token": row["token"],
            }

    return None

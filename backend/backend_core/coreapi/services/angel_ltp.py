from .angel_login import get_smart

TOKEN_MAP = {
    "NIFTY": ("NSE", "NIFTY 50", "26000"),
    "BANKNIFTY": ("NSE", "NIFTY BANK", "26009"),
}


def get_ltp(symbol):
    symbol = symbol.upper()

    if symbol not in TOKEN_MAP:
        raise ValueError("Unsupported symbol")

    exchange, tradingsymbol, token = TOKEN_MAP[symbol]

    smart = get_smart()
    data = smart.ltpData(exchange, tradingsymbol, token)

    if not data or "data" not in data:
        raise Exception(f"LTP failed: {data}")

    return data["data"]["ltp"]


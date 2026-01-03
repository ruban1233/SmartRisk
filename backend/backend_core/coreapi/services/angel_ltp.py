from coreapi.services.angel_session import get_smart_connection

TOKEN_MAP = {
    "NIFTY": ("NSE", "NIFTY 50", "26000"),
    "BANKNIFTY": ("NSE", "NIFTY BANK", "26009"),
}


def get_ltp(symbol: str) -> float:
    symbol = symbol.upper()

    if symbol not in TOKEN_MAP:
        raise ValueError(f"Unsupported symbol: {symbol}")

    exchange, tradingsymbol, token = TOKEN_MAP[symbol]

    smart = get_smart_connection()
    response = smart.ltpData(exchange, tradingsymbol, token)

    if not response or "data" not in response:
        raise Exception(f"LTP fetch failed: {response}")

    return float(response["data"]["ltp"])

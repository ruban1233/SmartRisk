from coreapi.services.angel_login import get_angel_session
from coreapi.services.symbol_loader import find_symbol


def get_ltp(symbol: str) -> float:
    session = get_angel_session()
    symbol = symbol.upper()

    # Special case: Index
    if symbol in ["NIFTY", "BANKNIFTY"]:
        data = session.ltpData(
            exchange="NSE",
            tradingsymbol=symbol,
            symboltoken="99926000"
        )
        return float(data["data"]["ltp"])

    # Equity / ETF / Stock (dynamic lookup)
    info = find_symbol(symbol)

    if not info:
        raise Exception(f"Symbol not found in Angel master: {symbol}")

    data = session.ltpData(
        exchange=info["exchange"],
        tradingsymbol=info["tradingsymbol"],
        symboltoken=info["token"],
    )

    if not data or not data.get("data"):
        raise Exception(f"LTP fetch failed for {symbol}")

    return float(data["data"]["ltp"])

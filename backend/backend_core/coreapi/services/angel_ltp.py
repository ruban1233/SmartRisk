# coreapi/services/angel_ltp.py

from coreapi.services.symbol_master import (
    EQUITY_SYMBOL_MAP,
    ETF_SYMBOL_MAP
)
from coreapi.services.angel_login import get_angel_session


def get_ltp(symbol: str):
    """
    Fetch LTP using Angel One SmartAPI
    """

    symbol = symbol.upper()
    session = get_angel_session()

    # -------------------------------
    # INDEX
    # -------------------------------
    if symbol in ["NIFTY", "BANKNIFTY"]:
        data = session.ltpData(
            exchange="NSE",
            tradingsymbol=symbol,
            symboltoken="99926000"
        )
        return float(data["data"]["ltp"])

    # -------------------------------
    # EQUITY
    # -------------------------------
    if symbol in EQUITY_SYMBOL_MAP:
        info = EQUITY_SYMBOL_MAP[symbol]
        data = session.ltpData(
            exchange=info["exchange"],
            tradingsymbol=symbol,
            symboltoken=info["token"]
        )
        return float(data["data"]["ltp"])

    # -------------------------------
    # ETF
    # -------------------------------
    if symbol in ETF_SYMBOL_MAP:
        info = ETF_SYMBOL_MAP[symbol]
        data = session.ltpData(
            exchange=info["exchange"],
            tradingsymbol=symbol,
            symboltoken=info["token"]
        )
        return float(data["data"]["ltp"])

    raise Exception(f"LTP not available for symbol: {symbol}")

import time

from coreapi.services.symbol_master import (
    EQUITY_SYMBOL_MAP,
    ETF_SYMBOL_MAP,
    INDEX_SYMBOL_MAP,
)

from coreapi.services.angel_login import get_smart_connection


# ----------------------------------------
# Simple LTP Cache (reduces API calls)
# ----------------------------------------

LTP_CACHE = {}
CACHE_TTL = 5   # seconds


# ----------------------------------------
# Get LTP
# ----------------------------------------

def get_ltp(symbol: str):
    """
    Fetch LTP safely from Angel One SmartAPI.

    Returns:
        float → price
        None → if unavailable
    """

    symbol = symbol.upper().strip()

    try:

        # --------------------------------
        # Check Cache
        # --------------------------------

        now = time.time()

        if symbol in LTP_CACHE:

            cached_price, cached_time = LTP_CACHE[symbol]

            if now - cached_time < CACHE_TTL:
                return cached_price

        # --------------------------------
        # Identify Asset Type
        # --------------------------------

        info = None
        tradingsymbol = None

        if symbol in INDEX_SYMBOL_MAP:
            info = INDEX_SYMBOL_MAP[symbol]
            tradingsymbol = symbol

        elif symbol in ETF_SYMBOL_MAP:
            info = ETF_SYMBOL_MAP[symbol]
            tradingsymbol = symbol

        elif symbol in EQUITY_SYMBOL_MAP:
            info = EQUITY_SYMBOL_MAP[symbol]
            tradingsymbol = f"{symbol}-EQ"

        else:
            print(f"[LTP ERROR] Unsupported symbol: {symbol}")
            return None

        # --------------------------------
        # Validate symbol info
        # --------------------------------

        exchange = info.get("exchange")
        token = info.get("token")

        if not exchange or not token:
            print(f"[LTP ERROR] Missing exchange/token for {symbol}")
            return None

        # --------------------------------
        # Retry Mechanism (Angel API unstable)
        # --------------------------------

        for attempt in range(3):

            try:

                session = get_smart_connection()

                if not session:
                    print("[LTP ERROR] Angel API session unavailable")
                    return None

                response = session.ltpData(
                    exchange=exchange,
                    tradingsymbol=tradingsymbol,
                    symboltoken=token,
                )

                if not response:
                    raise Exception("Empty response")

                if not response.get("status"):
                    raise Exception("API status false")

                data = response.get("data")

                if not data:
                    raise Exception("Missing data")

                ltp = data.get("ltp")

                if ltp is None:
                    raise Exception("Missing LTP")

                price = float(ltp)

                # --------------------------------
                # Save to Cache
                # --------------------------------

                LTP_CACHE[symbol] = (price, now)

                return price

            except Exception as e:

                print(f"[LTP RETRY {attempt+1}] {symbol}: {e}")

                time.sleep(1)

        print(f"[LTP FAILED] {symbol} after retries")

        return None

    except Exception as e:

        print(f"[LTP EXCEPTION] {symbol}: {e}")

        return None
import pandas as pd
from datetime import datetime, timedelta, time
import pytz
from django.core.cache import cache
from .angel_login import get_smartapi_client


CACHE_KEY = "index_candles_{symbol}"
CACHE_TTL = 60  # seconds


def get_index_candles(symbol="NIFTY", interval="FIVE_MINUTE"):
    cache_key = CACHE_KEY.format(symbol=symbol)
    cached_df = cache.get(cache_key)

    if cached_df is not None:
        return cached_df

    smart_api = get_smartapi_client()

    if symbol == "NIFTY":
        exchange = "NSE"
        token = "26000"
    elif symbol == "BANKNIFTY":
        exchange = "NSE"
        token = "26009"
    else:
        raise ValueError("Only NIFTY or BANKNIFTY supported")

    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    market_open = time(9, 15)
    market_close = time(15, 30)

    if now.time() < market_open:
        to_dt = datetime.combine(now.date() - timedelta(days=1), market_close)
    elif now.time() > market_close:
        to_dt = datetime.combine(now.date(), market_close)
    else:
        to_dt = now

    from_dt = to_dt - timedelta(days=1)

    params = {
        "exchange": exchange,
        "symboltoken": token,
        "interval": interval,
        "fromdate": from_dt.strftime("%Y-%m-%d %H:%M"),
        "todate": to_dt.strftime("%Y-%m-%d %H:%M"),
    }

    try:
        response = smart_api.getCandleData(params)
    except Exception as e:
        raise Exception(f"Angel One timeout: {str(e)}")

    if not response or response.get("status") is not True:
        raise Exception(f"Angel candle API error: {response}")

    df = pd.DataFrame(
        response["data"],
        columns=["time", "open", "high", "low", "close", "volume"]
    )

    df["close"] = df["close"].astype(float)

    # ✅ Cache result
    cache.set(cache_key, df, CACHE_TTL)

    return df

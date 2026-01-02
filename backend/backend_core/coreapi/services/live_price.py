from .angel_login import get_session_token
import traceback

# -----------------------------------------------
#   GET LTP FOR ANY SYMBOL
# -----------------------------------------------
def fetch_ltp(obj, exchange, tradingsymbol, token=""):
    try:
        data = obj.ltpData(exchange, tradingsymbol, token)
        return data["data"]["ltp"]
    except Exception:
        return None


# -----------------------------------------------
#   GET ALL IMPORTANT LIVE PRICES
# -----------------------------------------------
def get_all_prices():
    try:
        obj, auth_token, feed_token = get_session_token()

        if obj is None:
            return {
                "status": "error",
                "message": "Login failed",
                "detail": auth_token
            }

        # F&O INDEX TOKENS (SmartAPI standard tokens)
        SYMBOLS = {
            "NIFTY":   {"exchange": "NSE", "token": "256265"},
            "BANKNIFTY": {"exchange": "NSE", "token": "260105"},
            "FINNIFTY":  {"exchange": "NSE", "token": "257801"},
        }

        result = {}

        for name, info in SYMBOLS.items():
            ltp = fetch_ltp(
                obj=obj,
                exchange=info["exchange"],
                tradingsymbol=name,
                token=info["token"]
            )
            result[name] = ltp

        return {
            "status": "success",
            "prices": result
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch live prices",
            "detail": str(e),
            "trace": traceback.format_exc()
        }

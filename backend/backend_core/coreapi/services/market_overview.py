from SmartApi import SmartConnect
import pyotp
import traceback

# -----------------------------
# ANGEL ONE CREDENTIALS
# -----------------------------
CLIENT_ID = "YOUR_CLIENT_ID"
PASSWORD = "YOUR_PASSWORD"
TOTP_SECRET = "YOUR_TOTP_SECRET"
API_KEY = "YOUR_API_KEY"

# -----------------------------
# Create SmartAPI session
# -----------------------------
def smartapi_session():
    try:
        totp = pyotp.TOTP(TOTP_SECRET).now()
        obj = SmartConnect(api_key=API_KEY)
        data = obj.generateSession(CLIENT_ID, PASSWORD, totp)

        if "data" not in data:
            return None, data

        return obj, None
    except Exception as e:
        return None, str(e)

# ----------------------------------------------------
# GET MARKET STATUS (OPEN / CLOSED / PRE-OPEN)
# ----------------------------------------------------
def get_market_status():
    try:
        obj, err = smartapi_session()
        if obj is None:
            return {"status": "error", "detail": err}

        # Angel One API → Exchange status
        exchange_status = obj.marketStatus()

        return {
            "status": "success",
            "market": exchange_status
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch market status",
            "detail": str(e),
            "trace": traceback.format_exc()
        }

from SmartApi import SmartConnect
import pyotp
import traceback
from .greeks_engine import compute_greeks  # your custom Greeks calculator

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


# ------------------------------------------------------
# OPTION CHAIN (SMARTAPI ONLY, NOT NSE)
# ------------------------------------------------------
def get_option_chain(symbol):
    try:
        obj, err = smartapi_session()
        if obj is None:
            return {"status": "error", "detail": err}

        chain = obj.getOptionChain(symbol)

        ce_data = []
        pe_data = []

        for item in chain['data']:
            if item["option_type"] == "CE":
                ce_data.append(item)
            elif item["option_type"] == "PE":
                pe_data.append(item)

        # -----------------------------
        # Compute Greeks for each strike
        # -----------------------------
        for contract in ce_data + pe_data:
            try:
                greeks = compute_greeks(
                    spot=contract["underlying_value"],
                    strike=contract["strike_price"],
                    iv=contract.get("implied_volatility", 0.2),  # fallback if missing
                    time_to_expiry=contract["expiry_days"] / 365,
                    option_type=contract["option_type"]
                )
                contract["greeks"] = greeks
            except Exception as e:
                contract["greeks"] = {"error": str(e)}

        return {
            "status": "success",
            "symbol": symbol,
            "spot": chain["data"][0]["underlying_value"],
            "ce": ce_data,
            "pe": pe_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Failed to fetch option chain",
            "detail": str(e),
            "trace": traceback.format_exc()
        }

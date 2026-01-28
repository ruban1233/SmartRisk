from SmartApi import SmartConnect
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
MPIN = os.getenv("ANGEL_MPIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

_smartapi = None  # singleton session


def get_angel_session():
    global _smartapi

    if _smartapi is not None:
        return _smartapi

    smart = SmartConnect(api_key=API_KEY)

    totp = pyotp.TOTP(TOTP_SECRET).now()
    data = smart.generateSession(CLIENT_ID, MPIN, totp)

    if not data or not data.get("data"):
        raise Exception(f"Angel login failed: {data}")

    jwt = data["data"]["jwtToken"]
    if jwt.startswith("Bearer "):
        jwt = jwt.replace("Bearer ", "")

    smart.setAccessToken(jwt)

    _smartapi = smart
    return _smartapi


# ----------------------------------
# BACKWARD COMPATIBILITY
# ----------------------------------
def get_smartapi_client():
    return get_angel_session()

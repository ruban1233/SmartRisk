from SmartApi import SmartConnect
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
MPIN = os.getenv("ANGEL_MPIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

_smart = None   # singleton

def get_smart_connection():
    global _smart

    if _smart:
        return _smart

    smart = SmartConnect(api_key=API_KEY)

    totp = pyotp.TOTP(TOTP_SECRET).now()
    data = smart.generateSession(CLIENT_ID, MPIN, totp)

    if not data or not data.get("data"):
        raise Exception(f"Angel login failed: {data}")

    jwt = data["data"]["jwtToken"]

    # 🔥 CRITICAL FIX
    if jwt.startswith("Bearer "):
        jwt = jwt.replace("Bearer ", "")

    smart.setAccessToken(jwt)

    _smart = smart
    return smart
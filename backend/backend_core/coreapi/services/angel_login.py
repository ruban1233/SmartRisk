import pyotp
from SmartApi import SmartConnect
from django.conf import settings

smart_session = None


def get_smart_connection():
    global smart_session

    # ✅ reuse session if exists
    if smart_session is not None:
        return smart_session

    api_key = settings.ANGEL_API_KEY
    client_id = settings.ANGEL_CLIENT_ID
    mpin = settings.ANGEL_MPIN
    totp_secret = settings.ANGEL_TOTP_SECRET

    # ✅ generate TOTP
    totp = pyotp.TOTP(totp_secret).now()

    smart = SmartConnect(api_key)

    # ✅ login
    response = smart.generateSession(client_id, mpin, totp)

    if not response.get("status"):
        raise Exception(f"Angel login failed: {response}")

    # =========================
    # 🔥 EXTRACT TOKENS (CRITICAL)
    # =========================
    data = response.get("data", {})

    jwt_token = data.get("jwtToken")
    refresh_token = data.get("refreshToken")
    feed_token = smart.getfeedToken()

    if not jwt_token:
        raise Exception("JWT token missing")

    # =========================
    # 🔥 ATTACH TOKENS TO OBJECT
    # =========================
    smart.jwt_token = jwt_token
    smart.refresh_token = refresh_token
    smart.feed_token = feed_token

    # Debug
    print("✅ SmartAPI Login Success")
    print("JWT:", jwt_token[:20], "...")

    smart_session = smart

    return smart_session
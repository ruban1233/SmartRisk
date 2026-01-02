from SmartApi import SmartConnect
import pyotp

API_KEY = "t8pke43u"
CLIENT_ID = "AAAS174267"
MPIN = "6379"
TOTP_SECRET = "YCH3OKDS4WXJW2OKGXOLPSRGCE"

smart = SmartConnect(api_key=API_KEY)

AUTH_TOKEN = None
FEED_TOKEN = None


def generate_totp():
    totp = pyotp.TOTP(TOTP_SECRET)
    return totp.now()


def create_session():
    global AUTH_TOKEN, FEED_TOKEN

    totp_now = generate_totp()
    data = smart.generateSession(CLIENT_ID, MPIN, totp_now)

    if not data or "data" not in data:
        raise Exception(f"SmartAPI login failed: {data}")

    AUTH_TOKEN = data["data"]["jwtToken"]
    FEED_TOKEN = smart.getfeedToken()

    return AUTH_TOKEN, FEED_TOKEN


def get_smart():
    global AUTH_TOKEN

    if AUTH_TOKEN is None:
        create_session()

    return smart

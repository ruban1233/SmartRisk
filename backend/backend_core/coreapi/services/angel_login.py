import pyotp
from SmartApi import SmartConnect
from django.conf import settings

smart_session = None


def get_smart_connection():
    global smart_session

    if smart_session is not None:
        return smart_session

    api_key = settings.ANGEL_API_KEY
    client_id = settings.ANGEL_CLIENT_ID
    mpin = settings.ANGEL_MPIN
    totp_secret = settings.ANGEL_TOTP_SECRET

    totp = pyotp.TOTP(totp_secret).now()

    smart = SmartConnect(api_key)

    response = smart.generateSession(client_id, mpin, totp)

    if not response["status"]:
        raise Exception("Angel login failed")

    smart_session = smart

    return smart_session
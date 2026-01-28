# coreapi/services/angel_login.py

import os
import pyotp
from dotenv import load_dotenv
from SmartApi import SmartConnect

# Load environment variables
load_dotenv()

# -----------------------------
# SINGLETON SMARTAPI SESSION
# -----------------------------
_smartapi_client = None


def _create_smartapi_session():
    """
    Internal function to create Angel One SmartAPI session
    """
    api_key = os.getenv("ANGEL_API_KEY")
    client_id = os.getenv("ANGEL_CLIENT_ID")
    mpin = os.getenv("ANGEL_MPIN")
    totp_secret = os.getenv("ANGEL_TOTP_SECRET")

    if not all([api_key, client_id, mpin, totp_secret]):
        raise Exception("Angel One credentials missing in .env")

    smart_api = SmartConnect(api_key)

    totp = pyotp.TOTP(totp_secret).now()

    session = smart_api.generateSession(
        client_id,
        mpin,
        totp
    )

    if session.get("status") is False:
        raise Exception("Angel One login failed")

    return smart_api


# =====================================================
# PUBLIC FUNCTIONS (KEEP ALL FOR COMPATIBILITY)
# =====================================================

def get_angel_session():
    """
    Used by angel_ltp.py
    """
    global _smartapi_client
    if _smartapi_client is None:
        _smartapi_client = _create_smartapi_session()
    return _smartapi_client


def get_smartapi_client():
    """
    Used by angel_candles.py and legacy services
    """
    return get_angel_session()

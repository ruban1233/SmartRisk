import requests
from django.conf import settings
from datetime import datetime, timedelta
from coreapi.services.angel_login import get_smart_connection


def get_next_expiry():
    today = datetime.now()
    days = (3 - today.weekday()) % 7
    if days == 0:
        days = 7
    expiry = today + timedelta(days=days)
    return expiry.strftime("%d%b%Y").upper()


def get_option_greeks(symbol="NIFTY", expiry_date=None):

    try:
        obj = get_smart_connection()

        if not obj:
            return {"status": False, "message": "Login failed"}

        jwt_token = getattr(obj, "jwt_token", None)

        if not jwt_token:
            return {"status": False, "message": "Invalid JWT token"}

        if not expiry_date:
            expiry_date = get_next_expiry()

        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-PrivateKey": settings.ANGEL_API_KEY
        }

        payload = {
            "name": symbol,
            "expirydate": expiry_date
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code != 200:
            return {"status": False, "message": "HTTP error", "data": []}

        data = response.json()

        if not data.get("status") or not data.get("data"):
            return {"status": False, "message": "Empty data", "data": []}

        return data

    except Exception as e:
        return {"status": False, "message": str(e), "data": []}


def process_greeks(api_response):
    if not api_response or not api_response.get("status"):
        return []

    processed = []

    for item in api_response.get("data", []):
        try:
            processed.append({
                "strike": float(item["strikePrice"]),
                "option_type": item["optionType"],
                "delta": float(item["delta"]),
                "gamma": float(item["gamma"]),
                "theta": float(item["theta"]),
                "vega": float(item["vega"]),
                "iv": float(item["impliedVolatility"]),
                "volume": float(item["tradeVolume"])
            })
        except:
            continue

    processed.sort(key=lambda x: x["strike"])
    return processed
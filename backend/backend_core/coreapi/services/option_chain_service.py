import requests
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
CACHE_FILE = os.path.join(BASE_DIR, "last_option_chain.json")

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={}"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "data": data
        }, f)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r") as f:
        return json.load(f)


def get_option_chain(symbol: str):
    symbol = symbol.upper()
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        session.get("https://www.nseindia.com", timeout=5)
        response = session.get(NSE_URL.format(symbol), timeout=8)

        if response.status_code != 200:
            raise Exception("NSE blocked")

        json_data = response.json()
        records = json_data["records"]
        underlying = records["underlyingValue"]

        options = []

        for item in records["data"]:
            strike = item["strikePrice"]
            expiry = item["expiryDate"]

            if "CE" in item:
                ce = item["CE"]
                options.append({
                    "strike": strike,
                    "type": "CE",
                    "ltp": ce["lastPrice"],
                    "iv": ce["impliedVolatility"] / 100,
                    "expiry": expiry,
                    "underlying_price": underlying,
                    "source": "LIVE"
                })

            if "PE" in item:
                pe = item["PE"]
                options.append({
                    "strike": strike,
                    "type": "PE",
                    "ltp": pe["lastPrice"],
                    "iv": pe["impliedVolatility"] / 100,
                    "expiry": expiry,
                    "underlying_price": underlying,
                    "source": "LIVE"
                })

        if options:
            save_cache(options)
            return options

    except Exception:
        pass

    # 🔁 FALLBACK — LAST SESSION DATA
    cached = load_cache()
    if cached:
        for opt in cached["data"]:
            opt["source"] = "PREVIOUS_SESSION"
        return cached["data"]

    return []

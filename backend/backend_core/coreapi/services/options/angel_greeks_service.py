import requests
from datetime import datetime
from django.conf import settings
from coreapi.services.angel_login import get_smart_connection


# ============================================================
# EXPIRY HELPERS
# ============================================================

def format_expiry_display(expiry_str):
    try:
        dt = datetime.strptime(expiry_str, "%d%b%Y")
        return dt.strftime("%d %b %Y").upper()
    except:
        return expiry_str


def get_days_to_expiry(expiry_str):
    try:
        dt = datetime.strptime(expiry_str, "%d%b%Y")
        return max(1, (dt.date() - datetime.today().date()).days + 1)
    except:
        return 7


# ============================================================
# 🔥 SMARTAPI GREEKS API
# ============================================================

def get_option_greeks(symbol="NIFTY", expiry_date=None):

    try:
        print("\n🔍 CALLING ANGEL GREEKS API")

        obj = get_smart_connection()

        if not obj:
            print("❌ LOGIN FAILED")
            return None

        jwt_token = getattr(obj, "jwt_token", None)

        if not jwt_token:
            print("❌ NO JWT TOKEN")
            return None

        expiry_date = expiry_date.upper()

        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-UserType": "USER",
            "X-SourceID": "WEB",
            "X-PrivateKey": settings.ANGEL_API_KEY,
        }

        payload = {
            "name": symbol.upper(),
            "expirydate": expiry_date,
        }

        print("📤 PAYLOAD:", payload)

        response = requests.post(url, json=payload, headers=headers, timeout=10)

        print("📥 STATUS:", response.status_code)

        if response.status_code != 200:
            print("❌ BAD STATUS CODE")
            return None

        data = response.json()

        print("📥 DATA COUNT:", len(data.get("data", [])))

        if not data.get("status") or not data.get("data"):
            print("❌ EMPTY DATA FROM API")
            return None

        return data

    except Exception as e:
        print("❌ GREEKS ERROR:", str(e))
        return None


# ============================================================
# PROCESS GREEKS
# ============================================================

def process_greeks(api_response):

    if not api_response:
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
            })
        except:
            continue

    return processed


# ============================================================
# GET ATM GREEKS
# ============================================================

def get_atm_greeks(greeks_list, atm_strike, option_type):

    filtered = [g for g in greeks_list if g["option_type"] == option_type]

    if not filtered:
        return None

    return min(filtered, key=lambda x: abs(x["strike"] - atm_strike))


# ============================================================
# 🔥 MAIN FUNCTION (IMPORTANT)
# ============================================================

def get_real_greeks_for_strategy(symbol, atm_strike, expiry):

    print("\n🚀 FETCHING REAL GREEKS")

    raw = get_option_greeks(symbol, expiry)

    greeks_list = process_greeks(raw)

    if not greeks_list:
        print("⚠ FALLBACK TRIGGERED")

        return {
            "ce_greeks": None,
            "pe_greeks": None,
            "greeks_chain": [],
            "source": "fallback",
        }

    ce = get_atm_greeks(greeks_list, atm_strike, "CE")
    pe = get_atm_greeks(greeks_list, atm_strike, "PE")

    print("✅ USING SMARTAPI GREEKS")

    return {
        "ce_greeks": ce,
        "pe_greeks": pe,
        "greeks_chain": greeks_list,
        "source": "smartapi",
    }
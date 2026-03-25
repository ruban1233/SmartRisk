"""
angel_greeks_service.py
Path: backend/coreapi/services/options/angel_greeks_service.py

✅ Real Greeks from SmartAPI optionGreek endpoint
✅ Auto weekly/monthly expiry engine
✅ Proper JWT token handling
✅ process_greeks returns clean delta/gamma/theta/vega/iv
"""

import requests
from datetime import datetime, timedelta
from django.conf import settings
from coreapi.services.angel_login import get_smart_connection


# ============================================================
# AUTO EXPIRY ENGINE
# ============================================================

def get_nearest_expiry_date(symbol: str = "NIFTY") -> str:
    """
    Returns nearest valid weekly expiry in format: '27MAR2025'

    Expiry days by symbol:
      NIFTY      -> Thursday  (weekday 3)
      BANKNIFTY  -> Wednesday (weekday 2)
      FINNIFTY   -> Tuesday   (weekday 1)
      MIDCPNIFTY -> Tuesday   (weekday 1)
    """
    today = datetime.today()

    weekday_map = {
        "NIFTY":      3,   # Thursday
        "BANKNIFTY":  2,   # Wednesday
        "FINNIFTY":   1,   # Tuesday
        "MIDCPNIFTY": 1,   # Tuesday
    }
    target_weekday = weekday_map.get(symbol.upper(), 3)

    for i in range(8):
        d = today + timedelta(days=i)
        if d.weekday() == target_weekday:
            # If today IS expiry but market already closed (after 3:30 PM), skip
            if d.date() == today.date() and today.hour >= 15 and today.minute >= 30:
                continue
            return d.strftime("%d%b%Y").upper()   # e.g. "27MAR2025"

    # Fallback: 7 days from today
    return (today + timedelta(days=7)).strftime("%d%b%Y").upper()


def get_monthly_expiry(symbol: str = "NIFTY") -> str:
    """Returns last Thursday of current month."""
    today = datetime.today()

    if today.month == 12:
        last_day = datetime(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(today.year, today.month + 1, 1) - timedelta(days=1)

    while last_day.weekday() != 3:   # walk back to Thursday
        last_day -= timedelta(days=1)

    return last_day.strftime("%d%b%Y").upper()


def format_expiry_display(expiry_str: str) -> str:
    """
    '27MAR2025' -> '27 MAR 2025'
    Returns original string if parsing fails.
    """
    try:
        dt = datetime.strptime(expiry_str, "%d%b%Y")
        return dt.strftime("%d %b %Y").upper()
    except Exception:
        return expiry_str


def get_days_to_expiry(expiry_str: str) -> int:
    """How many calendar days until this expiry date."""
    try:
        dt = datetime.strptime(expiry_str, "%d%b%Y")
        return max(1, (dt.date() - datetime.today().date()).days + 1)
    except Exception:
        return 7


# ============================================================
# SMARTAPI GREEKS CALL
# ============================================================

def get_option_greeks(symbol: str = "NIFTY", expiry_date: str = None) -> dict:
    """
    Calls SmartAPI POST /v1/optionGreek
    Returns raw API response dict.

    symbol      : 'NIFTY', 'BANKNIFTY', etc.
    expiry_date : '27MAR2025'  (auto-computed if None)
    """
    try:
        obj = get_smart_connection()

        if not obj:
            return {"status": False, "message": "Login failed", "data": []}

        # Get JWT token
        jwt_token = getattr(obj, "jwt_token", None)
        if not jwt_token:
            return {"status": False, "message": "Invalid JWT token", "data": []}

        # Auto expiry if not provided
        if not expiry_date:
            expiry_date = get_nearest_expiry_date(symbol)

        url = "https://apiconnect.angelone.in/rest/secure/angelbroking/marketData/v1/optionGreek"

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type":  "application/json",
            "Accept":        "application/json",
            "X-UserType":    "USER",
            "X-SourceID":    "WEB",
            "X-PrivateKey":  settings.ANGEL_API_KEY,
        }

        payload = {
            "name":       symbol.upper(),
            "expirydate": expiry_date,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=15)

        if response.status_code != 200:
            return {
                "status":  False,
                "message": f"HTTP {response.status_code}",
                "data":    []
            }

        data = response.json()

        if not data.get("status") or not data.get("data"):
            return {"status": False, "message": "Empty data from API", "data": []}

        return data

    except requests.exceptions.Timeout:
        return {"status": False, "message": "API timeout", "data": []}
    except Exception as e:
        return {"status": False, "message": str(e), "data": []}


# ============================================================
# PROCESS RAW GREEKS RESPONSE
# ============================================================

def process_greeks(api_response: dict) -> list:
    """
    Parse SmartAPI optionGreek response into clean list.

    Each item:
    {
        "strike":      22900.0,
        "option_type": "CE",
        "delta":  0.4924,
        "gamma":  0.0028,
        "theta": -4.0918,
        "vega":   2.2967,
        "iv":    16.33,
        "volume": 24048
    }
    """
    if not api_response or not api_response.get("status"):
        return []

    processed = []

    for item in api_response.get("data", []):
        try:
            processed.append({
                "strike":      float(item["strikePrice"]),
                "option_type": item["optionType"],
                "delta":       round(float(item["delta"]), 4),
                "gamma":       round(float(item["gamma"]), 4),
                "theta":       round(float(item["theta"]), 4),
                "vega":        round(float(item["vega"]),  4),
                "iv":          round(float(item["impliedVolatility"]), 2),
                "volume":      int(float(item.get("tradeVolume", 0))),
            })
        except Exception:
            continue

    processed.sort(key=lambda x: x["strike"])
    return processed


# ============================================================
# GET ATM GREEKS FROM PROCESSED LIST
# ============================================================

def get_atm_greeks_from_chain(greeks_list: list, atm_strike: float, option_type: str = "CE") -> dict:
    """Find greeks for the strike closest to ATM."""
    if not greeks_list:
        return {}

    filtered = [g for g in greeks_list if g.get("option_type") == option_type]
    if not filtered:
        return {}

    return min(filtered, key=lambda x: abs(x.get("strike", 0) - atm_strike))


# ============================================================
# MAIN FUNCTION — used by views.py
# ============================================================

def get_real_greeks_for_strategy(symbol: str, atm_strike: float, expiry: str = None) -> dict:
    """
    Fetches real Greeks for ATM CE and PE from SmartAPI.

    Returns:
    {
        "expiry":         "27MAR2025",
        "expiry_display": "27 MAR 2025",
        "days_to_expiry": 3,
        "ce_greeks":      { strike, delta, gamma, theta, vega, iv },
        "pe_greeks":      { strike, delta, gamma, theta, vega, iv },
        "greeks_chain":   [ ...all strikes... ],
        "source":         "smartapi" | "fallback"
    }
    """
    if not expiry:
        expiry = get_nearest_expiry_date(symbol)

    days_to_expiry = get_days_to_expiry(expiry)
    raw            = get_option_greeks(symbol, expiry)
    greeks_list    = process_greeks(raw)

    if not greeks_list:
        return {
            "expiry":         expiry,
            "expiry_display": format_expiry_display(expiry),
            "days_to_expiry": days_to_expiry,
            "ce_greeks":      None,
            "pe_greeks":      None,
            "greeks_chain":   [],
            "source":         "fallback",
        }

    ce_greeks = get_atm_greeks_from_chain(greeks_list, atm_strike, "CE")
    pe_greeks = get_atm_greeks_from_chain(greeks_list, atm_strike, "PE")

    return {
        "expiry":         expiry,
        "expiry_display": format_expiry_display(expiry),
        "days_to_expiry": days_to_expiry,
        "ce_greeks":      ce_greeks,
        "pe_greeks":      pe_greeks,
        "greeks_chain":   greeks_list,
        "source":         "smartapi",
    }
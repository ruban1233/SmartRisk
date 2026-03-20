# coreapi/services/market_engine.py

def get_iv_level(iv):
    if iv < 15:
        return "low"
    elif iv < 25:
        return "medium"
    return "high"


def build_market_state(candles, option_data):
    trend = "sideways"

    if candles[-1]["close"] > candles[-10]["close"]:
        trend = "bullish"
    elif candles[-1]["close"] < candles[-10]["close"]:
        trend = "bearish"

    iv = option_data.get("avg_iv", 18)
    pcr = option_data.get("pcr", 1.0)

    return {
        "trend": trend,
        "iv": iv,
        "iv_level": get_iv_level(iv),
        "pcr": pcr
    }
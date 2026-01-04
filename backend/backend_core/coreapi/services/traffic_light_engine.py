def traffic_light_engine(sentiment, volatility_level):
    """
    sentiment: Bullish / Bearish / Sideways
    volatility_level: Low / Medium / High
    """

    # 🔴 HIGH RISK CONDITIONS
    if volatility_level == "High":
        return {
            "risk_color": "RED",
            "message": "High volatility – expert traders only"
        }

    # 🟢 SAFE CONDITIONS
    if sentiment == "Sideways" and volatility_level == "Low":
        return {
            "risk_color": "GREEN",
            "message": "Low risk – beginner safe (spreads / option buying)"
        }

    # 🟡 MODERATE RISK (DEFAULT)
    return {
        "risk_color": "YELLOW",
        "message": "Moderate risk – experience required (spreads only)"
    }

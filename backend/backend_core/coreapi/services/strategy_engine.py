def strategy_engine(sentiment, volatility_level, risk_color, capital_info):
    """
    sentiment: Bullish / Bearish / Sideways
    volatility_level: Low / Medium / High
    risk_color: GREEN / YELLOW / RED
    capital_info: output from capital_risk_engine
    """

    sentiment = sentiment.capitalize()
    volatility_level = volatility_level.capitalize()
    risk_color = risk_color.upper()

    # 🔴 Expert only
    if risk_color == "RED":
        return {
            "strategy": "No Trade / Expert Only",
            "reason": "High risk market",
            "allowed_for": "Expert",
            "max_risk": capital_info["max_risk_amount"]
        }

    # 🟢 Beginner safe
    if risk_color == "GREEN":

        if sentiment == "Sideways" and volatility_level == "Low":
            strategy = "Iron Condor (Small)"

        elif sentiment == "Bullish":
            strategy = "Bull Put Spread"

        elif sentiment == "Bearish":
            strategy = "Bear Call Spread"

        else:
            strategy = "No Trade"

        return {
            "strategy": strategy,
            "reason": f"{sentiment} market with {volatility_level} volatility",
            "allowed_for": "Beginner",
            "max_risk": capital_info["max_risk_amount"]
        }

    # 🟡 Intermediate
    if risk_color == "YELLOW":

        if sentiment == "Sideways":
            strategy = "Short Strangle (Hedged)"

        elif sentiment == "Bullish":
            strategy = "Bull Call Spread"

        elif sentiment == "Bearish":
            strategy = "Bear Put Spread"

        else:
            strategy = "No Trade"

        return {
            "strategy": strategy,
            "reason": f"{sentiment} market with {volatility_level} volatility",
            "allowed_for": "Intermediate",
            "max_risk": capital_info["max_risk_amount"]
        }

    return {"strategy": "No Trade"}

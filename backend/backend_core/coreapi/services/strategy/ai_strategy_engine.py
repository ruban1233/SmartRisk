# =========================================================
# 🧠 AI STRATEGY ENGINE (FINAL PRODUCTION)
# =========================================================

def classify_iv(iv):
    if iv < 15:
        return "LOW"
    elif iv < 25:
        return "MEDIUM"
    return "HIGH"


def ai_strategy_decision(capital, trend, iv, days_to_expiry):

    trend = trend.upper()
    iv_level = classify_iv(iv)

    strategy = "NO TRADE"
    reason = ""

    # =========================
    # 🔥 EXPIRY LOGIC (IMPORTANT)
    # =========================
    if days_to_expiry <= 1:
        if trend == "SIDEWAYS":
            return {
                "strategy": "IRON CONDOR",
                "reason": "Expiry day sideways premium decay",
            }
        elif trend == "BULLISH":
            return {
                "strategy": "BUY CALL",
                "reason": "Expiry breakout bullish",
            }
        else:
            return {
                "strategy": "BUY PUT",
                "reason": "Expiry breakout bearish",
            }

    # =========================
    # 🔥 CAPITAL + TREND + IV
    # =========================
    if capital < 10000:
        if trend == "BULLISH":
            strategy = "BUY CALL"
        elif trend == "BEARISH":
            strategy = "BUY PUT"
        else:
            strategy = "AVOID TRADE"

    elif capital < 30000:
        if trend == "BULLISH":
            strategy = "BUY CALL" if iv_level == "LOW" else "BULL CALL SPREAD"
        elif trend == "BEARISH":
            strategy = "BUY PUT" if iv_level == "LOW" else "BEAR PUT SPREAD"
        else:
            strategy = "IRON CONDOR"

    elif capital < 80000:
        if trend == "SIDEWAYS":
            strategy = "IRON CONDOR"
        elif trend == "BULLISH":
            strategy = "BULL CALL SPREAD"
        else:
            strategy = "BEAR PUT SPREAD"

    else:
        if iv_level == "HIGH":
            strategy = "SHORT STRANGLE"
        else:
            strategy = "SHORT STRADDLE"

    return {
        "strategy": strategy,
        "reason": f"{trend} market with {iv_level} IV",
    }


# =========================================================
# 📊 STRATEGY LIST
# =========================================================
def generate_all_strategies(capital):

    if capital < 10000:
        return [
            {"name": "BUY CALL"},
            {"name": "BUY PUT"},
        ]

    elif capital < 30000:
        return [
            {"name": "BUY CALL"},
            {"name": "BUY PUT"},
            {"name": "BULL CALL SPREAD"},
            {"name": "BEAR PUT SPREAD"},
        ]

    elif capital < 80000:
        return [
            {"name": "BULL CALL SPREAD"},
            {"name": "BEAR PUT SPREAD"},
            {"name": "IRON CONDOR"},
        ]

    else:
        return [
            {"name": "IRON CONDOR"},
            {"name": "SHORT STRANGLE"},
            {"name": "SHORT STRADDLE"},
        ]
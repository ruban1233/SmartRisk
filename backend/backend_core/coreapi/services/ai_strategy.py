import traceback

# ------------------------------------------------------------------
#  SIMPLE AI STRATEGY ENGINE (FINAL - 2026)
# ------------------------------------------------------------------
# Inputs:
#   - PCR
#   - IV Trend
#   - Spot vs Max Pain
# Output:
#   - Strategy suggestion + explanation
# ------------------------------------------------------------------


def get_strategy(pcr=1.0, iv=15.0, trend="sideways"):
    """
    pcr: Put/Call Ratio
    iv: implied volatility trend
    trend: bullish / bearish / sideways (from dashboard)
    """

    try:
        suggestion = ""
        reason = ""

        # ------------------------------
        # TREND BASED STRATEGIES
        # ------------------------------
        if trend == "bullish":
            if iv < 12:
                suggestion = "Bull Call Spread"
                reason = "Market bullish with low IV → debit spread safer."
            else:
                suggestion = "Bull Put Spread"
                reason = "Market bullish with high IV → credit spread earns premium."

        elif trend == "bearish":
            if iv < 12:
                suggestion = "Bear Put Spread"
                reason = "Market bearish with low IV → debit spread safer."
            else:
                suggestion = "Bear Call Spread"
                reason = "Market bearish with high IV → credit spread earns premium."

        else:  # sideways
            if iv > 15:
                suggestion = "Short Straddle"
                reason = "Sideways market with high IV → premium selling best."
            else:
                suggestion = "Iron Condor"
                reason = "Sideways + low/medium IV → neutral strategy."

        # ------------------------------
        # PCR BASED ADJUSTMENT
        # ------------------------------
        if pcr > 1.3:
            suggestion += " (PCR indicates extra bullishness)"
        elif pcr < 0.7:
            suggestion += " (PCR indicates extra bearishness)"

        return {
            "status": "success",
            "strategy": suggestion,
            "explanation": reason,
            "inputs": {
                "pcr": pcr,
                "iv": iv,
                "trend": trend
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Strategy engine failed",
            "detail": str(e),
            "trace": traceback.format_exc()
        }

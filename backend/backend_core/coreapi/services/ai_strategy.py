# coreapi/services/ai_strategy.py

import traceback

# ------------------------------------------------------------------
#  SMART RISK - AI STRATEGY ENGINE (FINAL - 2026)
# ------------------------------------------------------------------
# Dynamic strategy selector based on:
#   - PCR
#   - IV
#   - Market Trend
#   - Market State (optional)
# ------------------------------------------------------------------


def get_strategy(pcr=1.0, iv=15.0, trend="sideways"):
    """
    Basic single strategy output (used for direct calls)
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
            suggestion += " (PCR → bullish bias)"
        elif pcr < 0.7:
            suggestion += " (PCR → bearish bias)"

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


# ------------------------------------------------------------------
# 🔥 MAIN FUNCTION REQUIRED BY YOUR PROJECT
# FIXES YOUR IMPORT ERROR
# ------------------------------------------------------------------

def get_strategy_candidates(market_state, capital=0):
    """
    Dynamic multi-strategy selector (USED BY strategy_engine.py)

    market_state = {
        "trend": "bullish/bearish/sideways",
        "volatility": "low/medium/high",
        "pcr": float
    }
    """

    try:
        trend = market_state.get("trend", "sideways")
        iv_level = market_state.get("volatility", "medium")
        pcr = market_state.get("pcr", 1.0)

        strategies = []

        # ------------------------------
        # DYNAMIC STRATEGY LOGIC
        # ------------------------------

        if trend == "bullish":

            if iv_level == "low":
                strategies.append({
                    "name": "Bull Call Spread",
                    "type": "debit",
                    "reason": "Bullish + Low IV → cheap premium buying"
                })

            elif iv_level == "high":
                strategies.append({
                    "name": "Bull Put Spread",
                    "type": "credit",
                    "reason": "Bullish + High IV → premium selling"
                })

        elif trend == "bearish":

            if iv_level == "low":
                strategies.append({
                    "name": "Bear Put Spread",
                    "type": "debit",
                    "reason": "Bearish + Low IV → buy puts"
                })

            elif iv_level == "high":
                strategies.append({
                    "name": "Bear Call Spread",
                    "type": "credit",
                    "reason": "Bearish + High IV → sell calls"
                })

        else:  # SIDEWAYS

            if iv_level == "high":
                strategies.append({
                    "name": "Iron Condor",
                    "type": "neutral",
                    "reason": "Sideways + High IV → range-bound premium selling"
                })

                strategies.append({
                    "name": "Short Straddle",
                    "type": "neutral",
                    "reason": "High IV → aggressive premium selling"
                })

            else:
                strategies.append({
                    "name": "Long Straddle",
                    "type": "neutral",
                    "reason": "Low IV → expect breakout"
                })

        # ------------------------------
        # PCR ADJUSTMENT
        # ------------------------------

        if pcr > 1.3:
            bias = "Bullish PCR confirmation"
        elif pcr < 0.7:
            bias = "Bearish PCR confirmation"
        else:
            bias = "Neutral PCR"

        # ------------------------------
        # POSITION SIZING (DYNAMIC)
        # ------------------------------

        if capital > 0:
            if iv_level == "high":
                allocation = capital * 0.2
            elif iv_level == "medium":
                allocation = capital * 0.3
            else:
                allocation = capital * 0.5
        else:
            allocation = 0

        return {
            "status": "success",
            "market_state": market_state,
            "strategies": strategies,
            "capital_allocation": allocation,
            "pcr_bias": bias
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Strategy candidates failed",
            "detail": str(e),
            "trace": traceback.format_exc()
        }
"""
Traffic Light Engine – SmartRisk
--------------------------------
• Accepts numeric IV or IV level
• Accepts market bias
• NEVER crashes
• Production safe
"""

def traffic_light_signal(market_bias, iv_input):
    """
    iv_input can be:
    - float/int IV value
    - string: LOW / MEDIUM / HIGH
    """

    try:
        # ----------------------------------
        # NORMALIZE IV
        # ----------------------------------
        if isinstance(iv_input, (int, float)):
            iv_value = float(iv_input)
        elif isinstance(iv_input, str):
            iv_map = {
                "LOW": 12,
                "MEDIUM": 18,
                "HIGH": 30
            }
            iv_value = iv_map.get(iv_input.upper(), 18)
        else:
            iv_value = 18

        # ----------------------------------
        # DECISION LOGIC
        # ----------------------------------
        market_bias = str(market_bias).upper()

        if iv_value >= 25:
            return {
                "risk_color": "RED",
                "signal": "🔴 RED",
                "reason": "High volatility – risk elevated"
            }

        if market_bias in ["BEARISH", "STRONG BEARISH"]:
            return {
                "risk_color": "RED",
                "signal": "🔴 RED",
                "reason": "Bearish market conditions"
            }

        if iv_value >= 18:
            return {
                "risk_color": "YELLOW",
                "signal": "🟡 YELLOW",
                "reason": "Moderate volatility – caution required"
            }

        return {
            "risk_color": "GREEN",
            "signal": "🟢 GREEN",
            "reason": "Favorable risk conditions"
        }

    except Exception as e:
        # ----------------------------------
        # FINAL FAILSAFE
        # ----------------------------------
        print("[TRAFFIC LIGHT FALLBACK]", e)

        return {
            "risk_color": "YELLOW",
            "signal": "🟡 YELLOW",
            "reason": "Risk engine fallback"
        }


# ----------------------------------
# BACKWARD COMPATIBILITY
# ----------------------------------
def traffic_light_engine(market_bias, iv_input):
    return traffic_light_signal(market_bias, iv_input)

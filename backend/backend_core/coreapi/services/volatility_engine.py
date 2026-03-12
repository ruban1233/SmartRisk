"""
Volatility Engine – SmartRisk
-----------------------------
• Supports symbol-based IV (future)
• Supports IV list input (current system)
• NEVER crashes
• Normalizes volatility to LOW / MEDIUM / HIGH
"""

def volatility_engine(data):
    """
    data can be:
    1) list of dicts with 'iv' key
    2) a numeric IV
    """

    try:
        # ---------------------------------
        # CASE 1: LIST OF IVs
        # ---------------------------------
        if isinstance(data, list):
            iv_values = []

            for item in data:
                if isinstance(item, dict) and "iv" in item:
                    iv_values.append(float(item["iv"]))

            if not iv_values:
                raise ValueError("No IV values found")

            avg_iv = sum(iv_values) / len(iv_values)

        # ---------------------------------
        # CASE 2: SINGLE IV NUMBER
        # ---------------------------------
        elif isinstance(data, (int, float)):
            avg_iv = float(data)

        else:
            raise ValueError("Unsupported volatility input")

        # ---------------------------------
        # NORMALIZE VOLATILITY
        # ---------------------------------
        if avg_iv < 15:
            level = "LOW"
        elif avg_iv < 25:
            level = "MEDIUM"
        else:
            level = "HIGH"

        return {
            "average_iv": round(avg_iv, 2),
            "level": level
        }

    except Exception as e:
        # ---------------------------------
        # FINAL FAILSAFE
        # ---------------------------------
        print("[VOLATILITY FALLBACK]", e)

        return {
            "average_iv": 18.0,
            "level": "MEDIUM"
        }

"""
IV ENGINE
---------

Purpose:
Analyze Implied Volatility level from option chain.

Output:
Low / Medium / High / Extreme

Used by:
Strategy Builder Engine
"""

def classify_iv(iv_value):

    if iv_value is None:
        return {
            "iv": None,
            "level": "Unknown",
            "suggestion": "IV data unavailable"
        }

    iv = float(iv_value)

    if iv < 12:

        return {
            "iv": iv,
            "level": "Very Low",
            "suggestion": "Options are cheap. Buying strategies preferred."
        }

    elif 12 <= iv < 15:

        return {
            "iv": iv,
            "level": "Low",
            "suggestion": "Buying options strategies preferred."
        }

    elif 15 <= iv < 20:

        return {
            "iv": iv,
            "level": "Medium",
            "suggestion": "Balanced strategies like spreads."
        }

    elif 20 <= iv < 30:

        return {
            "iv": iv,
            "level": "High",
            "suggestion": "Premium selling strategies preferred."
        }

    else:

        return {
            "iv": iv,
            "level": "Extreme",
            "suggestion": "Very high volatility. Risk control required."
        }
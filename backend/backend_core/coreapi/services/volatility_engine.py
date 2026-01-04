def classify_iv(iv_value):
    """
    Classify Implied Volatility level
    """

    if iv_value is None:
        return {
            "iv": None,
            "level": "Unknown",
            "risk": "High"
        }

    if iv_value < 15:
        level = "Low"
        risk = "Low"
    elif 15 <= iv_value <= 25:
        level = "Medium"
        risk = "Moderate"
    else:
        level = "High"
        risk = "High"

    return {
        "iv": round(iv_value, 2),
        "level": level,
        "risk": risk
    }


def volatility_engine(option_chain_data):
    """
    option_chain_data → list of option IVs
    """

    if not option_chain_data:
        return {
            "avg_iv": None,
            "level": "Unknown",
            "risk": "High"
        }

    iv_values = [
        opt["iv"]
        for opt in option_chain_data
        if opt.get("iv") is not None
    ]

    if not iv_values:
        return {
            "avg_iv": None,
            "level": "Unknown",
            "risk": "High"
        }

    avg_iv = sum(iv_values) / len(iv_values)

    classification = classify_iv(avg_iv)

    return {
        "avg_iv": classification["iv"],
        "level": classification["level"],
        "risk": classification["risk"]
    }

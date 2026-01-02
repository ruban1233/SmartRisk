def risk_from_pcr(pcr):
    if pcr > 1.4:
        return 20  # bullish but high risk
    elif pcr > 1.0:
        return 10  # mild bullish, low risk
    elif pcr < 0.6:
        return 25  # strong bearish = high risk
    elif pcr < 1.0:
        return 15  # mild bearish
    return 10    # neutral


def risk_from_trend(trend):
    if trend == "Bullish":
        return 10
    elif trend == "Sideways":
        return 20
    elif trend == "Bearish":
        return 25
    return 20


def support_resistance_risk(support, resistance):
    if support is None or resistance is None:
        return 25  # no data = risky

    gap = resistance - support
    if gap < 200:
        return 15
    elif gap < 400:
        return 10
    else:
        return 20


def final_risk_score(nifty_data, bank_data):
    nifty_score = (
        risk_from_pcr(nifty_data["pcr"])
        + risk_from_trend(nifty_data["trend"])
        + support_resistance_risk(nifty_data["support"], nifty_data["resistance"])
    )

    bank_score = (
        risk_from_pcr(bank_data["pcr"])
        + risk_from_trend(bank_data["trend"])
        + support_resistance_risk(bank_data["support"], bank_data["resistance"])
    )

    total = (nifty_score + bank_score) // 2

    if total <= 20:
        level = "LOW RISK"
    elif total <= 35:
        level = "MODERATE RISK"
    else:
        level = "HIGH RISK"

    return {
        "risk_score": total,
        "risk_level": level,
        "nifty_risk": nifty_score,
        "banknifty_risk": bank_score
    }

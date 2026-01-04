def capital_risk_engine(capital, risk_color):
    """
    capital: int or float (user capital)
    risk_color: GREEN / YELLOW / RED
    """

    if capital <= 0:
        raise ValueError("Capital must be greater than zero")

    risk_color = risk_color.upper()

    if risk_color == "GREEN":
        risk_percent = 5
        max_trades = 2
        rule = "Small lots only. Beginner safe."

    elif risk_color == "YELLOW":
        risk_percent = 10
        max_trades = 3
        rule = "Spreads allowed. Experience required."

    elif risk_color == "RED":
        risk_percent = 20
        max_trades = 5
        rule = "High risk. Expert traders only."

    else:
        raise ValueError("Invalid risk color")

    max_risk_amount = round(capital * risk_percent / 100, 2)

    return {
        "capital": capital,
        "risk_color": risk_color,
        "risk_percent": risk_percent,
        "max_risk_amount": max_risk_amount,
        "max_trades_per_day": max_trades,
        "position_size_rule": rule
    }

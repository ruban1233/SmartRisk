"""
Capital Risk Engine
-------------------
Defines how much capital can be risked per trade.
Used by SmartRisk strategy & option advisor engines.
"""


def get_allowed_loss(capital: int) -> float:
    """
    Returns maximum allowed loss for a single trade
    based on capital size.

    This is RISK MANAGEMENT, not prediction.
    """

    # Beginner safety rules
    if capital < 50000:
        return round(capital * 0.05, 2)   # 5% risk
    elif capital < 300000:
        return round(capital * 0.04, 2)   # 4% risk
    elif capital < 1500000:
        return round(capital * 0.03, 2)   # 3% risk
    else:
        return round(capital * 0.02, 2)   # 2% risk


# ---------------------------------------
# BACKWARD COMPATIBILITY (DO NOT REMOVE)
# ---------------------------------------

def capital_risk_engine(capital: int) -> float:
    return get_allowed_loss(capital)


def allowed_loss(capital: int) -> float:
    return get_allowed_loss(capital)

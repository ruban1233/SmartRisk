"""
Greeks Engine – SmartRisk
------------------------
• Black–Scholes based Greeks
• Used across SmartRisk engines
• Production-safe
• Backward compatible
"""

import math
from scipy.stats import norm


def compute_greeks(S, K, T, r=0.05, sigma=0.2, option_type="CE"):
    """
    Compute option Greeks using Black–Scholes formula.

    Parameters:
    S : float
        Spot price
    K : float
        Strike price
    T : float
        Time to expiry (in years)
    r : float
        Risk-free interest rate
    sigma : float
        Implied volatility (decimal, e.g. 0.18)
    option_type : str
        'CE' for Call, 'PE' for Put
    """

    # Safety guards
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0
        }

    d1 = (
        math.log(S / K) +
        (r + 0.5 * sigma ** 2) * T
    ) / (sigma * math.sqrt(T))

    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "CE":
        delta = norm.cdf(d1)
    else:
        delta = -norm.cdf(-d1)

    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))

    theta = (
        -(S * norm.pdf(d1) * sigma) /
        (2 * math.sqrt(T))
    )

    vega = S * norm.pdf(d1) * math.sqrt(T)

    return {
        "delta": round(float(delta), 4),
        "gamma": round(float(gamma), 6),
        "theta": round(float(theta), 2),
        "vega": round(float(vega), 2)
    }


# -------------------------------------------------
# BACKWARD COMPATIBILITY (VERY IMPORTANT)
# -------------------------------------------------
# views.py and older engines import calculate_greeks
# DO NOT REMOVE THIS LINE
calculate_greeks = compute_greeks

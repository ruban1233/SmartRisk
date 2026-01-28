import math
from scipy.stats import norm

# RBI risk-free rate (approx)
RISK_FREE_RATE = 0.065  # 6.5%


def calculate_greeks(S, K, T, sigma, option_type="CE"):
    """
    Calculate Black-Scholes Greeks

    S = Spot price
    K = Strike price
    T = Time to expiry (in years)
    sigma = Implied volatility (decimal)
    option_type = CE / PE
    """

    if T <= 0 or sigma <= 0:
        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0
        }

    d1 = (math.log(S / K) + (RISK_FREE_RATE + 0.5 * sigma ** 2) * T) / (
        sigma * math.sqrt(T)
    )
    d2 = d1 - sigma * math.sqrt(T)

    pdf_d1 = norm.pdf(d1)

    if option_type == "CE":
        delta = norm.cdf(d1)
        theta = (
            -(S * pdf_d1 * sigma) / (2 * math.sqrt(T))
            - RISK_FREE_RATE * K * math.exp(-RISK_FREE_RATE * T) * norm.cdf(d2)
        ) / 365
    else:
        delta = -norm.cdf(-d1)
        theta = (
            -(S * pdf_d1 * sigma) / (2 * math.sqrt(T))
            + RISK_FREE_RATE * K * math.exp(-RISK_FREE_RATE * T) * norm.cdf(-d2)
        ) / 365

    gamma = pdf_d1 / (S * sigma * math.sqrt(T))
    vega = (S * pdf_d1 * math.sqrt(T)) / 100

    return {
        "delta": round(delta, 4),
        "gamma": round(gamma, 4),
        "theta": round(theta, 4),
        "vega": round(vega, 4),
    }

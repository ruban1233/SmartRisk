import math
from scipy.stats import norm


def compute_greeks(S, K, T, r, sigma, option_type="CE"):

    try:
        d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        if option_type == "CE":
            delta = norm.cdf(d1)
        else:
            delta = -norm.cdf(-d1)

        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))

        theta = (
            -(S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T))
            - r * K * math.exp(-r * T) * norm.cdf(d2)
        )

        vega = S * norm.pdf(d1) * math.sqrt(T)

        # ✅ FIX SCALING (VERY IMPORTANT)
        theta = theta / 365
        vega = vega / 100

        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega
        }

    except:
        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0
        }
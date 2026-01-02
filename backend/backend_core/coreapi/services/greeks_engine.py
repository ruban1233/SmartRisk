import math

# --------------------------------------------
# Black–Scholes Greeks Calculator (Final 2026)
# --------------------------------------------

def compute_greeks(spot, strike, iv, time_to_expiry, option_type):
    """
    spot: underlying price
    strike: strike price
    iv: implied volatility (0.0 — 1.0)
    time_to_expiry: in years (eg: 5 days = 5/365)
    option_type: "CE" or "PE"
    """

    if spot <= 0 or strike <= 0 or time_to_expiry <= 0 or iv <= 0:
        return {
            "delta": 0,
            "gamma": 0,
            "theta": 0,
            "vega": 0,
            "rho": 0
        }

    r = 0.10  # risk-free rate (10%)
    sigma = iv

    # d1 and d2 (Black-Scholes)
    d1 = (math.log(spot / strike) + (r + sigma * sigma / 2) * time_to_expiry) / (sigma * math.sqrt(time_to_expiry))
    d2 = d1 - sigma * math.sqrt(time_to_expiry)

    # normal distribution functions
    def N(x):
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    def n(x):
        return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x * x)

    # Greeks calculations
    gamma = n(d1) / (spot * sigma * math.sqrt(time_to_expiry))
    vega = spot * n(d1) * math.sqrt(time_to_expiry) / 100

    if option_type == "CE":
        delta = N(d1)
        theta = (
            -(spot * n(d1) * sigma) / (2 * math.sqrt(time_to_expiry))
            - r * strike * math.exp(-r * time_to_expiry) * N(d2)
        ) / 365
        rho = strike * time_to_expiry * math.exp(-r * time_to_expiry) * N(d2) / 100
    else:  # PE
        delta = -N(-d1)
        theta = (
            -(spot * n(d1) * sigma) / (2 * math.sqrt(time_to_expiry))
            + r * strike * math.exp(-r * time_to_expiry) * N(-d2)
        ) / 365
        rho = -strike * time_to_expiry * math.exp(-r * time_to_expiry) * N(-d2) / 100

    return {
        "delta": round(delta, 5),
        "gamma": round(gamma, 5),
        "theta": round(theta, 5),
        "vega": round(vega, 5),
        "rho": round(rho, 5)
    }

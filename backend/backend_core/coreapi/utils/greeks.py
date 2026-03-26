import math
from coreapi.services.iv_engine import calculate_iv


def norm_cdf(x):
    return (1.0 + math.erf(x / math.sqrt(2))) / 2


def norm_pdf(x):
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


def calculate_greeks(option, spot, strike, days_to_expiry):

    if not option:
        return None

    try:
        ltp = option.get("ltp")

        if not ltp or ltp <= 0:
            return None

        # Convert time
        T = days_to_expiry / 365
        r = 0.05

        option_type = option.get("option_type")

        # 🔥 REAL IV CALCULATION
        sigma = calculate_iv(
            option_price=ltp,
            S=spot,
            K=strike,
            T=T,
            r=r,
            option_type=option_type
        )

        d1 = (math.log(spot / strike) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)

        # ======================
        # GREEKS
        # ======================

        if option_type == "CE":
            delta = norm_cdf(d1)
        else:
            delta = norm_cdf(d1) - 1

        gamma = norm_pdf(d1) / (spot * sigma * math.sqrt(T))

        theta = (
            - (spot * norm_pdf(d1) * sigma) / (2 * math.sqrt(T))
            - r * strike * math.exp(-r * T) * norm_cdf(d2)
        )

        vega = spot * norm_pdf(d1) * math.sqrt(T)

        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "iv": round(sigma * 100, 2)   # % format
        }

    except Exception as e:
        print("❌ GREEKS ERROR:", e)
        return None
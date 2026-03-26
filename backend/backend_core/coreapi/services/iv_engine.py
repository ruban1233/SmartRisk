import math

# =========================
# NORMAL DISTRIBUTION
# =========================

def norm_cdf(x):
    return (1.0 + math.erf(x / math.sqrt(2))) / 2

def norm_pdf(x):
    return math.exp(-0.5 * x**2) / math.sqrt(2 * math.pi)


# =========================
# BLACK-SCHOLES PRICE
# =========================

def black_scholes(S, K, T, r, sigma, option_type):
    if T <= 0:
        return 0

    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == "CE":
        return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)
    else:
        return K * math.exp(-r * T) * norm_cdf(-d2) - S * norm_cdf(-d1)


# =========================
# VEGA
# =========================

def vega(S, K, T, r, sigma):
    if T <= 0:
        return 0

    d1 = (math.log(S / K) + (r + sigma**2 / 2) * T) / (sigma * math.sqrt(T))
    return S * math.sqrt(T) * norm_pdf(d1)


# =========================
# IMPLIED VOLATILITY
# =========================

def calculate_iv(option_price, S, K, T, r, option_type):
    sigma = 0.2  # initial guess

    for _ in range(100):
        price = black_scholes(S, K, T, r, sigma, option_type)
        v = vega(S, K, T, r, sigma)

        if v == 0:
            break

        sigma = sigma - (price - option_price) / v

    return abs(sigma)
# ===============================
# IV CLASSIFICATION
# ===============================

def classify_iv(iv_value):

    if iv_value is None:
        return {
            "iv": None,
            "level": "Unknown",
            "suggestion": "IV data unavailable"
        }

    iv = float(iv_value)

    if iv < 12:
        return {"iv": iv, "level": "Very Low", "suggestion": "Buy options"}

    elif iv < 15:
        return {"iv": iv, "level": "Low", "suggestion": "Buy options"}

    elif iv < 20:
        return {"iv": iv, "level": "Medium", "suggestion": "Use spreads"}

    elif iv < 30:
        return {"iv": iv, "level": "High", "suggestion": "Sell options"}

    else:
        return {"iv": iv, "level": "Extreme", "suggestion": "High risk"}
import math

def calculate_greeks(option):
    if not option:
        return None

    # Mock Greeks for now (you can replace with proper formulas)
    return {
        "delta": round(option.get("impliedVolatility", 0) / 100, 2),
        "gamma": 0.06,
        "theta": -10.5,
        "vega": 12.4,
        "rho": 5.2
    }
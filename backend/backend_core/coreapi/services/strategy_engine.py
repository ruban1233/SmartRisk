"""
SmartRisk – Option Strategy Engine (PRODUCTION SAFE)
---------------------------------------------------
• Uses LIVE option chain when available
• Uses cached option chain when market is closed
• FINAL fallback to Angel One LTP
• Dynamic lot size
• Greeks via Black–Scholes
• Capital-aware, risk-first
• Advisory-only (NO execution)
"""

from datetime import datetime, date

# =========================
# CORE DEPENDENCIES
# =========================
from coreapi.services.option_chain_service import get_option_chain
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.strike_engine import get_lot_size
from coreapi.services.capital_risk_engine import get_allowed_loss
from coreapi.services.traffic_light_engine import traffic_light_signal
from coreapi.services.greeks_engine import compute_greeks
from coreapi.services.expiry_engine import get_next_weekly_expiry

# =========================
# MAIN ENGINE
# =========================
def option_advisor_engine(symbol: str, capital: float):
    symbol = symbol.upper()
    capital = float(capital)

    # ---------------------------------
    # BASIC CAPITAL GUARD
    # ---------------------------------
    if capital < 10000:
        return {
            "symbol": symbol,
            "capital": capital,
            "traffic_light": "🔴 RED",
            "advice": "NO TRADE",
            "reason": "Minimum capital ₹10,000 required for options"
        }

    # ---------------------------------
    # LOT SIZE & RISK LIMIT
    # ---------------------------------
    lot_size = get_lot_size(symbol)
    allowed_loss = get_allowed_loss(capital)

    # ---------------------------------
    # TRY OPTION CHAIN (LIVE / CACHED)
    # ---------------------------------
    option_chain = None
    try:
        option_chain = get_option_chain(symbol)
    except Exception as e:
        option_chain = None

    # ---------------------------------
    # OPTION DATA SELECTION
    # ---------------------------------
    if option_chain:
        # Underlying price from option chain
        underlying_price = option_chain[0].get("underlying_price")

        # Choose ATM option
        option_chain.sort(
            key=lambda x: abs(x.get("strike", 0) - underlying_price)
        )
        selected = option_chain[0]

        strike_price = selected["strike"]
        premium = float(selected["ltp"])
        expiry = selected["expiry"]
        option_type = selected["type"]  # CE / PE
        iv = round(float(selected["iv"]) * 100, 2)
        data_source = selected.get("source", "OPTION_CHAIN")

        market_status = (
            "MARKET OPEN"
            if data_source == "LIVE"
            else "MARKET CLOSED (Last traded option data)"
        )

    else:
        # ---------------------------------
        # FINAL FALLBACK — ANGEL LTP
        # ---------------------------------
        underlying_price = float(get_ltp(symbol))

        # ATM rounding
        step = 50 if symbol in ["NIFTY", "BANKNIFTY"] else 100
        strike_price = round(underlying_price / step) * step

        # Conservative premium estimate
        premium = round(underlying_price * 0.004, 2)

        expiry = get_next_weekly_expiry()
        option_type = "CE"
        iv = 18.0

        data_source = "ANGEL_LTP_FALLBACK"
        market_status = "MARKET CLOSED (Fallback using underlying LTP)"

    # ---------------------------------
    # CAPITAL CHECK
    # ---------------------------------
    capital_required = round(premium * lot_size, 2)

    if capital_required > capital:
        return {
            "symbol": symbol,
            "capital": capital,
            "market_status": market_status,
            "traffic_light": "🟡 YELLOW",
            "advice": "NO SAFE OPTION",
            "reason": "Option premium exceeds available capital",
            "education": "Increase capital or wait for lower premium"
        }

    # ---------------------------------
    # MARKET BIAS & RISK SIGNAL
    # ---------------------------------
    if iv < 15:
        market_bias = "SIDEWAYS"
    elif iv < 22:
        market_bias = "MILD BULLISH"
    else:
        market_bias = "HIGH VOLATILITY"

    traffic_light = traffic_light_signal(market_bias, iv)

    # ---------------------------------
    # TIME TO EXPIRY
    # ---------------------------------
    try:
        expiry_date = datetime.strptime(expiry, "%d-%b-%Y").date()
        days_to_expiry = max((expiry_date - date.today()).days, 1)
    except Exception:
        days_to_expiry = 7

    T = days_to_expiry / 365

    # ---------------------------------
    # GREEKS (BLACK–SCHOLES)
    # ---------------------------------
    greeks = compute_greeks(
        S=underlying_price,
        K=strike_price,
        T=T,
        r=0.05,
        sigma=iv / 100,
        option_type=option_type
    )

    # ---------------------------------
    # RISK METRICS
    # ---------------------------------
    max_loss = capital_required

    break_even = (
        strike_price + premium
        if option_type == "CE"
        else strike_price - premium
    )

    risk_fit = "OK" if max_loss <= allowed_loss else "HIGH"

    # ---------------------------------
    # FINAL RESPONSE
    # ---------------------------------
    return {
        "symbol": symbol,
        "capital": capital,
        "market_status": market_status,
        "data_source": data_source,
        "underlying_price": round(underlying_price, 2),
        "market_bias": market_bias,
        "volatility": {
            "iv": iv,
            "iv_zone": (
                "LOW" if iv < 15 else
                "NORMAL" if iv < 25 else
                "HIGH"
            )
        },
        "traffic_light": traffic_light,
        "strategy": {
            "name": "LONG CALL" if option_type == "CE" else "LONG PUT",
            "option_type": option_type,
            "expiry": expiry,
            "strike_price": strike_price,
            "premium": premium,
            "lot_size": lot_size,
            "capital_required": capital_required,
            "max_loss": max_loss,
            "max_profit": "Unlimited",
            "break_even": round(break_even, 2),
            "risk_fit": risk_fit
        },
        "greeks": greeks,
        "risk_note": (
            "Options can lose 100% of premium. "
            "Theta decay, volatility and liquidity affect outcomes."
        ),
        "education": (
            "SmartRisk is a risk-first advisory system. "
            "Uses real broker data with safe fallbacks. "
            "No prediction, no guaranteed profit."
        )
    }


# ---------------------------------
# BACKWARD COMPATIBILITY (IMPORTANT)
# ---------------------------------
strategy_engine = option_advisor_engine

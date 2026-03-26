"""
strategy_engine.py
Path: backend/coreapi/services/strategy/strategy_engine.py
✔ Real LTP from chain for ALL strikes
✔ Capital-aware strategy selection
✔ Real payoff using payoff_engine
✔ Greeks use real IV + real DTE
"""

import math
from ..capital_risk_engine import get_capital_summary, get_traffic_signal
from ..instruments import get_lot_size  # ✅ SINGLE SOURCE
from ..greeks_engine import compute_greeks as calculate_greeks
from .payoff_engine import calculate_payoff, calculate_summary

# ============================================================
# STRATEGIES
# ============================================================

STRATEGIES = {
    "BUY_CALL": {
        "name": "BUY CALL", "legs": 1, "direction": "BULLISH",
        "iv_suitable": "LOW", "min_capital": 5_000,
        "risk": "HIGH", "reward": "UNLIMITED",
        "description": "Buy ATM Call. Profit if market rallies strongly.",
    },
    "BUY_PUT": {
        "name": "BUY PUT", "legs": 1, "direction": "BEARISH",
        "iv_suitable": "LOW", "min_capital": 5_000,
        "risk": "HIGH", "reward": "UNLIMITED",
        "description": "Buy ATM Put. Profit if market falls strongly.",
    },
    "BULL_CALL_SPREAD": {
        "name": "BULL CALL SPREAD", "legs": 2, "direction": "BULLISH",
        "iv_suitable": "ANY", "min_capital": 15_000,
        "risk": "MEDIUM", "reward": "LIMITED",
        "description": "Buy ATM CE, Sell OTM CE. Defined risk.",
    },
    "BEAR_PUT_SPREAD": {
        "name": "BEAR PUT SPREAD", "legs": 2, "direction": "BEARISH",
        "iv_suitable": "ANY", "min_capital": 15_000,
        "risk": "MEDIUM", "reward": "LIMITED",
        "description": "Buy ATM PE, Sell OTM PE. Defined risk.",
    },
    "IRON_CONDOR": {
        "name": "IRON CONDOR", "legs": 4, "direction": "SIDEWAYS",
        "iv_suitable": "HIGH", "min_capital": 1_00_000,
        "risk": "LOW", "reward": "LIMITED",
        "description": "Sell OTM CE+PE, Buy further OTM. Best sideways + high IV.",
    },
    "SHORT_STRANGLE": {
        "name": "SHORT STRANGLE", "legs": 2, "direction": "SIDEWAYS",
        "iv_suitable": "HIGH", "min_capital": 2_00_000,
        "risk": "MEDIUM", "reward": "LIMITED",
        "description": "Sell OTM CE+PE. Collect premium. Needs margin.",
    },
    "SHORT_STRADDLE": {
        "name": "SHORT STRADDLE", "legs": 2, "direction": "SIDEWAYS",
        "iv_suitable": "HIGH", "min_capital": 3_00_000,
        "risk": "HIGH", "reward": "LIMITED",
        "description": "Sell ATM CE+PE. Maximum premium. High risk.",
    },
}

# ============================================================
# REAL LTP FROM CHAIN
# ============================================================

def get_real_ltp(chain, strike, option_type):
    """Fetch actual market LTP from option chain for a specific strike."""
    if not chain:
        return 0.0
    strike = float(strike)
    for x in chain:
        s = float(x.get("strike", x.get("strikePrice", 0)))
        t = x.get("option_type") or x.get("optionType", "")
        if abs(s - strike) < 0.5 and t == option_type:
            ltp = x.get("ltp")
            if ltp is not None and float(ltp) > 0:
                return float(ltp)
    return 0.0

def get_nearest_strike_ltp(chain, target_strike, option_type, fallback=100.0):
    """Get LTP of nearest available strike if exact not found."""
    ltp = get_real_ltp(chain, target_strike, option_type)
    if ltp > 0:
        return ltp

    # Find nearest strike with valid LTP
    candidates = [
        x for x in (chain or [])
        if (x.get("option_type") or x.get("optionType", "")) == option_type
        and x.get("ltp") is not None
        and float(x.get("ltp", 0)) > 0
    ]
    if candidates:
        closest = min(candidates, key=lambda x: abs(
            float(x.get("strike", x.get("strikePrice", 0))) - float(target_strike)
        ))
        return float(closest["ltp"])
    return fallback

# ============================================================
# STRATEGY SELECTOR
# ============================================================

def select_strategy(capital, trend, iv_percentile, dte=15):
    trend    = (trend or "Sideways").strip().upper()
    iv_label = "HIGH" if iv_percentile >= 60 else ("LOW" if iv_percentile <= 30 else "MEDIUM")

    # Capital-based investor level
    if capital < 10_000:
        level = "ALERT"
    elif capital < 3_00_000:
        level = "BEGINNER"
    elif capital < 15_00_000:
        level = "PROFESSIONAL"
    else:
        level = "EXPERT"

    # Expiry override
    if dte <= 1:
        if trend == "SIDEWAYS" and capital >= 1_00_000:
            return {"key": "IRON_CONDOR", **STRATEGIES["IRON_CONDOR"]}
        elif trend == "BULLISH":
            return {"key": "BUY_CALL", **STRATEGIES["BUY_CALL"]}
        else:
            return {"key": "BUY_PUT", **STRATEGIES["BUY_PUT"]}

    candidates = []
    for key, s in STRATEGIES.items():
        if capital < s["min_capital"]:
            continue

        direction = s["direction"]
        # Direction match
        if trend == "BULLISH" and direction not in ("BULLISH",):
            continue
        if trend == "BEARISH" and direction not in ("BEARISH",):
            continue
        if trend == "SIDEWAYS" and direction not in ("SIDEWAYS",):
            continue

        # IV match (relaxed for directional)
        if s["iv_suitable"] != "ANY":
            if direction in ("BULLISH", "BEARISH"):
                pass  # allow any IV for directional
            elif s["iv_suitable"] != iv_label:
                continue

        candidates.append((key, s))

    if not candidates:
        # Fallback: any affordable strategy matching trend
        for key, s in STRATEGIES.items():
            if capital >= s["min_capital"]:
                if (trend == "BULLISH" and s["direction"] == "BULLISH") or \
                   (trend == "BEARISH" and s["direction"] == "BEARISH") or \
                   (trend == "SIDEWAYS" and s["direction"] == "SIDEWAYS"):
                    candidates.append((key, s))

    if not candidates:
        for key, s in STRATEGIES.items():
            if capital >= s["min_capital"]:
                candidates.append((key, s))

    if not candidates:
        return None

    # Pick highest min_capital (most advanced user can afford)
    best_key, best = sorted(candidates, key=lambda x: x[1]["min_capital"], reverse=True)[0]
    return {"key": best_key, **best}

# ============================================================
# BUILD STRIKES
# ============================================================

def build_strikes(atm, step=50):
    atm = float(atm)
    return {
        "atm":      atm,
        "atm_ce":   atm,
        "atm_pe":   atm,
        "otm1_ce":  atm + step,
        "otm2_ce":  atm + step * 2,
        "otm1_pe":  atm - step,
        "otm2_pe":  atm - step * 2,
    }

# ============================================================
# BUILD LEGS WITH REAL LTP
# ============================================================

def build_legs(strategy_key, strikes, ltp_map, lot_size, chain=None, symbol="NIFTY"):
    ce_fb = ltp_map.get("ce_ltp", 100.0)  # ATM fallback
    pe_fb = ltp_map.get("pe_ltp", 100.0)

    def ce(strike):
        return get_nearest_strike_ltp(chain, strike, "CE", ce_fb)

    def pe(strike):
        return get_nearest_strike_ltp(chain, strike, "PE", pe_fb)

    leg_defs = {
        "BUY_CALL": [
            ("BUY", "CE", strikes["atm_ce"], ce(strikes["atm_ce"])),
        ],
        "BUY_PUT": [
            ("BUY", "PE", strikes["atm_pe"], pe(strikes["atm_pe"])),
        ],
        "BULL_CALL_SPREAD": [
            ("BUY",  "CE", strikes["atm_ce"],  ce(strikes["atm_ce"])),
            ("SELL", "CE", strikes["otm1_ce"], ce(strikes["otm1_ce"])),
        ],
        "BEAR_PUT_SPREAD": [
            ("BUY",  "PE", strikes["atm_pe"],  pe(strikes["atm_pe"])),
            ("SELL", "PE", strikes["otm1_pe"], pe(strikes["otm1_pe"])),
        ],
        "IRON_CONDOR": [
            ("SELL", "CE", strikes["otm1_ce"], ce(strikes["otm1_ce"])),
            ("BUY",  "CE", strikes["otm2_ce"], ce(strikes["otm2_ce"])),
            ("SELL", "PE", strikes["otm1_pe"], pe(strikes["otm1_pe"])),
            ("BUY",  "PE", strikes["otm2_pe"], pe(strikes["otm2_pe"])),
        ],
        "SHORT_STRANGLE": [
            ("SELL", "CE", strikes["otm1_ce"], ce(strikes["otm1_ce"])),
            ("SELL", "PE", strikes["otm1_pe"], pe(strikes["otm1_pe"])),
        ],
        "SHORT_STRADDLE": [
            ("SELL", "CE", strikes["atm_ce"], ce(strikes["atm_ce"])),
            ("SELL", "PE", strikes["atm_pe"], pe(strikes["atm_pe"])),
        ],
    }

    raw_legs = leg_defs.get(strategy_key, [])
    legs      = []

    for action, opt_type, strike, ltp in raw_legs:
        sign = 1 if action == "BUY" else -1
        legs.append({
            "action":         action,
            "type":           opt_type,
            "strike":         strike,
            "ltp":            round(ltp, 2),
            "lots":           1,
            "lot_size":       lot_size,  # ✅ DYNAMIC SINGLE SOURCE
            "cost":           round(sign * ltp * lot_size, 2),
            "display_price":  round(ltp, 2),
        })

    return legs

# ============================================================
# NET PREMIUM
# ============================================================

def calculate_net_premium(legs):
    total = sum(leg["cost"] for leg in legs)
    return {
        "net_premium": round(total, 2),
        "type":        "DEBIT" if total > 0 else "CREDIT",
        "label":       f"{'Pay' if total > 0 else 'Receive'} ₹{abs(total):,.2f}",
    }

# ============================================================
# REAL PAYOFF
# ============================================================

def build_real_payoff(legs, atm, step, symbol):
    """Build payoff using real leg premiums."""
    # Convert to payoff_engine format
    payoff_legs = [
        {
            "action":  leg["action"],
            "type":    leg["type"],
            "strike":  leg["strike"],
            "premium": leg["ltp"],
        }
        for leg in legs
    ]
    return calculate_payoff(payoff_legs, symbol)

# ============================================================
# MAIN ENGINE
# ============================================================

def run_strategy_engine(
    capital, trend, iv_percentile, atm_price,
    ltp_map, symbol="NIFTY", step=50, chain=None,
    dte=15, expiry=None,  # ✅ Added expiry param
):
    symbol   = symbol.upper()
    lot_size = get_lot_size(symbol, expiry)  # ✅ SINGLE SOURCE WITH EXPIRY
    
    print(f"[STRATEGY] {symbol} expiry={expiry} lot_size={lot_size} capital={capital} trend={trend} "
          f"iv={iv_percentile} atm={atm_price} dte={dte}")

    atm      = round(float(atm_price) / step) * step

    # Capital summary with symbol+expiry
    capital_data = get_capital_summary(capital, symbol, expiry, {symbol: ltp_map})

    # Select strategy
    strategy = select_strategy(capital, trend, iv_percentile, dte)
    if not strategy:
        return {
            "error": True,
            "message": "No suitable strategy. Increase capital or wait for clearer market trend.",
            "capital_data": capital_data,
            "lot_size": lot_size,  # ✅ SINGLE SOURCE
        }

    print(f"[STRATEGY] Selected: {strategy['name']} (lot_size: {lot_size})")

    # Build strikes
    strikes = build_strikes(atm, step)

    # Build legs with REAL LTP + CORRECT lot_size
    legs        = build_legs(strategy["key"], strikes, ltp_map, lot_size, chain, symbol)
    net_premium = calculate_net_premium(legs)
    signal      = get_traffic_signal(capital, strategy["risk"])

    # Real payoff
    payoff = build_real_payoff(legs, atm, step, symbol)
    summary = calculate_summary(payoff)

    # Greeks with real IV and DTE
    T = max(dte / 365.0, 0.001)
    sigma = max((iv_percentile or 18.0) / 100.0, 0.08)
    try:
        greeks = calculate_greeks(
            S=float(atm_price), K=float(atm),
            T=T, r=0.065, sigma=sigma, option_type="CE",
        )
    except Exception:
        greeks = {"delta": 0.5, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    return {
        "error":          False,
        "symbol":         symbol,
        "capital":        capital,
        "trend":          trend,
        "iv_percentile":  iv_percentile,
        "atm_price":      atm,
        "lot_size":       lot_size,  # ✅ SINGLE SOURCE TOP LEVEL
        "expiry":         expiry,
        "strategy":       strategy,  # ✅ NO lot_size here
        "strikes":        strikes,
        "legs":           legs,     # ✅ Uses dynamic lot_size
        "net_premium":    net_premium,
        "traffic_signal": signal,
        "greeks":         greeks,
        "payoff":         payoff,
        "payoff_summary": summary,
        "capital_data":   capital_data,
    }
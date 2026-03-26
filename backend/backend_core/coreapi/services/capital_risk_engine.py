# ============================================================
# CAPITAL RISK ENGINE — SMART RISK AI
# ============================================================
# Determines:
#   - Investor level (BEGINNER / PROFESSIONAL / EXPERT)
#   - Max capital to deploy per trade
#   - Strategy eligibility by capital
#   - Lot affordability (DYNAMIC from instruments.py)
#   - Risk per trade (% based)
#   - Traffic light signal
# ============================================================

from coreapi.services.instruments import get_lot_size

STRATEGY_CAPITAL_MAP = [
    {
        "strategy":    "BUY CALL / BUY PUT",
        "min_capital": 5_000,
        "max_capital": 25_000,
        "risk":        "HIGH",
        "description": "Single leg directional. High risk, small capital."
    },
    {
        "strategy":    "BULL CALL SPREAD",
        "min_capital": 15_000,
        "max_capital": 75_000,
        "risk":        "MEDIUM",
        "description": "Debit spread. Defined max loss."
    },
    {
        "strategy":    "BEAR PUT SPREAD",
        "min_capital": 15_000,
        "max_capital": 75_000,
        "risk":        "MEDIUM",
        "description": "Debit spread for bearish view."
    },
    {
        "strategy":    "IRON CONDOR",
        "min_capital": 50_000,
        "max_capital": 3_00_000,
        "risk":        "LOW",
        "description": "4-leg neutral strategy. Best for sideways market."
    },
    {
        "strategy":    "SHORT STRANGLE",
        "min_capital": 1_00_000,
        "max_capital": 10_00_000,
        "risk":        "MEDIUM",
        "description": "Sell OTM CE + PE. Unlimited risk. Needs margin."
    },
    {
        "strategy":    "SHORT STRADDLE",
        "min_capital": 1_50_000,
        "max_capital": 10_00_000,
        "risk":        "HIGH",
        "description": "Sell ATM CE + PE. High premium, high risk."
    },
    {
        "strategy":    "JADE LIZARD",
        "min_capital": 2_00_000,
        "max_capital": 10_00_000,
        "risk":        "MEDIUM",
        "description": "Short Put + Short Call Spread. No upside risk."
    },
    {
        "strategy":    "RATIO SPREAD",
        "min_capital": 3_00_000,
        "max_capital": 10_00_000,
        "risk":        "HIGH",
        "description": "Advanced. Sell more options than you buy."
    },
]

def get_investor_level(capital: float) -> dict:
    if capital < 10_000:
        return {
            "level":   "ALERT",
            "emoji":   "⚠",
            "color":   "orange",
            "message": "Capital below ₹10,000 is not suitable for F&O trading."
        }
    elif capital < 3_00_000:
        return {
            "level":   "BEGINNER",
            "emoji":   "🟢",
            "color":   "green",
            "message": "Learning phase. Stick to single-leg options and small lots."
        }
    elif capital < 15_00_000:
        return {
            "level":   "PROFESSIONAL",
            "emoji":   "🟡",
            "color":   "goldenrod",
            "message": "Diversified strategies. Iron Condor and spreads suitable."
        }
    else:
        return {
            "level":   "EXPERT",
            "emoji":   "🔴",
            "color":   "red",
            "message": "Advanced portfolio. All strategies including Short Straddle available."
        }

def get_traffic_signal(capital: float, strategy_risk: str) -> dict:
    level = get_investor_level(capital)["level"]

    if level == "ALERT":
        return {"signal": "RED",    "color": "#ef4444", "message": "Capital too low for F&O trading."}

    if strategy_risk == "HIGH" and level == "BEGINNER":
        return {"signal": "RED",    "color": "#ef4444", "message": "High risk strategy not suitable for your capital."}

    if strategy_risk == "MEDIUM" and level == "BEGINNER":
        return {"signal": "YELLOW", "color": "#f59e0b", "message": "Proceed with caution. Use minimum lots only."}

    if strategy_risk == "LOW":
        return {"signal": "GREEN",  "color": "#22c55e", "message": "Strategy risk is acceptable for your capital."}

    if strategy_risk == "MEDIUM":
        return {"signal": "YELLOW", "color": "#f59e0b", "message": "Moderate risk. Size positions carefully."}

    return {"signal": "GREEN", "color": "#22c55e", "message": "Capital sufficient for this strategy."}

def get_eligible_strategies(capital: float) -> list:
    eligible = []
    for s in STRATEGY_CAPITAL_MAP:
        if capital >= s["min_capital"]:
            eligible.append(s)
    return eligible

def get_lot_affordability(capital: float, symbol: str, expiry: str, ltp_map: dict) -> list:
    """
    ltp_map = {
        "NIFTY":     {"ce_ltp": 120.0, "pe_ltp": 95.0},
        "BANKNIFTY": {"ce_ltp": 350.0, "pe_ltp": 280.0},
    }
    Returns how many lots of each index the capital can afford.
    """
    result = []
    deploy_capital = capital * 0.30  # Use 30% of capital for options

    # ✅ SINGLE SOURCE OF TRUTH
    lot_size = get_lot_size(symbol, expiry)
    
    if symbol not in ltp_map:
        return []

    ce_ltp = ltp_map[symbol].get("ce_ltp", 0)
    pe_ltp = ltp_map[symbol].get("pe_ltp", 0)

    if ce_ltp <= 0 and pe_ltp <= 0:
        return []

    avg_premium = (ce_ltp + pe_ltp) / 2 if (ce_ltp > 0 and pe_ltp > 0) else max(ce_ltp, pe_ltp)
    cost_per_lot = avg_premium * lot_size

    if cost_per_lot <= 0:
        return []

    max_lots = int(deploy_capital / cost_per_lot)
    result.append({
        "symbol":         symbol,
        "lot_size":       lot_size,  # ✅ DYNAMIC
        "ce_ltp":         ce_ltp,
        "pe_ltp":         pe_ltp,
        "cost_per_lot":   round(cost_per_lot, 2),
        "max_lots":       max_lots,
        "deploy_capital": round(deploy_capital, 2),
        "affordable":     max_lots >= 1,
    })

    return result

def get_risk_per_trade(capital: float) -> dict:
    """
    Standard risk management:
    - BEGINNER:      1% per trade
    - PROFESSIONAL:  1.5% per trade
    - EXPERT:        2% per trade
    """
    level = get_investor_level(capital)["level"]

    risk_pct_map = {
        "BEGINNER":     1.0,
        "PROFESSIONAL": 1.5,
        "EXPERT":       2.0,
        "ALERT":        0.0,
    }

    pct = risk_pct_map.get(level, 1.0)
    max_loss = capital * (pct / 100)

    return {
        "level":                level,
        "risk_pct":             pct,
        "max_loss_per_trade":   round(max_loss, 2),
        "message":              f"Risk {pct}% per trade = ₹{max_loss:,.2f} max loss per trade."
    }

def get_capital_summary(capital: float, symbol: str, expiry: str, ltp_map: dict = None) -> dict:
    """
    MAIN FUNCTION — call this from views.py
    Returns full capital analysis.
    """
    if ltp_map is None:
        ltp_map = {}

    investor       = get_investor_level(capital)
    strategies     = get_eligible_strategies(capital)
    risk_per_trade = get_risk_per_trade(capital)
    lot_afford     = get_lot_affordability(capital, symbol, expiry, ltp_map)

    best_strategy = strategies[-1] if strategies else None
    signal        = get_traffic_signal(capital, best_strategy["risk"] if best_strategy else "HIGH")

    return {
        "capital":           capital,
        "investor_level":    investor,
        "traffic_signal":    signal,
        "risk_per_trade":    risk_per_trade,
        "eligible_strategies": strategies,
        "best_strategy":     best_strategy,
        "lot_affordability": lot_afford,
        "deploy_capital":    round(capital * 0.30, 2),
        "reserve_capital":   round(capital * 0.70, 2),
    }
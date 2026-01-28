from coreapi.services.angel_ltp import get_ltp


def investment_planner_engine(capital, risk_profile="low", market_trend="Sideways"):
    plan = {
        "capital": capital,
        "investor_category": "",
        "diversification_status": "",
        "traffic_light": "",
        "investment_priority": [],
        "affordable_assets": [],
        "blocked_assets": [],
        "education": "",
        "next_step": "",
    }

    # 1️⃣ Investor category
    if capital < 300000:
        plan["investor_category"] = "BEGINNER"
    elif capital < 1500000:
        plan["investor_category"] = "PROFESSIONAL"
    else:
        plan["investor_category"] = "EXPERT"

    # 2️⃣ Risk & diversification
    if capital < 50000:
        plan["diversification_status"] = "NOT POSSIBLE"
        plan["traffic_light"] = "🟢 GREEN (SAFE)"
    elif capital < 300000:
        plan["diversification_status"] = "PARTIAL"
        plan["traffic_light"] = "🟡 YELLOW (MODERATE)"
    else:
        plan["diversification_status"] = "FULL"
        plan["traffic_light"] = "🟢 GREEN (HEALTHY)"

    # 3️⃣ Priority
    plan["investment_priority"] = [
        "Index Mutual Fund",
        "Debt Mutual Fund",
        "Gold Mutual Fund",
        "ETF / Stocks (when affordable)",
    ]

    # 4️⃣ Always-possible assets
    plan["affordable_assets"].extend([
        {"type": "Mutual Fund", "name": "Index Mutual Fund", "reason": "Auto diversified"},
        {"type": "Mutual Fund", "name": "Debt Mutual Fund", "reason": "Capital protection"},
        {"type": "Mutual Fund", "name": "Gold Mutual Fund", "reason": "Crisis hedge"},
    ])

    # 5️⃣ ETF & stock price-aware check
    symbols = ["NIFTYBEES", "BANKBEES", "GOLDBEES", "RELIANCE", "TCS", "INFY", "MRF"]

    for sym in symbols:
        try:
            price = get_ltp(sym)
        except Exception as e:
            plan["blocked_assets"].append({
                "type": "Asset",
                "name": sym,
                "reason": str(e),
            })
            continue

        if price <= capital:
            plan["affordable_assets"].append({
                "type": "ETF/Stock",
                "name": sym,
                "price": round(price, 2),
                "reason": "Affordable with your capital",
            })
        else:
            plan["blocked_assets"].append({
                "type": "ETF/Stock",
                "name": sym,
                "price": round(price, 2),
                "reason": "Price higher than capital",
            })

    # 6️⃣ Education
    plan["education"] = (
        "All prices are fetched from Angel One last traded price. "
        "SmartRisk never shows investments that cannot be executed."
    )

    plan["next_step"] = (
        "Grow capital first" if capital < 50000 else
        "Diversify slowly with discipline"
    )

    return plan

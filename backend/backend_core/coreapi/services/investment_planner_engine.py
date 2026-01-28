# coreapi/services/investment_planner_engine.py

from coreapi.services.angel_ltp import get_ltp


def investment_planner_engine(capital, risk_profile, market_trend):
    """
    SMART RISK – CAPITAL AWARE INVESTMENT PLANNER
    - No fake diversification
    - Capital decides everything
    - Clear priority & explanation
    """

    plan = {
        "capital": capital,
        "investor_category": "",
        "diversification_status": "",
        "traffic_light": "",
        "investment_priority": [],
        "affordable_assets": [],
        "blocked_assets": [],
        "education": "",
        "next_step": ""
    }

    # --------------------------------------------------
    # 1️⃣ INVESTOR CATEGORY (CAPITAL BASED)
    # --------------------------------------------------
    if capital < 300000:
        plan["investor_category"] = "BEGINNER"
    elif capital < 1500000:
        plan["investor_category"] = "PROFESSIONAL"
    else:
        plan["investor_category"] = "EXPERT"

    # --------------------------------------------------
    # 2️⃣ DIVERSIFICATION STATUS
    # --------------------------------------------------
    if capital < 50000:
        plan["diversification_status"] = "NOT POSSIBLE"
        plan["traffic_light"] = "🟢 GREEN (SAFE – CAPITAL PROTECTED)"
    elif capital < 300000:
        plan["diversification_status"] = "PARTIAL"
        plan["traffic_light"] = "🟡 YELLOW (MODERATE RISK)"
    else:
        plan["diversification_status"] = "FULL"
        plan["traffic_light"] = "🟢 GREEN (HEALTHY DIVERSIFICATION)"

    # --------------------------------------------------
    # 3️⃣ INVESTMENT PRIORITY (WHAT FIRST?)
    # --------------------------------------------------
    if capital < 50000:
        plan["investment_priority"] = [
            "Index Mutual Fund (SIP only)"
        ]
    elif capital < 300000:
        plan["investment_priority"] = [
            "Index Mutual Fund",
            "Debt Mutual Fund",
            "Gold Mutual Fund"
        ]
    else:
        plan["investment_priority"] = [
            "Index Fund / ETF (Base)",
            "Debt (Stability)",
            "Gold (Insurance)",
            "Stocks (Selective)"
        ]

    # --------------------------------------------------
    # 4️⃣ MUTUAL FUNDS (ALWAYS POSSIBLE)
    # --------------------------------------------------
    plan["affordable_assets"].extend([
        {
            "type": "Mutual Fund",
            "name": "Index Mutual Fund",
            "reason": "Best first investment, auto-diversified"
        },
        {
            "type": "Mutual Fund",
            "name": "Debt Mutual Fund",
            "reason": "Stability during market crashes"
        },
        {
            "type": "Mutual Fund",
            "name": "Gold Mutual Fund",
            "reason": "Protection during crisis, war, inflation"
        }
    ])

    # --------------------------------------------------
    # 5️⃣ STOCK & ETF CHECK (PRICE AWARE)
    # --------------------------------------------------
    stock_universe = ["RELIANCE", "TCS", "INFY", "ITC", "HDFCBANK", "MRF"]
    etf_universe = ["NIFTYBEES", "BANKBEES", "GOLDBEES"]

    for stock in stock_universe:
        try:
            price = get_ltp(stock)
        except Exception:
            plan["blocked_assets"].append({
                "type": "Stock",
                "name": stock,
                "reason": "Live price not available"
            })
            continue

        if price <= capital:
            plan["affordable_assets"].append({
                "type": "Stock",
                "name": stock,
                "price": price,
                "reason": "Affordable with your capital"
            })
        else:
            plan["blocked_assets"].append({
                "type": "Stock",
                "name": stock,
                "price": price,
                "reason": "Stock price higher than your capital"
            })

    for etf in etf_universe:
        try:
            price = get_ltp(etf)
        except Exception:
            plan["blocked_assets"].append({
                "type": "ETF",
                "name": etf,
                "reason": "Live price not available"
            })
            continue

        if price <= capital:
            plan["affordable_assets"].append({
                "type": "ETF",
                "name": etf,
                "price": price,
                "reason": "ETF unit affordable"
            })
        else:
            plan["blocked_assets"].append({
                "type": "ETF",
                "name": etf,
                "price": price,
                "reason": "ETF unit price exceeds capital"
            })

    # --------------------------------------------------
    # 6️⃣ EDUCATION & NEXT STEP
    # --------------------------------------------------
    plan["education"] = (
        "SmartRisk shows only investments that are actually possible with your money. "
        "Diversification is allowed only when capital supports it."
    )

    if capital < 50000:
        plan["next_step"] = "Grow capital first. Do not force diversification."
    elif capital < 300000:
        plan["next_step"] = "You can diversify slowly using funds. Avoid direct stocks."
    else:
        plan["next_step"] = "You are ready for full diversification with discipline."

    return plan

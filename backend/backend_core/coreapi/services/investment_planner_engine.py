def investment_planner_engine(capital, risk_profile, market_trend):
    """
    Investment Planner with:
    - Stock & ETF suggestions
    - Expected annual returns
    - Human-readable reasoning
    """

    risk_profile = risk_profile.lower()
    market_trend = market_trend.capitalize()

    # ----------------------------
    # BASE ALLOCATION
    # ----------------------------
    if risk_profile == "low":
        plan = {
            "Index ETF": {
                "percent": 0.50,
                "return": 10,
                "assets": ["NIFTY 50 ETF"],
                "reason": "Provides diversification across top Indian companies with low risk."
            },
            "Large Cap Stocks": {
                "percent": 0.30,
                "return": 11,
                "assets": ["Reliance", "TCS", "HDFC Bank"],
                "reason": "Stable market leaders with strong fundamentals and steady growth."
            },
            "Gold ETF": {
                "percent": 0.10,
                "return": 7,
                "assets": ["GoldBeES"],
                "reason": "Acts as a hedge during market volatility and inflation."
            },
            "Liquid Fund": {
                "percent": 0.10,
                "return": 4,
                "assets": ["Liquid ETF"],
                "reason": "Ensures capital safety and liquidity."
            }
        }

    elif risk_profile == "medium":
        plan = {
            "Index ETF": {
                "percent": 0.40,
                "return": 10,
                "assets": ["NIFTY 50 ETF"],
                "reason": "Provides core stability to the portfolio."
            },
            "Large Cap Stocks": {
                "percent": 0.30,
                "return": 11,
                "assets": ["Reliance", "TCS"],
                "reason": "Balances growth and safety."
            },
            "Mid Cap Stocks": {
                "percent": 0.20,
                "return": 13,
                "assets": ["Trent", "L&T Technology Services"],
                "reason": "Offers higher growth potential with manageable risk."
            },
            "Gold ETF": {
                "percent": 0.10,
                "return": 7,
                "assets": ["GoldBeES"],
                "reason": "Protects portfolio during downturns."
            }
        }

    else:  # high risk
        plan = {
            "Index ETF": {
                "percent": 0.30,
                "return": 10,
                "assets": ["NIFTY 50 ETF"],
                "reason": "Maintains minimum portfolio stability."
            },
            "Mid Cap Stocks": {
                "percent": 0.40,
                "return": 13,
                "assets": ["Trent", "L&T Technology Services"],
                "reason": "Strong growth-oriented companies."
            },
            "Small Cap Stocks": {
                "percent": 0.20,
                "return": 15,
                "assets": ["Affle India", "Deepak Nitrite"],
                "reason": "High growth potential with higher volatility."
            },
            "Gold ETF": {
                "percent": 0.10,
                "return": 7,
                "assets": ["GoldBeES"],
                "reason": "Risk hedge against equity drawdowns."
            }
        }

    # ----------------------------
    # BEAR MARKET SAFETY RULE
    # ----------------------------
    if market_trend == "Bearish":
        plan["Liquid Fund"] = {
            "percent": 0.10,
            "return": 4,
            "assets": ["Liquid ETF"],
            "reason": "Added for capital protection during bearish markets."
        }
        plan["Index ETF"]["percent"] -= 0.10

    # ----------------------------
    # FINAL CALCULATION
    # ----------------------------
    allocation = {}
    weighted_return = 0

    for category, data in plan.items():
        amount = round(capital * data["percent"], 2)
        allocation[category] = {
            "amount": amount,
            "expected_return_percent": data["return"],
            "assets": data["assets"],
            "reason": data["reason"]
        }
        weighted_return += data["percent"] * data["return"]

    # ----------------------------
    # OVERALL EXPLANATION
    # ----------------------------
    overall_reason = (
        f"This allocation is designed for a {risk_profile.capitalize()} risk investor. "
        f"It balances growth and safety based on current {market_trend} market conditions. "
        "Index ETFs provide diversification, selected stocks offer stable growth, "
        "and defensive assets reduce downside risk."
    )

    return {
        "capital": capital,
        "risk_profile": risk_profile.capitalize(),
        "market_trend": market_trend,
        "expected_portfolio_return_percent": round(weighted_return, 2),
        "why_this_plan_works": overall_reason,
        "allocation": allocation
    }

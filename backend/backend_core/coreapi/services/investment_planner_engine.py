from coreapi.services.angel_ltp import get_ltp
from coreapi.services.asset_allocation_engine import get_asset_allocation
from coreapi.services.ai_summary import generate_ai_summary


# -------------------------------------------------------
# Asset Universe
# -------------------------------------------------------

STOCKS = [
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "ITC",
]

ETFS = [
    "NIFTYBEES",
    "BANKBEES",
    "ITBEES",
]

GOLD = [
    "GOLDBEES",
]


# -------------------------------------------------------
# Unit Calculation
# -------------------------------------------------------

def calculate_units(allocation_amount, price):

    if price is None or price <= 0:
        return 0, 0, allocation_amount

    units = int(allocation_amount // price)

    invested = round(units * price, 2)

    remaining = round(allocation_amount - invested, 2)

    return units, invested, remaining


# -------------------------------------------------------
# Helper: Build Portfolio
# -------------------------------------------------------

def build_portfolio(asset_list, capital):

    portfolio = []
    blocked_assets = []

    asset_count = len(asset_list)

    if asset_count == 0:
        return portfolio, blocked_assets, 0

    allocation_per_asset = capital / asset_count

    total_invested = 0

    for symbol in asset_list:

        try:

            price = get_ltp(symbol)

            if price is None:
                raise Exception("Price not available")

            units, invested, remaining = calculate_units(
                allocation_per_asset,
                price
            )

            if units == 0:

                blocked_assets.append({
                    "asset": symbol,
                    "reason": "Capital too low",
                    "price": price
                })

                continue

            portfolio.append({
                "asset": symbol,
                "price": price,
                "allocated_amount": round(allocation_per_asset, 2),
                "units": units,
                "invested": invested,
                "remaining_from_allocation": remaining
            })

            total_invested += invested

        except Exception as e:

            blocked_assets.append({
                "asset": symbol,
                "reason": str(e)
            })

    return portfolio, blocked_assets, total_invested


# -------------------------------------------------------
# Main Investment Planner Engine
# -------------------------------------------------------

def investment_planner_engine(capital: float, risk_profile: str, market_trend: str):

    # --------------------------------
    # Asset Allocation Layer
    # --------------------------------

    allocation = get_asset_allocation(capital, risk_profile)

    stocks_capital = capital * allocation["stocks"] / 100
    etf_capital = capital * allocation["etf"] / 100
    gold_capital = capital * allocation["gold"] / 100
    cash_reserve = capital * allocation["cash"] / 100

    # --------------------------------
    # Build Portfolios
    # --------------------------------

    stock_portfolio, stock_blocked, stock_invested = build_portfolio(
        STOCKS,
        stocks_capital
    )

    etf_portfolio, etf_blocked, etf_invested = build_portfolio(
        ETFS,
        etf_capital
    )

    gold_portfolio, gold_blocked, gold_invested = build_portfolio(
        GOLD,
        gold_capital
    )

    # --------------------------------
    # Combine Results
    # --------------------------------

    portfolio = stock_portfolio + etf_portfolio + gold_portfolio

    blocked_assets = stock_blocked + etf_blocked + gold_blocked

    total_invested = stock_invested + etf_invested + gold_invested

    final_remaining_cash = round(capital - total_invested, 2)

    # --------------------------------
    # AI Financial Doctor Explanation
    # --------------------------------

    ai_summary = generate_ai_summary(
        capital,
        risk_profile,
        allocation,
        portfolio
    )

    # --------------------------------
    # Final Output
    # --------------------------------

    return {
        "capital": capital,
        "risk_profile": risk_profile,
        "market_trend": market_trend,
        "asset_allocation": allocation,
        "cash_reserve": round(cash_reserve, 2),
        "portfolio": portfolio,
        "blocked_assets": blocked_assets,
        "total_invested": round(total_invested, 2),
        "final_remaining_cash": final_remaining_cash,
        "ai_summary": ai_summary
    }

# backend/backend_core/coreapi/services/invest_plan.py

def invest_plan_engine(data):
    capital = float(data.get("capital", 0))
    risk_level = data.get("risk_level", "medium")

    if capital <= 0:
        return {"error": "Capital must be greater than 0"}

    if risk_level == "low":
        plan = "60% Index Funds, 40% Bonds"
    elif risk_level == "high":
        plan = "70% Equity, 30% Index Funds"
    else:
        plan = "50% Equity, 50% Index Funds"

    return {
        "capital": capital,
        "risk_level": risk_level,
        "plan": plan,
        "message": "Investment plan generated successfully."
    }

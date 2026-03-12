# coreapi/services/asset_allocation_engine.py

def get_asset_allocation(capital: float, risk_profile: str):

    risk_profile = risk_profile.lower()

    # Beginner
    if capital <= 300000:
        return {
            "stocks": 20,
            "etf": 40,
            "mutual_funds": 30,
            "gold": 5,
            "cash": 5
        }

    # Professional
    elif capital <= 1500000:
        return {
            "stocks": 35,
            "etf": 30,
            "mutual_funds": 25,
            "gold": 5,
            "cash": 5
        }

    # Expert
    else:
        return {
            "stocks": 40,
            "etf": 30,
            "mutual_funds": 20,
            "gold": 5,
            "cash": 5
        }
from .option_chain_service import get_option_chain
import numpy as np
import traceback


# ------------------------------------------------------
#   PCR = Total PE OI / Total CE OI
# ------------------------------------------------------
def compute_pcr(option_chain):
    try:
        ce = option_chain["ce"]
        pe = option_chain["pe"]

        total_ce_oi = sum(item.get("open_interest", 0) for item in ce)
        total_pe_oi = sum(item.get("open_interest", 0) for item in pe)

        if total_ce_oi == 0:
            return 0

        return round(total_pe_oi / total_ce_oi, 2)

    except:
        return 0


# ------------------------------------------------------
#   MAX PAIN (Strike with lowest combined CE+PE loss)
# ------------------------------------------------------
def compute_max_pain(option_chain):
    try:
        strikes = list(set(item["strike_price"] for item in option_chain["ce"]))
        strikes.sort()

        loss_map = {}

        for strike in strikes:
            loss = 0
            for ce in option_chain["ce"]:
                loss += ce["open_interest"] * abs(ce["strike_price"] - strike)

            for pe in option_chain["pe"]:
                loss += pe["open_interest"] * abs(pe["strike_price"] - strike)

            loss_map[strike] = loss

        max_pain = min(loss_map, key=loss_map.get)
        return max_pain

    except:
        return None


# ------------------------------------------------------
#   IV TREND (Average CE + PE IV)
# ------------------------------------------------------
def compute_iv_trend(option_chain):
    try:
        ce_iv = np.mean([x.get("implied_volatility", 0) for x in option_chain["ce"]])
        pe_iv = np.mean([x.get("implied_volatility", 0) for x in option_chain["pe"]])

        iv_avg = round((ce_iv + pe_iv) / 2, 2)
        return iv_avg

    except:
        return 0


# ------------------------------------------------------
#   MARKET TREND (Bullish / Bearish / Sideways)
# ------------------------------------------------------
def compute_trend(option_chain):
    try:
        spot = option_chain["spot"]
        max_pain = compute_max_pain(option_chain)

        if max_pain is None:
            return "unknown"

        if spot > max_pain:
            return "bullish"
        elif spot < max_pain:
            return "bearish"
        else:
            return "sideways"
    except:
        return "unknown"


# ------------------------------------------------------
#   DASHBOARD MAIN FUNCTION
# ------------------------------------------------------
def get_dashboard_data(symbol="NIFTY"):
    try:
        option_chain = get_option_chain(symbol)

        if option_chain.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to fetch option chain"
            }

        pcr = compute_pcr(option_chain)
        max_pain = compute_max_pain(option_chain)
        iv = compute_iv_trend(option_chain)
        trend = compute_trend(option_chain)

        return {
            "status": "success",
            "symbol": symbol,
            "spot": option_chain.get("spot"),
            "pcr": pcr,
            "max_pain": max_pain,
            "iv": iv,
            "trend": trend,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Dashboard calculation failed",
            "detail": str(e),
            "trace": traceback.format_exc()
        }

def analyze_option_chain(option_chain, spot_price):

    if not option_chain:
        return {}

    total_call_oi = 0
    total_put_oi = 0

    max_call_oi = 0
    max_put_oi = 0

    resistance = None
    support = None

    iv_sum = 0
    iv_count = 0

    for item in option_chain:

        call_oi = item.get("call_oi", 0)
        put_oi = item.get("put_oi", 0)

        strike = item.get("strike")

        total_call_oi += call_oi
        total_put_oi += put_oi

        # 🔥 Resistance = max call OI
        if call_oi > max_call_oi:
            max_call_oi = call_oi
            resistance = strike

        # 🔥 Support = max put OI
        if put_oi > max_put_oi:
            max_put_oi = put_oi
            support = strike

        # 🔥 IV average
        iv = item.get("call_iv") or item.get("put_iv")
        if iv:
            iv_sum += iv
            iv_count += 1

    # 🔥 PCR
    pcr = total_put_oi / total_call_oi if total_call_oi else 1

    # 🔥 Bias
    if pcr > 1.2:
        bias = "Bullish"
    elif pcr < 0.8:
        bias = "Bearish"
    else:
        bias = "Sideways"

    # 🔥 ATM
    atm_strike = min(option_chain, key=lambda x: abs(x["strike"] - spot_price))["strike"]

    avg_iv = iv_sum / iv_count if iv_count else 18

    return {
        "support": support,
        "resistance": resistance,
        "pcr": round(pcr, 2),
        "bias": bias,
        "atm_strike": atm_strike,
        "avg_iv": round(avg_iv, 2)
    }
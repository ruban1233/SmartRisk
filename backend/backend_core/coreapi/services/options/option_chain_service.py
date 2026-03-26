from concurrent.futures import ThreadPoolExecutor
from coreapi.services.angel_login import get_smart_connection
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.instruments import find_option, get_available_strikes


# ==========================================
# FAST LTP FETCH FUNCTION
# ==========================================
def fetch_ltp(smart, option):
    try:
        data = smart.ltpData("NFO", option["symbol"], option["token"])
        return data["data"]["ltp"]
    except Exception as e:
        print("❌ LTP ERROR:", e)
        return None


# ==========================================
# OPTION CHAIN (FAST VERSION 🚀)
# ==========================================
def get_option_chain(symbol="NIFTY", expiry=None):

    print("\n🚀 START OPTION CHAIN (FAST MODE)")

    smart = get_smart_connection()

    spot = get_ltp(symbol)
    atm = get_atm_strike(spot, symbol)

    print("SPOT:", spot)
    print("ATM:", atm)

    # ======================================
    # GET STRIKES
    # ======================================
    all_strikes = get_available_strikes(symbol)

    if not all_strikes:
        print("❌ NO STRIKES")
        return []

    RANGE = 20

    sorted_strikes = sorted(all_strikes, key=lambda x: abs(x - atm))
    selected_strikes = sorted(sorted_strikes[:RANGE])

    print("\n🎯 SELECTED STRIKES:", selected_strikes)

    # ======================================
    # VALID STRIKES
    # ======================================
    valid_strikes = []

    for strike in selected_strikes:
        ce = find_option(symbol, strike, "CE", expiry)
        pe = find_option(symbol, strike, "PE", expiry)

        if ce and pe:
            valid_strikes.append(strike)

    if not valid_strikes:
        print("❌ NO VALID STRIKES")
        return []

    print("\n🎯 FINAL VALID STRIKES:", valid_strikes)

    # ======================================
    # 🔥 PARALLEL FETCH
    # ======================================
    def process_strike(strike):

        ce = find_option(symbol, strike, "CE", expiry)
        pe = find_option(symbol, strike, "PE", expiry)

        ce_price = fetch_ltp(smart, ce) if ce else None
        pe_price = fetch_ltp(smart, pe) if pe else None

        return [
            {
                "strike": strike,
                "option_type": "CE",
                "ltp": ce_price
            },
            {
                "strike": strike,
                "option_type": "PE",
                "ltp": pe_price
            }
        ]

    chain = []

    # 🔥 THREADING (FAST)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_strike, valid_strikes)

    for res in results:
        chain.extend(res)

    print("\n✅ FINAL CHAIN READY (FAST)")

    return chain
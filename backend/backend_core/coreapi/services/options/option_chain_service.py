import time
from coreapi.services.angel_login import get_smart_connection
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.instruments import find_option, get_available_strikes


# ==========================================
# OPTION CHAIN (FINAL PRO VERSION - FIXED)
# ==========================================
def get_option_chain(symbol="NIFTY"):

    print("\n🚀 START OPTION CHAIN")

    smart = get_smart_connection()

    spot = get_ltp(symbol)
    atm = get_atm_strike(spot, symbol)

    print("SPOT:", spot)
    print("ATM:", atm)

    # ======================================
    # 🔥 GET ALL STRIKES
    # ======================================
    all_strikes = get_available_strikes(symbol)

    if not all_strikes:
        print("❌ NO STRIKES")
        return []

    # ======================================
    # 🔥 EXPAND RANGE (CRITICAL FIX)
    # ======================================
    RANGE = 20   # ← controls how many strikes around ATM

    sorted_strikes = sorted(all_strikes, key=lambda x: abs(x - atm))

    selected_strikes = sorted(sorted_strikes[:RANGE])

    print("\n🎯 SELECTED STRIKES:", selected_strikes)

    # ======================================
    # 🔥 VALIDATE STRIKES (CE + PE must exist)
    # ======================================
    valid_strikes = []

    for strike in selected_strikes:

        print("\n🔍 Validating strike:", strike)

        ce = find_option(symbol, strike, "CE")
        pe = find_option(symbol, strike, "PE")

        if ce and pe:
            print("✅ VALID STRIKE:", strike)
            valid_strikes.append(strike)
        else:
            print("❌ INVALID STRIKE:", strike)

    if not valid_strikes:
        print("❌ NO VALID STRIKES FOUND")
        return []

    print("\n🎯 FINAL VALID STRIKES:", valid_strikes)

    # ======================================
    # 🔥 FETCH LTP DATA
    # ======================================
    chain = []

    for strike in valid_strikes:

        print("\n🔍 Fetching strike:", strike)

        ce = find_option(symbol, strike, "CE")
        pe = find_option(symbol, strike, "PE")

        ce_price = None
        pe_price = None

        # =========================
        # CE
        # =========================
        if ce:
            try:
                print("⏳ CE FETCH:", ce["symbol"])
                ce_data = smart.ltpData("NFO", ce["symbol"], ce["token"])
                ce_price = ce_data["data"]["ltp"]
                print("✅ CE:", ce_price)
            except Exception as e:
                print("❌ CE ERROR:", e)

        time.sleep(0.15)

        # =========================
        # PE
        # =========================
        if pe:
            try:
                print("⏳ PE FETCH:", pe["symbol"])
                pe_data = smart.ltpData("NFO", pe["symbol"], pe["token"])
                pe_price = pe_data["data"]["ltp"]
                print("✅ PE:", pe_price)
            except Exception as e:
                print("❌ PE ERROR:", e)

        time.sleep(0.15)

        # =========================
        # STORE DATA
        # =========================
        chain.append({
            "strike": strike,
            "option_type": "CE",
            "ltp": ce_price
        })

        chain.append({
            "strike": strike,
            "option_type": "PE",
            "ltp": pe_price
        })

    print("\n✅ FINAL CHAIN READY")

    return chain
import time
from coreapi.services.angel_login import get_smart_connection
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.instruments import find_option


def get_option_chain(symbol="NIFTY"):

    print("🚀 START OPTION CHAIN")

    smart = get_smart_connection()

    spot = get_ltp(symbol)
    atm = get_atm_strike(spot, symbol)

    print("SPOT:", spot)
    print("ATM:", atm)

    # 🔥 ONLY 3 STRIKES (FAST)
    strikes = [atm - 50, atm, atm + 50]

    chain = []

    for strike in strikes:

        print("\n🔍 Checking strike:", strike)

        ce = find_option(symbol, strike, "CE")
        pe = find_option(symbol, strike, "PE")

        ce_price = None
        pe_price = None

        # =========================
        # CE PRICE
        # =========================
        if ce:
            try:
                print("⏳ CE FETCH:", ce["symbol"])
                ce_data = smart.ltpData("NFO", ce["symbol"], ce["token"])
                ce_price = ce_data["data"]["ltp"]
                print("✅ CE:", ce_price)
            except Exception as e:
                print("❌ CE ERROR:", e)

        time.sleep(0.3)

        # =========================
        # PE PRICE
        # =========================
        if pe:
            try:
                print("⏳ PE FETCH:", pe["symbol"])
                pe_data = smart.ltpData("NFO", pe["symbol"], pe["token"])
                pe_price = pe_data["data"]["ltp"]
                print("✅ PE:", pe_price)
            except Exception as e:
                print("❌ PE ERROR:", e)

        time.sleep(0.3)

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
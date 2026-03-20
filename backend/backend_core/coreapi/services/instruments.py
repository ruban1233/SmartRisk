import pandas as pd
import json
import os

INSTRUMENT_DF = None


# ==========================================
# LOAD INSTRUMENT DATA
# ==========================================
def load_instruments():
    global INSTRUMENT_DF

    if INSTRUMENT_DF is not None:
        return INSTRUMENT_DF

    file_path = os.path.join(
        os.path.dirname(__file__),
        "OpenAPIScripMaster.json"
    )

    with open(file_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)

    # ✅ keep only NFO segment
    df = df[df["exch_seg"] == "NFO"]

    INSTRUMENT_DF = df
    return df


# ==========================================
# FIND OPTION TOKEN
# ==========================================
def find_option(symbol, strike, option_type):

    df = load_instruments()

    # ✅ normalize symbol
    df["name"] = df["name"].str.upper()

    # ✅ filter only NIFTY (or given symbol)
    df = df[df["name"] == symbol.upper()]

    print("TOTAL FILTERED ROWS:", len(df))

    if df.empty:
        print("❌ NO DATA AFTER FILTER")
        return None

    # ======================================
    # 🔥 EXPIRY FIX
    # ======================================
    expiries = sorted(df["expiry"].unique())

    if not expiries:
        print("❌ NO EXPIRY FOUND")
        return None

    expiry = expiries[0]   # nearest expiry

    print("🔥 USING EXPIRY:", expiry)

    # ======================================
    # 🔥 STRIKE MATCH
    # ======================================
    result = df[
    (df["expiry"] == expiry) &
    (df["strike"].astype(float).round(0) == round(strike * 100)) &
    (df["symbol"].str.endswith(option_type))
]

    if result.empty:
        print("❌ NOT FOUND:", strike, option_type)
        return None

    row = result.iloc[0]

    print("✅ FOUND:", row["symbol"], row["token"])

    return {
        "symbol": row["symbol"],
        "token": row["token"]
    }
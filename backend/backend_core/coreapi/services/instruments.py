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

    # Only derivatives
    df = df[df["exch_seg"] == "NFO"]

    # Fix datatype
    df["strike"] = df["strike"].astype(float)

    INSTRUMENT_DF = df
    return df


# ==========================================
# STRIKE STEP ENGINE
# ==========================================
def get_strike_step(symbol):
    symbol = symbol.upper()

    if symbol == "BANKNIFTY":
        return 100
    elif symbol == "NIFTY":
        return 50
    elif symbol == "FINNIFTY":
        return 50
    elif symbol == "MIDCPNIFTY":
        return 25
    else:
        return 50   # stocks


# ==========================================
# GET VALID STRIKES ONLY
# ==========================================
def get_available_strikes(symbol):
    df = load_instruments()

    df["name"] = df["name"].str.upper()
    df = df[df["name"] == symbol.upper()]

    if df.empty:
        return []

    strikes = sorted(df["strike"].unique())

    # convert 2310000 → 23100
    strikes = [int(s / 100) for s in strikes]

    step = get_strike_step(symbol)

    # 🔥 keep only valid strikes
    valid_strikes = [s for s in strikes if s % step == 0]

    return valid_strikes


# ==========================================
# FIND OPTION TOKEN
# ==========================================
def find_option(symbol, strike, option_type):

    df = load_instruments()

    df["name"] = df["name"].str.upper()
    symbol = symbol.upper()

    df = df[df["name"] == symbol]

    if df.empty:
        print("❌ NO DATA:", symbol)
        return None

    expiries = sorted(df["expiry"].unique())

    if not expiries:
        print("❌ NO EXPIRY")
        return None

    expiry = expiries[0]

    target = round(strike * 100)

    result = df[
        (df["expiry"] == expiry) &
        (df["strike"].round(0) == target) &
        (df["symbol"].str.endswith(option_type))
    ]

    if result.empty:
        print(f"❌ NOT FOUND: {symbol} {strike} {option_type}")
        return None

    row = result.iloc[0]

    print("✅ FOUND:", row["symbol"], row["token"])

    return {
        "symbol": row["symbol"],
        "token": row["token"]
    }
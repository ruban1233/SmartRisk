import pandas as pd
import json
import os
from datetime import datetime

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

    # Only derivatives (NFO)
    df = df[df["exch_seg"] == "NFO"]

    # Fix datatype
    df["strike"] = pd.to_numeric(df["strike"], errors="coerce")

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
        return 50


# ==========================================
# GET VALID STRIKES
# ==========================================
def get_available_strikes(symbol):
    df = load_instruments()

    df["name"] = df["name"].str.upper()
    df = df[df["name"] == symbol.upper()]

    if df.empty:
        return []

    strikes = sorted(df["strike"].dropna().unique())

    # convert 2310000 → 23100
    strikes = [int(s / 100) for s in strikes]

    step = get_strike_step(symbol)

    valid_strikes = [s for s in strikes if s % step == 0]

    return valid_strikes


# ==========================================
# GET NEAREST EXPIRY
# ==========================================
def get_nearest_expiry(df):
    expiries = df["expiry"].dropna().unique()

    valid_expiries = []

    for exp in expiries:
        try:
            dt = datetime.strptime(exp, "%d%b%Y")
            if dt >= datetime.today():
                valid_expiries.append((dt, exp))
        except:
            continue

    if not valid_expiries:
        return None

    valid_expiries.sort()

    selected = valid_expiries[0][1]

    print("🔥 USING EXPIRY:", selected)

    return selected


# ==========================================
# FIND OPTION TOKEN
# ==========================================
def find_option(symbol, strike, option_type, selected_expiry=None):

    df = load_instruments()

    df["name"] = df["name"].str.upper()
    symbol = symbol.upper()

    df = df[df["name"] == symbol]

    if df.empty:
        print("❌ NO DATA:", symbol)
        return None

    # 🔥 STRICT: MUST HAVE EXPIRY
    if not selected_expiry:
        print("❌ EXPIRY REQUIRED")
        return None

    expiry = selected_expiry.upper()

    target = int(strike * 100)

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


# ==========================================
# GET LOT SIZE (🔥 FINAL CORRECT)
# ==========================================
def get_lot_size(symbol, expiry=None):
    df = load_instruments()

    df["name"] = df["name"].str.upper()
    df = df[df["name"] == symbol.upper()]

    if expiry:
        df = df[df["expiry"] == expiry]

    if df.empty:
        print("❌ LOT SIZE NOT FOUND")
        return None

    try:
        # take first valid row
        row = df.iloc[0]

        lot_size = int(float(row["lotsize"]))

        print(f"📦 LOT SIZE ({symbol}):", lot_size)

        return lot_size

    except Exception as e:
        print("❌ LOT SIZE ERROR:", e)
        return None
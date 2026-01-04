import pandas as pd
import numpy as np

# =========================
# INDICATOR FUNCTIONS
# =========================

def calculate_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(series):
    ema12 = calculate_ema(series, 12)
    ema26 = calculate_ema(series, 26)

    macd = ema12 - ema26
    signal = calculate_ema(macd, 9)

    return macd, signal


# =========================
# MARKET SENTIMENT ENGINE
# =========================

def market_sentiment_engine(candles_df):
    """
    candles_df must contain a 'close' column
    """

    # 🔐 Safety check (important)
    if len(candles_df) < 50:
        return {
            "trend": "Sideways",
            "strength": 0
        }

    score = 0
    close = candles_df["close"]

    # 1️⃣ EMA Trend
    ema_fast = calculate_ema(close, 20)
    ema_slow = calculate_ema(close, 50)

    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        score += 1
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        score -= 1

    # 2️⃣ RSI Momentum (STRICT to avoid noise)
    rsi = calculate_rsi(close)

    if rsi.iloc[-1] > 60:
        score += 1
    elif rsi.iloc[-1] < 40:
        score -= 1

    # 3️⃣ MACD Confirmation
    macd, signal = calculate_macd(close)

    if macd.iloc[-1] > signal.iloc[-1]:
        score += 1
    elif macd.iloc[-1] < signal.iloc[-1]:
        score -= 1

    # =========================
    # FINAL DECISION
    # =========================

    if score >= 3:
        trend = "Bullish"
    elif score <= -3:
        trend = "Bearish"
    else:
        trend = "Sideways"

    strength = min(abs(score) * 3, 10)

    return {
        "trend": trend,
        "strength": strength
    }


# =========================
# LOCAL TEST (STEP-1 CHECK)
# =========================
if __name__ == "__main__":

    # Sideways market example
    data = {
       "close": [21500, 21501, 21499, 21500, 21501]
    }

    df = pd.DataFrame(data)

    print(market_sentiment_engine(df))

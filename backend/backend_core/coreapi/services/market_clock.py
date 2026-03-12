from datetime import datetime
import pytz

def is_market_open():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)

    if now.weekday() >= 5:  # Sat/Sun
        return False

    market_open = now.replace(hour=9, minute=15, second=0)
    market_close = now.replace(hour=15, minute=30, second=0)

    return market_open <= now <= market_close

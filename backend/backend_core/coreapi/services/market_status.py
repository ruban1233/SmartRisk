from datetime import datetime
import pytz

def is_market_open():
    india = pytz.timezone("Asia/Kolkata")
    now = datetime.now(india).time()

    market_open = now >= datetime.strptime("09:15", "%H:%M").time()
    market_close = now <= datetime.strptime("15:30", "%H:%M").time()

    return market_open and market_close

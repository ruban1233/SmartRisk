from datetime import date, timedelta

def get_next_weekly_expiry():
    today = date.today()
    days_ahead = (3 - today.weekday()) % 7  # Thursday = 3
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).strftime("%d-%b-%Y").upper()

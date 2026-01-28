from datetime import datetime

def time_to_expiry(expiry_date):
    now = datetime.now()
    expiry = datetime.combine(expiry_date, datetime.min.time())
    days = max((expiry - now).days, 1)
    return days / 365

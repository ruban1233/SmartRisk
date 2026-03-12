# coreapi/services/angel_candles.py

from coreapi.services.angel_login import get_smart_connection


def get_index_candles(symbol):
    session = get_smart_connection()

    if not session:
        raise Exception("Angel session not available")

    # SAFE fallback dummy structure
    return [
        {"close": 100},
        {"close": 101},
        {"close": 102},
    ]

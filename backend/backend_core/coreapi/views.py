from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.angel_candles import get_index_candles
from coreapi.services.market_sentiment import market_sentiment_engine


# -----------------------
# Health
# -----------------------
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


# -----------------------
# Angel Login (handled in service)
# -----------------------
@api_view(["GET"])
def angel_login(request):
    return Response({"status": "login handled in service"})


# -----------------------
# Market Status (placeholder)
# -----------------------
@api_view(["GET"])
def market_status(request):
    return Response({"market": "open"})


# -----------------------
# Option Chain (placeholder)
# -----------------------
@api_view(["GET"])
def option_chain(request, symbol):
    return Response({"symbol": symbol})


# -----------------------
# Dashboard (placeholder)
# -----------------------
@api_view(["GET"])
def dashboard(request):
    return Response({"dashboard": "ok"})


# -----------------------
# Strategy (placeholder)
# -----------------------
@api_view(["GET"])
def strategy(request):
    return Response({"strategy": "ok"})


# -----------------------
# P/L Calculator (placeholder)
# -----------------------
@api_view(["POST"])
def pl_calculator(request):
    return Response({"pl": "ok"})


# -----------------------
# Prices (placeholder)
# -----------------------
@api_view(["GET"])
def prices(request):
    return Response({"prices": "ok"})


# -----------------------
# Test LTP (WORKING)
# -----------------------
@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY")
    ltp = get_ltp(symbol)
    return Response({"symbol": symbol, "ltp": ltp})


# -----------------------
# ATM Strike (WORKING)
# -----------------------
@api_view(["GET"])
def atm_strike_view(request):
    symbol = request.GET.get("symbol")

    if not symbol:
        return Response(
            {"error": "symbol query param required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ltp = get_ltp(symbol)
        atm = get_atm_strike(ltp, symbol)

        return Response({
            "symbol": symbol.upper(),
            "ltp": ltp,
            "atm_strike": atm
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------------
# ✅ MARKET SENTIMENT (STEP-3 FINAL)
# -----------------------
@api_view(["GET"])
def market_sentiment_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    if symbol not in ["NIFTY", "BANKNIFTY"]:
        return Response(
            {"error": "Invalid symbol. Use NIFTY or BANKNIFTY"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        df = get_index_candles(symbol)
        sentiment = market_sentiment_engine(df)

        return Response({
            "symbol": symbol,
            "trend": sentiment["trend"],
            "strength": sentiment["strength"]
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

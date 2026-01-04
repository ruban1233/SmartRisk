from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.angel_candles import get_index_candles

from coreapi.services.market_sentiment import market_sentiment_engine
from coreapi.services.volatility_engine import volatility_engine
from coreapi.services.traffic_light_engine import traffic_light_engine
from coreapi.services.capital_risk_engine import capital_risk_engine
from coreapi.services.strategy_engine import strategy_engine


# -----------------------
# Health
# -----------------------
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


# -----------------------
# Angel Login
# -----------------------
@api_view(["GET"])
def angel_login(request):
    return Response({"status": "login handled in service"})


# -----------------------
# Market Status
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
# Dashboard
# -----------------------
@api_view(["GET"])
def dashboard(request):
    return Response({"dashboard": "ok"})


# -----------------------
# Strategy
# -----------------------
@api_view(["GET"])
def strategy(request):
    return Response({"strategy": "ok"})


# -----------------------
# P/L Calculator
# -----------------------
@api_view(["POST"])
def pl_calculator(request):
    return Response({"pl": "ok"})


# -----------------------
# Prices
# -----------------------
@api_view(["GET"])
def prices(request):
    return Response({"prices": "ok"})


# -----------------------
# Test LTP
# -----------------------
@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY")
    ltp = get_ltp(symbol)
    return Response({"symbol": symbol, "ltp": ltp})


# -----------------------
# ATM Strike
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
        return Response({"error": str(e)}, status=500)


# -----------------------
# Market Sentiment API
# -----------------------
@api_view(["GET"])
def market_sentiment_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    if symbol not in ["NIFTY", "BANKNIFTY"]:
        return Response({"error": "Invalid symbol"}, status=400)

    try:
        df = get_index_candles(symbol)
        sentiment = market_sentiment_engine(df)

        return Response({
            "symbol": symbol,
            "trend": sentiment["trend"],
            "strength": sentiment["strength"]
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# -----------------------
# ✅ Unified SmartRisk API (STEP-8)
# -----------------------
@api_view(["GET"])
def smartrisk_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    capital = float(request.GET.get("capital", 25000))

    if symbol not in ["NIFTY", "BANKNIFTY"]:
        return Response({"error": "Invalid symbol"}, status=400)

    try:
        # 1️⃣ Sentiment
        candles_df = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles_df)

        # 2️⃣ Volatility (dummy IV for now)
        volatility = volatility_engine([
            {"iv": 14},
            {"iv": 15},
            {"iv": 16}
        ])

        # 3️⃣ Traffic Light
        traffic = traffic_light_engine(
            sentiment["trend"],
            volatility["level"]
        )

        # 4️⃣ Capital Risk
        capital_info = capital_risk_engine(
            capital,
            traffic["risk_color"]
        )

        # 5️⃣ Strategy
        strategy = strategy_engine(
            sentiment["trend"],
            volatility["level"],
            traffic["risk_color"],
            capital_info
        )

        return Response({
            "symbol": symbol,
            "sentiment": sentiment,
            "volatility": volatility,
            "traffic_light": traffic,
            "capital": capital_info,
            "strategy": strategy
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)
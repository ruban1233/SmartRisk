from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import date

# =======================
# CORE SERVICES
# =======================

from coreapi.services.angel_login import get_smart_connection
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.angel_candles import get_index_candles
from coreapi.services.market_sentiment import market_sentiment_engine
from coreapi.services.volatility_engine import volatility_engine
from coreapi.services.capital_risk_engine import capital_risk_engine
from coreapi.services.strategy_engine import option_advisor_engine
from coreapi.services.investment_planner_engine import investment_planner_engine

# OPTION / TIME / GREEKS
from coreapi.services.greeks_engine import compute_greeks
from coreapi.services.pricing_engine import intrinsic_value, extrinsic_value
from coreapi.services.time_engine import time_to_expiry

# DYNAMIC RISK
from coreapi.services.dynamic_risk_engine import DynamicRiskEngine


# =======================
# SYSTEM / HEALTH
# =======================

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def angel_login(request):
    """
    Safe Angel login check
    """
    try:
        session = get_smart_connection()
        if session:
            return Response({"status": "connected"})
        else:
            return Response({"status": "failed"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})


@api_view(["GET"])
def market_status(request):
    return Response({"market": "connected"})


# =======================
# MARKET DATA
# =======================

@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        ltp = get_ltp(symbol)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response({
        "symbol": symbol,
        "ltp": ltp
    })


@api_view(["GET"])
def atm_strike_view(request):
    symbol = request.GET.get("symbol")

    if not symbol:
        return Response({"error": "symbol required"}, status=400)

    symbol = symbol.upper()

    try:
        ltp = get_ltp(symbol)
        atm = get_atm_strike(ltp, symbol)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response({
        "symbol": symbol,
        "ltp": ltp,
        "atm_strike": atm
    })


# =======================
# MARKET SENTIMENT
# =======================

@api_view(["GET"])
def market_sentiment_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        candles = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
    except Exception:
        sentiment = {"trend": "Sideways", "strength": "Weak"}

    return Response({
        "symbol": symbol,
        "trend": sentiment["trend"],
        "strength": sentiment["strength"]
    })


# =======================
# 🚦 SMART RISK ENGINE
# =======================

@api_view(["GET"])
def smartrisk_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()
    capital = float(request.GET.get("capital", 25000))

    # Spot
    try:
        spot = get_ltp(symbol)
    except Exception:
        spot = None

    # Sentiment
    try:
        candles = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
    except Exception:
        sentiment = {"trend": "Sideways", "strength": "Weak"}

    # Volatility
    try:
        vol = volatility_engine(symbol)
        iv = float(vol.get("iv", 18))
    except Exception:
        iv = 18

    iv_level = "low" if iv < 15 else "normal" if iv < 25 else "high"

    days_to_expiry = time_to_expiry(date.today())

    atm = get_atm_strike(spot or 0, symbol)
    option_price = abs((spot or 0) - atm) + 100

    greeks = compute_greeks(
        S=spot or 0,
        K=atm,
        T=days_to_expiry / 365,
        r=0.05,
        sigma=iv / 100,
        option_type="CE"
    )

    theta = greeks.get("theta", 0)

    risk_engine = DynamicRiskEngine(
        capital=capital,
        days_to_expiry=days_to_expiry,
        option_premium=option_price,
        theta=theta,
        iv_level=iv_level,
        strategy_type="unknown"
    )

    risk = risk_engine.evaluate()
    capital_info = capital_risk_engine(capital)

    option_advice = None
    if risk["signal"] != "RED":
        try:
            option_advice = option_advisor_engine(
                symbol=symbol,
                capital=int(capital)
            )
        except Exception:
            option_advice = None

    return Response({
        "symbol": symbol,
        "spot_price": spot,
        "risk": risk,
        "market": {
            "sentiment": sentiment,
            "iv": iv,
            "iv_level": iv_level,
            "days_to_expiry": days_to_expiry
        },
        "capital": capital_info,
        "option_advisory": option_advice
    })


# =======================
# 💼 INVESTMENT PLANNER
# =======================

@api_view(["GET"])
def investment_planner_view(request):

    capital = float(request.GET.get("capital", 0))
    risk_profile = request.GET.get("risk", "low")
    symbol = request.GET.get("symbol", "NIFTY").upper()

    if capital < 10000:
        return Response({
            "capital_entered": capital,
            "investment_plan": "Capital too low"
        })

    try:
        candles = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
        market_trend = sentiment["trend"]
    except Exception:
        market_trend = "Sideways"

    try:
        plan = investment_planner_engine(
            capital=capital,
            risk_profile=risk_profile,
            market_trend=market_trend
        )
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response({
        "capital_entered": capital,
        "market_trend": market_trend,
        "investment_plan": plan
    })


# =======================
# 🧮 OPTION DOCTOR
# =======================

@api_view(["GET"])
def option_doctor_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike", 0))
    option_type = request.GET.get("type", "CE")

    try:
        spot = get_ltp(symbol)
    except Exception:
        spot = 0

    option_price = abs(spot - strike) + 120
    iv = 0.18
    T = time_to_expiry(date.today()) / 365

    greeks = compute_greeks(
        S=spot,
        K=strike,
        T=T,
        r=0.05,
        sigma=iv,
        option_type=option_type
    )

    intrinsic = intrinsic_value(spot, strike, option_type)
    extrinsic = extrinsic_value(option_price, intrinsic)

    return Response({
        "symbol": symbol,
        "spot_price": spot,
        "strike": strike,
        "option_type": option_type,
        "pricing": {
            "option_price": option_price,
            "intrinsic": intrinsic,
            "extrinsic": extrinsic
        },
        "greeks": greeks
    })

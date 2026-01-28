from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import date

# =======================
# CORE SERVICES
# =======================
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.angel_candles import get_index_candles

from coreapi.services.market_sentiment import market_sentiment_engine
from coreapi.services.volatility_engine import volatility_engine
from coreapi.services.traffic_light_engine import traffic_light_engine
from coreapi.services.capital_risk_engine import capital_risk_engine
from coreapi.services.strategy_engine import strategy_engine
from coreapi.services.investment_planner_engine import investment_planner_engine
from coreapi.services.strike_engine import strike_engine
from coreapi.services.pl_engine import pl_engine

# =======================
# OPTION DOCTOR SERVICES
# =======================
from coreapi.services.greeks_engine import calculate_greeks
from coreapi.services.pricing_engine import intrinsic_value, extrinsic_value
from coreapi.services.time_engine import time_to_expiry


# =======================
# SYSTEM / HEALTH
# =======================

@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def angel_login(request):
    return Response({
        "status": "handled",
        "note": "Angel One login handled in service layer"
    })


@api_view(["GET"])
def market_status(request):
    return Response({
        "market": "Market status inferred via broker connectivity"
    })


# =======================
# PLACEHOLDER / UTILITY VIEWS
# =======================

@api_view(["GET"])
def prices(request):
    return Response({
        "status": "ok",
        "message": "Prices endpoint placeholder",
        "note": "Use /api/test-ltp/?symbol=NIFTY"
    })


@api_view(["GET"])
def dashboard(request):
    return Response({
        "status": "ok",
        "dashboard": "active",
        "note": "Dashboard aggregation placeholder"
    })


@api_view(["GET"])
def strategy(request):
    return Response({
        "status": "ok",
        "strategy": "available",
        "note": "Strategy details handled by SmartRisk engine"
    })


@api_view(["POST"])
def pl_calculator(request):
    return Response({
        "status": "ok",
        "pl": "calculated",
        "note": "P/L calculator placeholder"
    })


# =======================
# MARKET DATA
# =======================

@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    ltp = get_ltp(symbol)

    return Response({
        "symbol": symbol,
        "ltp": ltp,
        "note": "LTP works even when market is closed"
    })


@api_view(["GET"])
def atm_strike_view(request):
    symbol = request.GET.get("symbol", "").upper()

    if not symbol:
        return Response(
            {"error": "symbol query param required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    spot = get_ltp(symbol)
    atm = get_atm_strike(spot, symbol)

    return Response({
        "symbol": symbol,
        "spot_price": spot,
        "atm_strike": atm
    })


@api_view(["GET"])
def option_chain(request, symbol):
    return Response({
        "symbol": symbol,
        "status": "placeholder",
        "note": "Option chain will be integrated via Angel One"
    })


# =======================
# MARKET SENTIMENT
# =======================

@api_view(["GET"])
def market_sentiment_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    if symbol not in ["NIFTY", "BANKNIFTY"]:
        return Response(
            {"error": "Invalid symbol"},
            status=status.HTTP_400_BAD_REQUEST
        )

    candles_df = get_index_candles(symbol)
    sentiment = market_sentiment_engine(candles_df)

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

    candles_df = get_index_candles(symbol)
    sentiment = market_sentiment_engine(candles_df)

    volatility = volatility_engine([
        {"iv": 14},
        {"iv": 15},
        {"iv": 16},
    ])

    traffic = traffic_light_engine(
        sentiment["trend"],
        volatility["level"]
    )

    capital_info = capital_risk_engine(
        capital,
        traffic["risk_color"]
    )

    raw_strategy = strategy_engine(
        sentiment["trend"],
        volatility["level"],
        traffic["risk_color"],
        capital_info
    )

    if raw_strategy["strategy"] not in ["BUY_OPTION", "DEBIT_SPREAD"]:
        strategy = {
            "strategy": "DEBIT_SPREAD",
            "reason": "Fallback to safest supported strategy",
            "max_risk": capital_info["max_risk_amount"]
        }
    else:
        strategy = raw_strategy

    spot = get_ltp(symbol)

    strike_plan = strike_engine(
        symbol=symbol,
        spot_price=spot,
        strategy=strategy["strategy"],
        capital=capital,
        risk_percent=capital_info["risk_percent"]
    )

    premium_data = (
        {"buy": 120}
        if strategy["strategy"] == "BUY_OPTION"
        else {"buy": 120, "sell": 60}
    )

    pl_summary = pl_engine(
        strategy=strategy["strategy"],
        strikes=strike_plan["strikes"],
        premium_data=premium_data,
        lot_size=strike_plan["lot_size"],
        lots=strike_plan["lots_allowed"]
    )

    return Response({
        "symbol": symbol,
        "spot_price": spot,
        "sentiment": sentiment,
        "volatility": volatility,
        "traffic_light": traffic,
        "capital": capital_info,
        "strategy": strategy,
        "strike_plan": strike_plan,
        "pl_summary": pl_summary
    })


# =======================
# 💼 INVESTMENT PLANNER
# =======================

@api_view(["GET"])
def investment_planner_view(request):
    capital = float(request.GET.get("capital"))
    risk_profile = request.GET.get("risk", "low")
    symbol = request.GET.get("symbol", "NIFTY").upper()

    candles_df = get_index_candles(symbol)
    sentiment = market_sentiment_engine(candles_df)

    plan = investment_planner_engine(
        capital=capital,
        risk_profile=risk_profile,
        market_trend=sentiment["trend"]
    )

    return Response({
        "capital_entered": capital,
        "market_trend": sentiment["trend"],
        "investment_plan": plan
    })


# =======================
# 🧮 OPTION DOCTOR
# =======================

@api_view(["GET"])
def option_doctor_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike"))
    option_type = request.GET.get("type", "CE")

    spot = get_ltp(symbol)

    option_price = abs(spot - strike) + 120
    iv = 0.18

    expiry_date = date.today()
    T = time_to_expiry(expiry_date)

    greeks = calculate_greeks(
        S=spot,
        K=strike,
        T=T,
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
        "iv_percent": round(iv * 100, 2),
        "greeks": greeks,
        "pricing": {
            "option_price": round(option_price, 2),
            "intrinsic": round(intrinsic, 2),
            "extrinsic": round(extrinsic, 2)
        },
        "note": "Market closed uses last traded price from Angel One"
    })

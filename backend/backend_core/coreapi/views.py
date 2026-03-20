from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime

# =======================
# CORE SERVICES
# =======================

from coreapi.services.angel_login import get_smart_connection
from coreapi.services.angel_ltp import get_ltp
from coreapi.services.angel_candles import get_index_candles

from coreapi.services.options.option_chain_service import get_option_chain
from coreapi.services.options.option_chain_analyzer import analyze_option_chain

from coreapi.services.atm_strike import get_atm_strike
from coreapi.services.greeks_engine import compute_greeks
from coreapi.services.pricing_engine import intrinsic_value, extrinsic_value

from coreapi.services.market_sentiment import market_sentiment_engine
from coreapi.services.volatility_engine import volatility_engine

from coreapi.services.capital_risk_engine import capital_risk_engine
from coreapi.services.dynamic_risk_engine import DynamicRiskEngine
from coreapi.services.strategy.strategy_engine import option_advisor_engine
from coreapi.services.investment_planner_engine import investment_planner_engine

from coreapi.services.time_engine import time_to_expiry
from coreapi.services.iv_engine import classify_iv

from coreapi.services.options.angel_greeks_service import get_option_greeks, process_greeks
from coreapi.services.options.local_greeks_chain import build_greeks_chain
from coreapi.services.options.option_ltp import get_option_ltp_from_chain


# =========================================================
# CACHE
# =========================================================
LAST_OPTION_CHAIN = {}


def get_market_data(symbol):
    global LAST_OPTION_CHAIN
    try:
        data = get_option_chain(symbol)
        if data:
            LAST_OPTION_CHAIN[symbol] = data
            return data
    except:
        pass
    return LAST_OPTION_CHAIN.get(symbol, [])


# =========================================================
# EXPIRY
# =========================================================
def get_nearest_expiry(symbol):
    chain = get_market_data(symbol)

    if not chain:
        return None

    expiries = sorted(set([x.get("expiry") for x in chain if x.get("expiry")]))

    if not expiries:
        return None

    try:
        nearest = expiries[0]
        dt = datetime.strptime(nearest, "%Y-%m-%d")
        return dt.strftime("%d%b%Y").upper()
    except:
        return None


# =========================================================
# HEALTH
# =========================================================
@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


# =========================================================
# LOGIN
# =========================================================
@api_view(["GET"])
def angel_login(request):
    try:
        session = get_smart_connection()
        return Response({"status": "connected" if session else "failed"})
    except Exception as e:
        return Response({"error": str(e)})


# =========================================================
# MARKET STATUS
# =========================================================
@api_view(["GET"])
def market_status(request):
    return Response({"market": "connected"})


# =========================================================
# LTP
# =========================================================
@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    return Response({"symbol": symbol, "ltp": get_ltp(symbol)})


# =========================================================
# ATM STRIKE
# =========================================================
@api_view(["GET"])
def atm_strike_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    spot = get_ltp(symbol)
    atm = get_atm_strike(spot, symbol)

    return Response({
        "symbol": symbol,
        "spot": spot,
        "atm_strike": atm
    })


# =========================================================
# MARKET SENTIMENT
# =========================================================
@api_view(["GET"])
def market_sentiment_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        candles = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
    except:
        sentiment = {"trend": "Sideways", "strength": "Weak"}

    return Response(sentiment)


# =========================================================
# OPTION CHAIN ANALYSIS
# =========================================================
@api_view(["GET"])
def option_chain_analysis_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()

    spot = get_ltp(symbol)
    chain = get_market_data(symbol)

    if not chain:
        return Response({"error": "No chain"})

    analysis = analyze_option_chain(chain, spot)

    return Response(analysis)


# =========================================================
# SMART RISK ENGINE
# =========================================================
@api_view(["GET"])
def smartrisk_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()
    capital = float(request.GET.get("capital", 25000))

    spot = get_ltp(symbol)
    chain = get_market_data(symbol)

    if not chain:
        return Response({"error": "No option chain"})

    analysis = analyze_option_chain(chain, spot)
    atm = analysis.get("atm_strike")

    closest = min(chain, key=lambda x: abs(float(
        x.get("strike", x.get("strikePrice", 0))
    ) - float(atm)))

    target_strike = float(closest.get("strike", closest.get("strikePrice")))

    ce_option = None

    for x in chain:
        s = float(x.get("strike", x.get("strikePrice", 0)))

        if s == target_strike:
            opt_type = x.get("option_type") or x.get("optionType")

            if opt_type == "CE":
                ce_option = x

    premium = get_option_ltp_from_chain(ce_option) or 100

    greeks = compute_greeks(
        S=spot,
        K=target_strike,
        T=0.01,
        r=0.05,
        sigma=0.2,
        option_type="CE"
    )

    risk = DynamicRiskEngine(
        capital=capital,
        days_to_expiry=5,
        option_premium=premium,
        theta=greeks.get("theta", 0),
        iv_level="normal",
        strategy_type="unknown"
    ).evaluate()

    return Response({
        "symbol": symbol,
        "spot": spot,
        "atm_used": target_strike,
        "premium": premium,
        "greeks": greeks,
        "risk": risk,
        "capital": capital_risk_engine(capital)
    })


# =========================================================
# INVESTMENT PLANNER
# =========================================================
@api_view(["GET"])
def investment_planner_view(request):

    capital = float(request.GET.get("capital", 0))
    risk_profile = request.GET.get("risk", "low")
    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        candles = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
        market_trend = sentiment.get("trend", "Sideways")
    except:
        market_trend = "Sideways"

    plan = investment_planner_engine(
        capital=capital,
        risk_profile=risk_profile,
        market_trend=market_trend
    )

    return Response({
        "capital": capital,
        "market_trend": market_trend,
        "plan": plan
    })


# =========================================================
# OPTION DOCTOR
# =========================================================
@api_view(["GET"])
def option_doctor_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike", 0))

    spot = get_ltp(symbol)

    greeks = compute_greeks(
        S=spot,
        K=strike,
        T=0.01,
        r=0.05,
        sigma=0.2,
        option_type="CE"
    )

    intrinsic = intrinsic_value(spot, strike, "CE")
    extrinsic = extrinsic_value(100, intrinsic)

    return Response({
        "symbol": symbol,
        "spot": spot,
        "strike": strike,
        "greeks": greeks,
        "pricing": {
            "intrinsic": intrinsic,
            "extrinsic": extrinsic
        }
    })


# =========================================================
# IV TEST
# =========================================================
@api_view(["GET"])
def iv_test_view(request):

    iv = request.GET.get("iv")

    if iv is None:
        return Response({"error": "Provide iv value"})

    return Response({
        "input_iv": float(iv),
        "classification": classify_iv(float(iv))
    })


# =========================================================
# OPTION GREEKS
# =========================================================
@api_view(["GET"])
def option_greeks_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()

    spot = get_ltp(symbol)
    expiry = get_nearest_expiry(symbol)

    raw = get_option_greeks(symbol, expiry)

    if raw.get("status"):
        data = process_greeks(raw)
        if data:
            return Response({
                "symbol": symbol,
                "expiry": expiry,
                "greeks": data[:30]
            })

    return Response({
        "symbol": symbol,
        "expiry": expiry,
        "greeks": build_greeks_chain(spot)
    })


# =========================================================
# TEST OPTION PRICE
# =========================================================
@api_view(["GET"])
def test_option_price(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike", 0))

    try:
        spot = get_ltp(symbol)
        chain = get_market_data(symbol)

        if not chain:
            return Response({"error": "No option chain data"})

        closest = min(chain, key=lambda x: abs(float(
            x.get("strike", x.get("strikePrice", 0))
        ) - float(strike)))

        target_strike = float(closest.get("strike", closest.get("strikePrice")))

        ce_option = None
        pe_option = None

        for x in chain:
            s = float(x.get("strike", x.get("strikePrice", 0)))

            if s == target_strike:

                opt_type = (
                    x.get("option_type")
                    or x.get("optionType")
                    or x.get("type")
                )

                if opt_type == "CE":
                    ce_option = x

                elif opt_type == "PE":
                    pe_option = x

        ce_price = get_option_ltp_from_chain(ce_option)
        pe_price = get_option_ltp_from_chain(pe_option)

        return Response({
            "symbol": symbol,
            "spot": spot,
            "requested_strike": strike,
            "used_strike": target_strike,
            "CE_price": ce_price,
            "PE_price": pe_price,
            "debug_sample": chain[:2]
        })

    except Exception as e:
        return Response({"error": str(e)})
# =========================================================
# FULL OPTION CHAIN (FINAL CLEAN VERSION)
# =========================================================
@api_view(["GET"])
def full_option_chain_view(request):

    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        spot = get_ltp(symbol)
        chain = get_market_data(symbol)

        if not chain:
            return Response({"error": "No option chain data"})

        # ======================================
        # 🔥 REMOVE NULL LTP (FINAL FIX)
        # ======================================
        clean_chain = [
            x for x in chain
            if x.get("ltp") is not None
        ]

        # ======================================
        # 🔥 SORT BY STRIKE
        # ======================================
        clean_chain = sorted(clean_chain, key=lambda x: x["strike"])

        return Response({
            "symbol": symbol,
            "spot": spot,
            "total_strikes": len(clean_chain),
            "data": clean_chain
        })

    except Exception as e:
        return Response({"error": str(e)})
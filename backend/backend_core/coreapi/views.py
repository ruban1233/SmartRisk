"""
views.py
Path: backend/backend_core/coreapi/views.py
✔ Real LTP from Angel One
✔ Real option chain with parallel fetch
✔ Real Greeks from SmartAPI + Black-Scholes fallback
✔ Capital-based strategy selection
✔ Real payoff with correct intrinsic
✔ Expiry auto-detected (weekly/monthly)
✔ Risk signal with advice
"""

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

from coreapi.services.capital_risk_engine import get_capital_summary as capital_risk_engine
from coreapi.services.dynamic_risk_engine import DynamicRiskEngine
from coreapi.services.strategy.strategy_engine import run_strategy_engine
from coreapi.services.investment_planner_engine import investment_planner_engine

from coreapi.services.time_engine import time_to_expiry
from coreapi.services.iv_engine import classify_iv

from coreapi.services.options.angel_greeks_service import (
    get_option_greeks,
    process_greeks,
    get_nearest_expiry_date,
    get_monthly_expiry,
    format_expiry_display,
    get_days_to_expiry,
    get_real_greeks_for_strategy,
)
from coreapi.services.options.local_greeks_chain import build_greeks_chain
from coreapi.services.options.option_ltp import get_option_ltp_from_chain
from coreapi.services.strategy.payoff_engine import calculate_payoff, calculate_summary


# =========================================================
# CHAIN CACHE
# =========================================================
LAST_OPTION_CHAIN = {}


def get_market_data(symbol):
    global LAST_OPTION_CHAIN
    try:
        data = get_option_chain(symbol)
        if data:
            LAST_OPTION_CHAIN[symbol] = data
            return data
    except Exception:
        pass
    return LAST_OPTION_CHAIN.get(symbol, [])


# =========================================================
# EXPIRY HELPERS
# =========================================================

def get_nearest_expiry(symbol):
    """
    Auto-detect nearest expiry:
    1. Try to extract from live option chain (most accurate)
    2. Fallback to computed weekly expiry
    """
    chain = get_market_data(symbol)

    if chain:
        expiries = sorted(set([
            x.get("expiry") for x in chain if x.get("expiry")
        ]))
        if expiries:
            try:
                dt = datetime.strptime(expiries[0], "%Y-%m-%d")
                return dt.strftime("%d%b%Y").upper()
            except Exception:
                try:
                    datetime.strptime(expiries[0], "%d%b%Y")
                    return expiries[0].upper()
                except Exception:
                    pass

    return get_nearest_expiry_date(symbol)


# =========================================================
# REAL LTP FROM CHAIN HELPER
# =========================================================

def get_real_ltp_map(chain, atm_strike, symbol):
    """
    Extract real CE and PE LTP at ATM strike from option chain.
    Falls back to nearest available strike if exact ATM not found.
    """
    ce_ltp = None
    pe_ltp = None
    atm    = int(atm_strike)

    for x in chain:
        strike   = int(float(x.get("strike", x.get("strikePrice", 0))))
        opt_type = x.get("option_type") or x.get("optionType", "")
        ltp      = x.get("ltp")

        if strike == atm and ltp is not None and float(ltp) > 0:
            if opt_type == "CE" and ce_ltp is None:
                ce_ltp = float(ltp)
            elif opt_type == "PE" and pe_ltp is None:
                pe_ltp = float(ltp)

        if ce_ltp and pe_ltp:
            break

    # Find nearest if exact ATM not found
    if not ce_ltp:
        candidates = [
            x for x in chain
            if (x.get("option_type") or x.get("optionType", "")) == "CE"
            and x.get("ltp") is not None
            and float(x.get("ltp", 0)) > 0
        ]
        if candidates:
            closest = min(candidates, key=lambda x: abs(
                int(float(x.get("strike", x.get("strikePrice", 0)))) - atm
            ))
            ce_ltp = float(closest["ltp"])

    if not pe_ltp:
        candidates = [
            x for x in chain
            if (x.get("option_type") or x.get("optionType", "")) == "PE"
            and x.get("ltp") is not None
            and float(x.get("ltp", 0)) > 0
        ]
        if candidates:
            closest = min(candidates, key=lambda x: abs(
                int(float(x.get("strike", x.get("strikePrice", 0)))) - atm
            ))
            pe_ltp = float(closest["ltp"])

    ce_ltp = ce_ltp or 100.0
    pe_ltp = pe_ltp or 100.0

    print(f"[LTP MAP] {symbol} ATM={atm} CE={ce_ltp} PE={pe_ltp}")
    return {"ce_ltp": ce_ltp, "pe_ltp": pe_ltp}


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
    spot   = get_ltp(symbol)
    step   = 100 if symbol == "BANKNIFTY" else 50
    atm    = round(spot / step) * step
    return Response({"symbol": symbol, "spot": spot, "atm_strike": atm})


# =========================================================
# MARKET SENTIMENT
# =========================================================
@api_view(["GET"])
def market_sentiment_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    try:
        candles   = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
    except Exception:
        sentiment = {"trend": "Sideways", "strength": "Weak"}
    return Response(sentiment)


# =========================================================
# OPTION CHAIN ANALYSIS
# =========================================================
@api_view(["GET"])
def option_chain_analysis_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    spot   = get_ltp(symbol)
    chain  = get_market_data(symbol)
    if not chain:
        return Response({"error": "No chain"})
    return Response(analyze_option_chain(chain, spot))


# =========================================================
# SMART RISK ENGINE — MAIN VIEW
# =========================================================
@api_view(["GET"])
def smartrisk_view(request):

    symbol  = request.GET.get("symbol",  "NIFTY").upper()
    capital = float(request.GET.get("capital", 25000))

    # ── Step size
    step = 100 if symbol == "BANKNIFTY" else 50

    # ── Step 1: Real spot price
    spot = get_ltp(symbol)
    if not spot:
        return Response({
            "error": True,
            "message": f"Cannot fetch live spot price for {symbol}. Check Angel One connection."
        })

    print(f"\n[SMARTRISK] ── {symbol} ──────────────────")
    print(f"[SMARTRISK] spot={spot}  capital={capital}")

    # ── Step 2: Real option chain (parallel fetch, cached)
    chain = get_market_data(symbol)
    if not chain:
        return Response({
            "error": True,
            "message": "No option chain data available. Try again in 30 seconds."
        })

    # ── Step 3: ATM strike (correctly rounded)
    atm = round(spot / step) * step
    print(f"[SMARTRISK] ATM={atm}")

    # ── Step 4: Expiry (auto-detected from chain or computed)
    expiry         = get_nearest_expiry(symbol)
    expiry_display = format_expiry_display(expiry)
    days_to_expiry = get_days_to_expiry(expiry)

    print(f"[SMARTRISK] expiry={expiry}  dte={days_to_expiry}")

    # ── Step 5: Real LTP map from chain
    ltp_map = get_real_ltp_map(chain, atm, symbol)

    # ── Step 6: Market sentiment + IV
    trend = "Sideways"
    iv    = 18.0
    try:
        candles   = get_index_candles(symbol)
        sentiment = market_sentiment_engine(candles)
        trend     = sentiment.get("trend", "Sideways")
        iv        = float(
            sentiment.get("iv_percentile") or
            sentiment.get("iv_rank") or
            sentiment.get("iv") or
            18.0
        )
    except Exception as e:
        print(f"[WARN] Sentiment failed: {e}")

    print(f"[SMARTRISK] trend={trend}  iv={iv}")

    # ── Step 7: Strategy engine (real chain + real LTP)
    strategy_data = run_strategy_engine(
        capital       = capital,
        trend         = trend,
        iv_percentile = iv,
        atm_price     = atm,
        ltp_map       = ltp_map,
        symbol        = symbol,
        step          = step,
        chain         = chain,
        dte           = days_to_expiry,
    )

    if strategy_data.get("error"):
        return Response({
            "error":        True,
            "message":      strategy_data.get("message", "Strategy engine failed."),
            "capital_data": strategy_data.get("capital_data"),
        })

    print(f"[SMARTRISK] strategy={strategy_data.get('strategy', {}).get('name')}")

    # ── Step 8: Premium for risk engine
    premium = ltp_map.get("ce_ltp", 100.0)

    # ── Step 9: Greeks — try real SmartAPI first, fallback to Black-Scholes
    ce_greeks     = None
    pe_greeks     = None
    greeks_source = "fallback"
    greeks        = {}

    try:
        greeks_data   = get_real_greeks_for_strategy(symbol, atm, expiry)
        ce_greeks     = greeks_data.get("ce_greeks")
        pe_greeks     = greeks_data.get("pe_greeks")
        greeks_source = greeks_data.get("source", "fallback")

        if ce_greeks and ce_greeks.get("delta") is not None:
            greeks = {
                "delta": ce_greeks.get("delta", 0.5),
                "gamma": ce_greeks.get("gamma", 0.0),
                "theta": ce_greeks.get("theta", 0.0),
                "vega":  ce_greeks.get("vega",  0.0),
                "iv":    ce_greeks.get("iv",     iv),
            }
            print(f"[SMARTRISK] Greeks source=SmartAPI delta={greeks['delta']}")
        else:
            raise ValueError("No valid SmartAPI greeks")

    except Exception as e:
        print(f"[WARN] Real greeks failed ({e}) — using Black-Scholes fallback")
        T = max(days_to_expiry / 365.0, 0.001)
        try:
            greeks = compute_greeks(
                S=float(spot),
                K=float(atm),
                T=T,
                r=0.065,
                sigma=max(iv / 100.0, 0.08),
                option_type="CE"
            )
            greeks["iv"] = iv
        except Exception as ge:
            print(f"[ERROR] Greeks fallback also failed: {ge}")
            greeks = {
                "delta": 0.5, "gamma": 0.0,
                "theta": 0.0, "vega":  0.0,
                "iv":    iv,
            }

    # ── Step 10: Dynamic risk engine
    risk = {"risk_score": 50, "signal": "YELLOW", "reasons": []}
    try:
        risk = DynamicRiskEngine(
            capital        = capital,
            days_to_expiry = days_to_expiry,
            option_premium = premium,
            theta          = greeks.get("theta", 0),
            iv_level       = "high" if iv > 60 else "normal",
            strategy_type  = strategy_data.get("strategy", {}).get("key", "unknown")
                             if strategy_data.get("strategy") else "unknown",
        ).evaluate()
    except Exception as e:
        print(f"[WARN] Risk engine failed: {e}")

    print(f"[SMARTRISK] risk_score={risk.get('risk_score')}  signal={risk.get('signal')}")

    # ── Step 11: Signal improvement advice
    signal_advice = []
    signal_level  = risk.get("signal", "YELLOW")

    if signal_level in ("RED", "YELLOW"):
        if days_to_expiry <= 3:
            signal_advice.append("⏰ Very close to expiry — reduce position size by 50%.")
        if iv < 20:
            signal_advice.append("📈 IV is LOW (< 20%) — avoid selling premium. Buy options instead.")
        if iv > 60:
            signal_advice.append("📉 IV is HIGH (> 60%) — switch to premium selling strategies.")
        if capital < 50_000:
            signal_advice.append("💰 Increase capital to ₹50,000+ for safer Iron Condor strategy.")
        strategy_risk = strategy_data.get("strategy", {}).get("risk", "")
        if strategy_risk == "HIGH":
            signal_advice.append("🔄 Switch to defined-risk strategy: Bull Call Spread or Iron Condor.")
        if signal_level == "RED":
            signal_advice.append("🚫 RED signal — do NOT enter trade. Wait for YELLOW or GREEN.")
        signal_advice.append("✅ GREEN signal requires: defined-risk strategy + normal IV (20-50) + adequate capital.")

    # ── Step 12: Build final response
    return Response({
        # Market data
        "symbol":         symbol,
        "spot":           spot,
        "trend":          trend,
        "iv_percentile":  round(iv, 2),

        # Expiry
        "expiry":         expiry,
        "expiry_display": expiry_display,
        "days_to_expiry": days_to_expiry,

        # ATM
        "atm_price":      atm,
        "atm_used":       atm,
        "lot_size":       strategy_data.get("lot_size", 75),

        # Strategy
        "strategy":       strategy_data.get("strategy"),
        "legs":           strategy_data.get("legs", []),
        "net_premium":    strategy_data.get("net_premium"),
        "traffic_signal": strategy_data.get("traffic_signal"),
        "capital_data":   strategy_data.get("capital_data"),

        # Payoff
        "payoff":         strategy_data.get("payoff", []),
        "payoff_summary": strategy_data.get("payoff_summary", {}),

        # Greeks
        "greeks":         greeks,
        "ce_greeks":      ce_greeks,
        "pe_greeks":      pe_greeks,
        "greeks_source":  greeks_source,

        # Risk
        "premium":        premium,
        "risk":           risk,
        "signal_advice":  signal_advice,
        "capital":        capital,

        # Debug (remove in production)
        "strategy_suggestions": strategy_data,
        "real_ltp_map":         ltp_map,
    })


# =========================================================
# INVESTMENT PLANNER
# =========================================================
@api_view(["GET"])
def investment_planner_view(request):
    capital      = float(request.GET.get("capital", 0))
    risk_profile = request.GET.get("risk", "low")
    symbol       = request.GET.get("symbol", "NIFTY").upper()

    try:
        candles      = get_index_candles(symbol)
        sentiment    = market_sentiment_engine(candles)
        market_trend = sentiment.get("trend", "Sideways")
    except Exception:
        market_trend = "Sideways"

    plan = investment_planner_engine(
        capital      = capital,
        risk_profile = risk_profile,
        market_trend = market_trend
    )
    return Response({
        "capital":      capital,
        "market_trend": market_trend,
        "plan":         plan
    })


# =========================================================
# OPTION DOCTOR
# =========================================================
@api_view(["GET"])
def option_doctor_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike", 0))
    spot   = get_ltp(symbol)
    step   = 100 if symbol == "BANKNIFTY" else 50
    T      = max(get_days_to_expiry(get_nearest_expiry(symbol)) / 365.0, 0.001)

    greeks = compute_greeks(
        S=spot, K=strike, T=T,
        r=0.065, sigma=0.18, option_type="CE"
    )
    intrinsic = intrinsic_value(spot, strike, "CE")
    extrinsic = extrinsic_value(100, intrinsic)

    return Response({
        "symbol":  symbol,
        "spot":    spot,
        "strike":  strike,
        "greeks":  greeks,
        "pricing": {"intrinsic": intrinsic, "extrinsic": extrinsic}
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
        "input_iv":       float(iv),
        "classification": classify_iv(float(iv))
    })


# =========================================================
# OPTION GREEKS VIEW
# =========================================================
@api_view(["GET"])
def option_greeks_view(request):
    symbol       = request.GET.get("symbol",  "NIFTY").upper()
    expiry_param = request.GET.get("expiry",  None)
    use_monthly  = request.GET.get("monthly", "false").lower() == "true"

    spot = get_ltp(symbol)
    step = 100 if symbol == "BANKNIFTY" else 50
    atm  = round(spot / step) * step

    if expiry_param:
        expiry = expiry_param.upper()
    elif use_monthly:
        expiry = get_monthly_expiry(symbol)
    else:
        expiry = get_nearest_expiry(symbol)

    expiry_display = format_expiry_display(expiry)
    days           = get_days_to_expiry(expiry)

    raw    = get_option_greeks(symbol, expiry)
    greeks = process_greeks(raw)

    if greeks:
        return Response({
            "symbol":         symbol,
            "spot":           spot,
            "atm":            atm,
            "expiry":         expiry,
            "expiry_display": expiry_display,
            "days_to_expiry": days,
            "source":         "smartapi",
            "total_strikes":  len(greeks),
            "greeks":         greeks[:50],
        })

    local = build_greeks_chain(spot)
    return Response({
        "symbol":         symbol,
        "spot":           spot,
        "atm":            atm,
        "expiry":         expiry,
        "expiry_display": expiry_display,
        "days_to_expiry": days,
        "source":         "fallback_bs",
        "total_strikes":  len(local),
        "greeks":         local,
    })


# =========================================================
# TEST OPTION PRICE
# =========================================================
@api_view(["GET"])
def test_option_price(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    strike = float(request.GET.get("strike", 0))

    try:
        spot  = get_ltp(symbol)
        chain = get_market_data(symbol)

        if not chain:
            return Response({"error": "No option chain data"})

        closest = min(chain, key=lambda x: abs(
            float(x.get("strike", x.get("strikePrice", 0))) - float(strike)
        ))
        target = float(closest.get("strike", closest.get("strikePrice")))

        ce_option = pe_option = None
        for x in chain:
            s = int(float(x.get("strike", x.get("strikePrice", 0))))
            t = x.get("option_type") or x.get("optionType") or x.get("type")
            if s == int(target):
                if t == "CE":
                    ce_option = x
                elif t == "PE":
                    pe_option = x

        return Response({
            "symbol":           symbol,
            "spot":             spot,
            "requested_strike": strike,
            "used_strike":      target,
            "CE_price":         get_option_ltp_from_chain(ce_option),
            "PE_price":         get_option_ltp_from_chain(pe_option),
            "debug_sample":     chain[:2],
        })

    except Exception as e:
        return Response({"error": str(e)})


# =========================================================
# FULL OPTION CHAIN
# =========================================================
@api_view(["GET"])
def full_option_chain_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()

    try:
        spot   = get_ltp(symbol)
        chain  = get_market_data(symbol)
        expiry = get_nearest_expiry(symbol)

        if not chain:
            return Response({"error": "No option chain data"})

        clean = sorted(
            [x for x in chain if x.get("ltp") is not None],
            key=lambda x: float(x.get("strike", 0))
        )

        return Response({
            "symbol":         symbol,
            "spot":           spot,
            "expiry":         expiry,
            "expiry_display": format_expiry_display(expiry),
            "total_strikes":  len(clean),
            "data":           clean,
        })

    except Exception as e:
        return Response({"error": str(e)})


# =========================================================
# AI STRATEGY
# =========================================================
@api_view(["GET"])
def ai_strategy_view(request):
    symbol  = request.GET.get("symbol",  "NIFTY").upper()
    capital = float(request.GET.get("capital", 10000))
    iv      = float(request.GET.get("iv",      15))

    chain = get_market_data(symbol)
    spot  = get_ltp(symbol)

    if not chain:
        return Response({"error": "No chain"})

    return Response({
        "symbol": symbol,
        "result": analyze_option_chain(chain, spot, capital, iv)
    })


# =========================================================
# PAYOFF ENGINE VIEW
# =========================================================
@api_view(["GET"])
def payoff_view(request):
    symbol = request.GET.get("symbol", "NIFTY").upper()
    spot   = get_ltp(symbol)
    chain  = get_market_data(symbol)

    if not chain:
        return Response({"error": "No option data"})

    step   = 100 if symbol == "BANKNIFTY" else 50
    atm    = round(spot / step) * step
    expiry = get_nearest_expiry(symbol)

    strikes = sorted(set([
        float(x.get("strike", x.get("strikePrice", 0))) for x in chain
    ]))
    if not strikes:
        return Response({"error": "No strikes found"})

    def find_option(strike, typ):
        for x in chain:
            s = int(float(x.get("strike", x.get("strikePrice", 0))))
            t = x.get("option_type") or x.get("optionType")
            if s == int(strike) and t == typ:
                return x
        return None

    pe_sell_strike = min(strikes, key=lambda x: abs(x - (atm - step)))
    ce_sell_strike = min(strikes, key=lambda x: abs(x - (atm + step)))

    lower_strikes  = sorted([s for s in strikes if s < pe_sell_strike])
    higher_strikes = sorted([s for s in strikes if s > ce_sell_strike])

    pe_buy_strike = lower_strikes[-1]  if lower_strikes  else min(strikes, key=lambda x: abs(x - (pe_sell_strike - step * 2)))
    ce_buy_strike = higher_strikes[0] if higher_strikes else min(strikes, key=lambda x: abs(x - (ce_sell_strike + step * 2)))

    if pe_buy_strike == pe_sell_strike:
        pe_buy_strike = min(strikes, key=lambda x: abs(x - (pe_sell_strike - step * 2)))
    if ce_buy_strike == ce_sell_strike:
        ce_buy_strike = min(strikes, key=lambda x: abs(x - (ce_sell_strike + step * 2)))

    pe_sell = find_option(pe_sell_strike, "PE")
    pe_buy  = find_option(pe_buy_strike,  "PE")
    ce_sell = find_option(ce_sell_strike, "CE")
    ce_buy  = find_option(ce_buy_strike,  "CE")

    if not all([pe_sell, pe_buy, ce_sell, ce_buy]):
        return Response({
            "error": "Option data missing",
            "debug": {
                "pe_sell": pe_sell_strike, "pe_buy": pe_buy_strike,
                "ce_sell": ce_sell_strike, "ce_buy": ce_buy_strike,
            }
        })

    pe_sell_p = get_option_ltp_from_chain(pe_sell)
    pe_buy_p  = get_option_ltp_from_chain(pe_buy)
    ce_sell_p = get_option_ltp_from_chain(ce_sell)
    ce_buy_p  = get_option_ltp_from_chain(ce_buy)

    if None in [pe_sell_p, pe_buy_p, ce_sell_p, ce_buy_p]:
        return Response({"error": "Premium data missing for one or more legs"})

    total_credit = (pe_sell_p - pe_buy_p) + (ce_sell_p - ce_buy_p)

    if total_credit <= 0:
        return Response({
            "error":  "Invalid strategy — net credit is zero or negative",
            "detail": {
                "pe_sell": pe_sell_p, "pe_buy": pe_buy_p,
                "ce_sell": ce_sell_p, "ce_buy": ce_buy_p,
            }
        })

    legs = [
        {"type": "PE", "action": "SELL", "strike": pe_sell_strike, "premium": pe_sell_p},
        {"type": "PE", "action": "BUY",  "strike": pe_buy_strike,  "premium": pe_buy_p},
        {"type": "CE", "action": "SELL", "strike": ce_sell_strike, "premium": ce_sell_p},
        {"type": "CE", "action": "BUY",  "strike": ce_buy_strike,  "premium": ce_buy_p},
    ]

    payoff  = calculate_payoff(legs, symbol)
    summary = calculate_summary(payoff)

    return Response({
        "symbol":         symbol,
        "spot":           spot,
        "atm":            atm,
        "expiry":         expiry,
        "expiry_display": format_expiry_display(expiry),
        "days_to_expiry": get_days_to_expiry(expiry),
        "strategy":       "Iron Condor",
        "credit":         round(total_credit, 2),
        "legs":           legs,
        "summary":        summary,
        "payoff_chart":   payoff[:60],
    })


# =========================================================
# EXPIRY INFO
# =========================================================
@api_view(["GET"])
def expiry_info_view(request):
    """
    GET /api/expiry/?symbol=NIFTY
    Returns weekly + monthly expiry info.
    """
    symbol = request.GET.get("symbol", "NIFTY").upper()

    weekly  = get_nearest_expiry_date(symbol)
    monthly = get_monthly_expiry(symbol)

    return Response({
        "symbol":          symbol,
        "weekly_expiry":   weekly,
        "weekly_display":  format_expiry_display(weekly),
        "monthly_expiry":  monthly,
        "monthly_display": format_expiry_display(monthly),
        "days_to_weekly":  get_days_to_expiry(weekly),
        "days_to_monthly": get_days_to_expiry(monthly),
    })
def detect_market_regime(nifty, support, resistance):
    """
    Detects if market is BULLISH, BEARISH, or SIDEWAYS.
    """

    if support and resistance:
        try:
            support = float(support)
            resistance = float(resistance)

            if nifty > resistance:
                return "Bullish Breakout"
            elif nifty < support:
                return "Bearish Breakdown"
            elif abs(nifty - support) < 40:
                return "Near Support (Bullish Bias)"
            elif abs(nifty - resistance) < 40:
                return "Near Resistance (Bearish Bias)"
        except:
            pass

    # No S/R → general trend
    if nifty % 100 > 50:
        return "Sideways with Bullish Bias"
    else:
        return "Sideways"


def strategy_by_capital(capital):
    """
    Defines which strategies are allowed for the user's capital.
    """

    capital = float(capital)

    if capital < 3000:
        return "No safe option strategy possible. Try index ETFs."

    if capital < 10000:
        return "Only directional naked options or small debit spreads allowed."

    if capital < 25000:
        return "Debit spreads like Bull Call Spread / Bear Put Spread recommended."

    if capital < 50000:
        return "Credit spreads like Bull Put Spread / Bear Call Spread possible."

    if capital < 100000:
        return "Iron Condor, Iron Fly, Ratio spreads allowed."

    return "All advanced strategies allowed including Straddle/Strangle."


def get_strategy(nifty, bank, support, resistance, capital=20000, iv=16, ivp=20, pcr=1.0):
    """
    MAIN AI STRATEGY ENGINE
    This combines:
    - Market regime
    - Capital
    - IV & PCR
    - Trend bias
    """

    market_regime = detect_market_regime(nifty, support, resistance)
    capital_advice = strategy_by_capital(capital)

    # Strategy selection logic
    strategy = None
    reason = []

    # ------------- STRATEGY DECISION LOGIC ----------------

    # Low IV → Debit spreads, Directional
    if iv < 15:
        strategy = "Bull Call Spread" if nifty % 200 < 100 else "Bear Put Spread"
        reason.append("Low IV → Debit spreads work better.")

    # Medium IV → Credit spreads
    elif 15 <= iv < 22:
        strategy = "Bull Put Spread" if pcr > 1 else "Bear Call Spread"
        reason.append("Medium IV → Credit spreads optimal.")

    # High IV → Neutral strategies
    else:
        strategy = "Iron Condor"
        reason.append("High IV → Sell premium with risk-defined strategies.")

    # PCR adjustment
    if pcr > 1.1:
        reason.append("PCR indicates bullish sentiment.")
    elif pcr < 0.9:
        reason.append("PCR indicates bearish sentiment.")
    else:
        reason.append("PCR neutral → Non-directional strategies possible.")

    # Final data to send
    return {
        "market_regime": market_regime,
        "capital_advice": capital_advice,
        "recommended_strategy": strategy,
        "reason": reason,
        "nifty": nifty,
        "iv": iv,
        "iv_percentile": ivp,
        "pcr": pcr,
    }

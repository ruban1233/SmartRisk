def filter_by_capital(candidates, capital):

    allowed = []

    for s in candidates:

        # ✅ HANDLE STRING FORMAT
        if isinstance(s, str):
            allowed.append({
                "strategy": s,
                "margin_required": 1000  # default small
            })
            continue

        # ✅ HANDLE DICT FORMAT
        if isinstance(s, dict):
            margin = s.get("margin_required", 0)

            if margin <= capital:
                allowed.append(s)

    return allowed


def option_advisor_engine(symbol, trend="Sideways", iv=18, capital=25000):

    option_chain = get_option_chain(symbol)

    if not option_chain:
        return {"error": "Option chain not available"}

    spot_price = option_chain[0].get("ltp", 0)

    analysis = analyze_option_chain(option_chain, spot_price)

    support = analysis.get("support")
    resistance = analysis.get("resistance")
    bias = analysis.get("bias")

    candidates = get_strategy_candidates(trend, iv)

    allowed = filter_by_capital(candidates, capital)

    results = []

    for s in allowed:

        # ✅ SAFE ACCESS
        if isinstance(s, dict):
            strategy_name = s.get("strategy", "Unknown")
            margin_required = s.get("margin_required", 0)
            strikes = s.get("strikes", {})
            premium_data = s.get("premium_data", {})
            lot_size = s.get("lot_size", 50)

        else:
            # fallback
            strategy_name = str(s)
            margin_required = 1000
            strikes = {}
            premium_data = {}
            lot_size = 50

        try:
            pl = calculate_pl(
                strategy=strategy_name,
                strikes=strikes,
                premium_data=premium_data,
                lot_size=lot_size,
                lots=1
            )
        except:
            pl = {"max_profit": None, "max_loss": None}

        results.append({
            "strategy": strategy_name,
            "margin_required": margin_required,
            "max_profit": pl.get("max_profit"),
            "max_loss": pl.get("max_loss")
        })

    return {
        "support": support,
        "resistance": resistance,
        "bias": bias,
        "strategies": results
    }
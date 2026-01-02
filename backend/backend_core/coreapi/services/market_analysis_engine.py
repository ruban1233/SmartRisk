def analyze_market(pcr, iv, support, resistance, ce_oi_change, pe_oi_change):

    # -------- TREND DETECTION --------
    if pcr > 1.3:
        trend = "Strong Bullish"
    elif 1.0 < pcr <= 1.3:
        trend = "Mild Bullish"
    elif 0.7 <= pcr <= 1.0:
        trend = "Neutral / Sideways"
    elif 0.5 <= pcr < 0.7:
        trend = "Mild Bearish"
    else:
        trend = "Strong Bearish"

    # -------- TREND SCORE --------
    trend_strength = int(pcr * 50)
    if trend_strength > 90:
        trend_strength = 90
    if trend_strength < 10:
        trend_strength = 10

    # -------- VOLATILITY ANALYSIS --------
    if iv < 12:
        vol_comment = "Low volatility — premium selling favorable."
    elif iv < 20:
        vol_comment = "Moderate volatility — mixed strategies work."
    else:
        vol_comment = "High volatility — hedged debit strategies advisable."

    # -------- OI SHIFT ANALYSIS --------
    if pe_oi_change > ce_oi_change:
        writers_bias = "Put writers dominating → bullish signal."
    elif ce_oi_change > pe_oi_change:
        writers_bias = "Call writers dominating → bearish pressure."
    else:
        writers_bias = "Neutral OI shift."

    # -------- EXPERT LEVEL SUMMARY --------
    expert_summary = f"""
Market Trend: {trend}
Trend Strength: {trend_strength}/100
PCR: {pcr}
IV: {iv}%
Support Zone: {support}
Resistance Zone: {resistance}

OI Shift:
- CE OI Change: {ce_oi_change}
- PE OI Change: {pe_oi_change}
→ {writers_bias}

Volatility Insight:
{vol_comment}

Expert Commentary:
The current derivatives structure indicates {trend.lower()} momentum.
Put writers around support zones show strong defense.
If resistance at {resistance} breaks, expect continuation.
If support at {support} breaks, expect reversal.
"""

    # -------- STRATEGY RECOMMENDATION --------
    if trend in ["Strong Bullish", "Mild Bullish"] and iv < 20:
        strategy = "Bull Put Spread"
    elif trend == "Neutral / Sideways" and iv < 20:
        strategy = "Iron Condor"
    elif trend in ["Mild Bearish", "Strong Bearish"] and iv > 15:
        strategy = "Bear Put Spread"
    else:
        strategy = "Straddle or Strangle"

    return {
        "trend": trend,
        "trend_strength": trend_strength,
        "volatility_comment": vol_comment,
        "oi_interpretation": writers_bias,
        "expert_summary": expert_summary,
        "recommended_strategy": strategy
    }

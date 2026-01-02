def generate_ai_summary(nifty, banknifty):
    def trend_text(pcr):
        if pcr > 1.3:
            return "strong bullish sentiment"
        elif pcr > 1.0:
            return "mild bullish sentiment"
        elif pcr < 0.7:
            return "strong bearish sentiment"
        elif pcr < 1.0:
            return "mild bearish sentiment"
        else:
            return "neutral behavior"

    # Extract values safely
    nifty_pcr = nifty.get("pcr", 0)
    bank_pcr = banknifty.get("pcr", 0)

    nifty_support = nifty.get("support")
    nifty_resistance = nifty.get("resistance")

    bank_support = banknifty.get("support")
    bank_resistance = banknifty.get("resistance")

    nifty_trend = trend_text(nifty_pcr)
    bank_trend = trend_text(bank_pcr)

    summary = f"""
📊 MARKET SUMMARY

📌 NIFTY:
- Trend: {nifty_trend}
- PCR: {nifty_pcr}
- Key Support: {nifty_support}
- Key Resistance: {nifty_resistance}

📌 BANKNIFTY:
- Trend: {bank_trend}
- PCR: {bank_pcr}
- Support: {bank_support}
- Resistance: {bank_resistance}

🧠 AI Outlook:
- Nifty is showing {nifty_trend}, indicating potential movement between {nifty_support} and {nifty_resistance}.
- BankNifty is showing {bank_trend}. If support at {bank_support} holds, upside toward {bank_resistance} is likely.

⚠ NOTE:
Market data may vary due to NSE blocking or delay. 
This is an AI-generated summary for insights, not financial advice.
"""

    return summary.strip()

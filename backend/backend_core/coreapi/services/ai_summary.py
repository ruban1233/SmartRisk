def generate_ai_summary(capital, risk_profile, allocation, portfolio):

    summary = f"""
AI Financial Doctor Portfolio Explanation

Capital Invested: ₹{capital}

Risk Profile: {risk_profile.upper()}

Portfolio Allocation Strategy

Stocks ({allocation['stocks']}%)
Large-cap stocks are selected for long-term capital growth.

ETF Allocation ({allocation['etf']}%)
ETFs provide diversified exposure to the entire market index.

Mutual Funds ({allocation['mutual_funds']}%)
Mutual funds allow professional managers to diversify investments.

Gold Allocation ({allocation['gold']}%)
Gold acts as a hedge against inflation and market volatility.

Cash Reserve ({allocation['cash']}%)
Maintaining cash helps capture opportunities during market dips.

Educational Purpose:
This portfolio demonstrates diversification, risk control,
and long-term investing principles.
"""

    return summary.strip()
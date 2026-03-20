from typing import Dict, List


class DynamicRiskEngine:
    """
    SMART RISK ENGINE (FINAL VERSION)
    """

    def __init__(
        self,
        capital: float,
        days_to_expiry: int,
        option_premium: float,
        theta: float,
        iv_level: str,
        strategy_type: str,
    ):
        self.capital = capital
        self.days_to_expiry = days_to_expiry
        self.option_premium = option_premium
        self.theta = abs(theta)
        self.iv_level = (iv_level or "normal").lower()
        self.strategy_type = (strategy_type or "unknown").lower()

        self.reasons: List[str] = []
        self.total_score = 0

    def capital_risk(self):
        if self.capital < 25_000:
            self.total_score += 25
            self.reasons.append("Capital below ₹25,000")
        elif self.capital < 50_000:
            self.total_score += 15
        elif self.capital < 100_000:
            self.total_score += 8
        else:
            self.total_score += 3

    def expiry_risk(self):
        if self.days_to_expiry <= 1:
            self.total_score += 30
            self.reasons.append("Expiry within 1 day (high risk)")
        elif self.days_to_expiry <= 3:
            self.total_score += 20
        elif self.days_to_expiry <= 7:
            self.total_score += 10
        else:
            self.total_score += 5

        if self.capital < 50_000 and self.days_to_expiry <= 1:
            self.total_score += 100
            self.reasons.append("Low capital + near expiry → FORCED NO TRADE")

    def theta_risk(self):
        if self.option_premium <= 0:
            return

        theta_ratio = self.theta / self.option_premium

        if theta_ratio > 0.03:
            self.total_score += 25
            self.reasons.append("High theta decay (>3%)")
        elif theta_ratio > 0.01:
            self.total_score += 15
        else:
            self.total_score += 5

    def iv_risk(self):
        if self.iv_level == "high_falling":
            self.total_score += 25
            self.reasons.append("High IV crash risk")
        elif self.iv_level == "high":
            self.total_score += 15
        elif self.iv_level == "normal":
            self.total_score += 8
        else:
            self.total_score += 3

    def strategy_risk(self):
        if self.strategy_type in ["short_straddle", "short_strangle"]:
            self.total_score += 30
            self.reasons.append("Unlimited loss strategy")
        elif self.strategy_type in ["iron_condor"]:
            self.total_score += 12
        elif self.strategy_type in ["debit_spread"]:
            self.total_score += 8
        else:
            self.total_score += 5

    def evaluate(self) -> Dict:

        self.capital_risk()
        self.expiry_risk()
        self.theta_risk()
        self.iv_risk()
        self.strategy_risk()

        final_score = min(self.total_score, 100)

        if final_score > 60:
            signal = "RED"
        elif final_score > 30:
            signal = "YELLOW"
        else:
            signal = "GREEN"

        return {
            "risk_score": final_score,
            "signal": signal,
            "reasons": list(set(self.reasons)),
        }
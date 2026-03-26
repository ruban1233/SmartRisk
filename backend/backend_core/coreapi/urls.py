"""
urls.py
Path: backend/coreapi/urls.py
"""

from django.urls import path
from .views import get_expiries_view
from coreapi import views

urlpatterns = [
    path("health/",                views.health),
    path("angel-login/",           views.angel_login),
    path("market-status/",         views.market_status),
    path("test-ltp/",              views.test_ltp_view),
    path("atm-strike/",            views.atm_strike_view),
    path("market-sentiment/",      views.market_sentiment_view),
    path("option-chain-analysis/", views.option_chain_analysis_view),
    path("smartrisk/",             views.smartrisk_view),
    path("investment-planner/",    views.investment_planner_view),
    path("test-iv/",               views.iv_test_view),
    path("option-greeks/",         views.option_greeks_view),
    path("test-option-price/",     views.test_option_price),
    path("full-option-chain/",     views.full_option_chain_view),
    path("ai-strategy/",           views.ai_strategy_view),
    path("payoff/",                views.payoff_view),
    path("option-doctor/",         views.option_doctor_view),

    # ✅ NEW — Auto expiry info
    path("expiry/",                views.expiry_info_view),
    path("expiries/", get_expiries_view),
]
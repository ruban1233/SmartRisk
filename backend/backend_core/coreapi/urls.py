from django.urls import path
from coreapi import views

urlpatterns = [

    # =======================
    # SYSTEM / HEALTH
    # =======================
    path("health/", views.health),
    path("angel-login/", views.angel_login),
    path("market-status/", views.market_status),

    # =======================
    # MARKET DATA
    # =======================
    path("prices/", views.prices),                 # placeholder (safe)
    path("test-ltp/", views.test_ltp_view),
    path("atm-strike/", views.atm_strike_view),
    path("option-chain/<str:symbol>/", views.option_chain),

    # =======================
    # ANALYSIS & CORE ENGINES
    # =======================
    path("market-sentiment/", views.market_sentiment_view),
    path("smartrisk/", views.smartrisk_view),
    path("investment-planner/", views.investment_planner_view),

    # =======================
    # OPTION DOCTOR
    # =======================
    path("option-doctor/", views.option_doctor_view),

    # =======================
    # UTILITIES / DASHBOARD
    # =======================
    path("dashboard/", views.dashboard),
    path("strategy/", views.strategy),
    path("pl/", views.pl_calculator),
]

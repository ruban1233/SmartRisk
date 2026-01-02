from django.urls import path
from coreapi import views

urlpatterns = [
    path("health/", views.health),
    path("angel-login/", views.angel_login),
    path("market-status/", views.market_status),
    path("option-chain/<str:symbol>/", views.option_chain),
    path("dashboard/", views.dashboard),
    path("strategy/", views.strategy),
    path("pl/", views.pl_calculator),
    path("prices/", views.prices),
    path("test-ltp/", views.test_ltp_view),

    # ✅ ADD THIS LINE
    path("atm-strike/", views.atm_strike_view),
]

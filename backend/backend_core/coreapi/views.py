from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from coreapi.services.angel_ltp import get_ltp
from coreapi.services.atm_strike import get_atm_strike


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})


@api_view(["GET"])
def angel_login(request):
    return Response({"status": "login handled in service"})


@api_view(["GET"])
def market_status(request):
    return Response({"market": "open"})


@api_view(["GET"])
def option_chain(request, symbol):
    return Response({"symbol": symbol})


@api_view(["GET"])
def dashboard(request):
    return Response({"dashboard": "ok"})


@api_view(["GET"])
def strategy(request):
    return Response({"strategy": "ok"})


@api_view(["POST"])
def pl_calculator(request):
    return Response({"pl": "ok"})


@api_view(["GET"])
def prices(request):
    return Response({"prices": "ok"})


@api_view(["GET"])
def test_ltp_view(request):
    symbol = request.GET.get("symbol", "NIFTY")
    ltp = get_ltp(symbol)
    return Response({"symbol": symbol, "ltp": ltp})


@api_view(["GET"])
def atm_strike_view(request):
    symbol = request.GET.get("symbol")

    if not symbol:
        return Response(
            {"error": "symbol query param required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        ltp = get_ltp(symbol)
        atm = get_atm_strike(ltp, symbol)

        return Response({
            "symbol": symbol.upper(),
            "ltp": ltp,
            "atm_strike": atm
        })

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# SmartRisk Backend

SmartRisk is a Django REST backend for options trading analytics (Opstra-style).

## Features Implemented
- Health Check API
- Angel One LTP Fetch
- ATM Strike Calculation (NIFTY / BANKNIFTY)
- Modular Service-Based Architecture

## ATM Strike API

### Endpoint
GET /api/atm-strike/?symbol=NIFTY

### Response
```json
{
  "symbol": "NIFTY",
  "ltp": 26328.55,
  "atm_strike": 26350
}

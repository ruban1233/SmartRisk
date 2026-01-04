from SmartApi import SmartConnect
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_ID = os.getenv("ANGEL_CLIENT_ID")
MPIN = os.getenv("ANGEL_MPIN")
TOTP_SECRET = os.getenv("ANGEL_TOTP_SECRET")

smart = SmartConnect(api_key=API_KEY)

# 1️⃣ Generate TOTP
totp = pyotp.TOTP(TOTP_SECRET).now()
print("TOTP:", totp)

# 2️⃣ Login
data = smart.generateSession(CLIENT_ID, MPIN, totp)
print("LOGIN RESPONSE:", data)

# 3️⃣ 🔥 STRIP BEARER
jwt = data["data"]["jwtToken"]
if jwt.startswith("Bearer "):
    jwt = jwt.replace("Bearer ", "")

# 4️⃣ Set token CORRECTLY
smart.setAccessToken(jwt)

# 5️⃣ Call LTP
res = smart.ltpData("NSE", "NIFTY BANK", "26009")
print("LTP RESPONSE:", res)
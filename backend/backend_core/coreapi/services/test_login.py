from SmartApi import SmartConnect
import pyotp

API_KEY = "t8pke43u"
USER_ID = "AAAS174267"      
MPIN = "6379"    
TOTP_SECRET = "YCH3OKDS4WXJW2OKGXOLPSRGCE"

totp = pyotp.TOTP(TOTP_SECRET).now()

obj = SmartConnect(api_key=API_KEY)
print(obj.generateSession(CLIENT_ID, PIN, totp))

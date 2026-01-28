import requests
import smtplib
from email.mime.text import MIMEText

# ========= SETTINGS =========
INTERVAL = "1m"
THRESHOLD = 0.04  # %

EMAIL_FROM = "YOUR_EMAIL@gmail.com"
EMAIL_TO = "YOUR_EMAIL@gmail.com"
EMAIL_APP_PASSWORD = "YOUR_APP_PASSWORD"

SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
    "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT"
]
# ============================

def get_candles(symbol):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": INTERVAL,
        "limit": 7
    }
    return requests.get(url, params=params, timeout=10).json()

def candle_change(c):
    o = float(c[1])
    c_ = float(c[4])
    return ((c_ - o) / o) * 100

alerts = []

for symbol in SYMBOLS:
    candles = get_candles(symbol)

    c4, c3, c2, c1 = candles[-5], candles[-4], candles[-3], candles[-2]

    c1_close = float(c1[4])
    c1_high  = float(c1[2])
    c1_low   = float(c1[3])

    c2_close = float(c2[4])
    c2_high  = float(c2[2])
    c2_low   = float(c2[3])

    high_4 = max(float(x[2]) for x in [c2, c3, c4])
    low_4  = min(float(x[3]) for x in [c2, c3, c4])

    c1_change = candle_change(c1)
    c2_change = candle_change(c2)

    # -------- BULLISH --------
    if (
        c1_close > c2_high and
        c2_close > high_4 and
        c1_change >= THRESHOLD and
        c2_change >= THRESHOLD
    ):
        alerts.append(
            f"🚀 {symbol} BULLISH\n"
            f"C1: {c1_change:.3f}% | C2: {c2_change:.3f}% | Price: {c1_close}\n"
        )

    # -------- BEARISH --------
    if (
        c1_close < c2_low and
        c2_close < low_4 and
        c1_change <= -THRESHOLD and
        c2_change <= -THRESHOLD
    ):
        alerts.append(
            f"🔻 {symbol} BEARISH\n"
            f"C1: {c1_change:.3f}% | C2: {c2_change:.3f}% | Price: {c1_close}\n"
        )

# -------- SEND EMAIL --------
if alerts:
    body = "\n".join(alerts)
    msg = MIMEText(body)
    msg["Subject"] = "🚨 1-MIN CRYPTO ALERT (TOP-10)"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_APP_PASSWORD)
        server.send_message(msg)

    print("ALERT SENT")
else:
    print("No signals")

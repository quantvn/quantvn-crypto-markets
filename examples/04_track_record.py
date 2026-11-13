"""Send live positions to the QuantVN Track Record service (https://paper.quantvn.com).

The service records when each position ARRIVED and prices it later from its own Binance data, at the open of
the first 1-minute bar after that moment. Nothing you send can set a price.

    QUANTVN_EMAIL=you@example.com QUANTVN_API_KEY=... python examples/04_track_record.py
"""
import os
import sys

from quantvn.crypto.data import get_crypto_hist
from quantvn.paper import TrackRecord

email, key = os.environ.get("QUANTVN_EMAIL"), os.environ.get("QUANTVN_API_KEY")
if not (email and key):
    sys.exit("set QUANTVN_EMAIL and QUANTVN_API_KEY (the API key from your QuantVN profile)")

tr = TrackRecord(email=email, api_key=key)
open_now = {a["asset"] for a in tr.assets() if a["market"].startswith("CRYPTO")}
print(f"{len(open_now)} crypto instruments accept positions, e.g. {sorted(open_now)[:5]}")

# decide from the last closed hourly bars
bars = get_crypto_hist("BTCUSDT", "1h", start="2026-11-01", end=None, tz=None)
weight = 1.0 if bars["Close"].iloc[-1] > bars["Close"].tail(24).mean() else 0.0
print(tr.send("btc-trend-example", "BTCUSDT", weight))      # CRYPTO spot: 0..1
print(tr.bots())

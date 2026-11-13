"""Crypto data with `pip install quantvn`: spot and perpetual bars, funding rates.

    python examples/01_data.py
"""
import quantvn
from quantvn.crypto.data import get_crypto_hist, get_funding_rates, list_crypto_symbols

# quantvn.client(apikey="...")        # optional: the key of your QuantVN account raises the rate limits

print("spot pairs:", ", ".join(list_crypto_symbols("spot")[:10]), "...")
print("perpetuals:", ", ".join(list_crypto_symbols("perp")[:10]), "...")

# hourly BTC spot bars for October 2026, labelled by OPEN time in UTC
btc = get_crypto_hist("BTCUSDT", "1h", start="2026-10-01", end="2026-11-01", tz=None)
print(btc.head(3), f"\n{len(btc)} hourly bars")

# 1-minute ETH perpetual bars for one day, in Vietnam time (the default, as in quantvn 0.2)
eth = get_crypto_hist("ETHUSDT", "1m", start="2026-11-10", end="2026-11-11", market="perp")
print(eth.tail(3), f"\n{len(eth)} one-minute bars")

# funding events of the BTC perpetual: a long pays rate x notional when the rate is positive
fund = get_funding_rates("BTCUSDT", start="2026-10-01", end="2026-11-01")
print(fund.head(3))
print(f"{len(fund)} funding events, mean rate {fund['rate'].mean() * 1e4:.2f} bp, "
      f"sum {fund['rate'].sum() * 100:.3f}% of notional over the month")

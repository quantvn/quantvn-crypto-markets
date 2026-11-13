"""Backtest a spot strategy with the library's Backtest_Crypto and compare with paper.simulate.

Backtest_Crypto works in price units (one coin held); paper.simulate in shares of equity, compounded.
Both fill a decision at the open of the next bar.

    python examples/03_backtest_spot.py
"""
import numpy as np

from quantvn import paper
from quantvn.crypto.data import get_crypto_hist
from quantvn.crypto.metrics import Backtest_Crypto

df = get_crypto_hist("SOLUSDT", "1h", start="2026-06-01", end="2026-11-01", tz=None)
r = df["Close"].pct_change()
df["position"] = np.where(r.rolling(24).mean() > 0, 1.0, 0.0)     # long after a rising day, flat otherwise

bt = Backtest_Crypto(df, pnl_type="after_fees", transaction_fee_pct=0.001)
print("Backtest_Crypto: profit per coin held, after 0.1% fees:", round(float(bt.PNL().iloc[-1]), 2))

sim = paper.simulate(df, market="CRYPTO")
print("paper.simulate (Track Record rules, 10 bp per side):", sim)

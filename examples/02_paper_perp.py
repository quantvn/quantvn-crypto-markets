"""A moving-average strategy on the ETH perpetual, priced the way the QuantVN Track Record service prices it:
filled at the next bar's open, 5 bp per side, funding paid or received at every funding event.

    python examples/02_paper_perp.py
"""
import numpy as np

from quantvn import paper
from quantvn.crypto.data import get_crypto_hist, get_funding_rates

START, END = "2026-09-01", "2026-11-01"

df = get_crypto_hist("ETHUSDT", "15m", start=START, end=END, market="perp", tz=None)
fast, slow = df["Close"].rolling(16).mean(), df["Close"].rolling(96).mean()
df["position"] = np.where(fast > slow, 1.0, -1.0)       # long above the slow average, short below
df.loc[slow.isna(), "position"] = 0.0                     # flat until the averages exist

funding = get_funding_rates("ETHUSDT", start=START, end=END)

with_funding = paper.simulate(df, market="CRYPTO_PERP", funding=funding)
without = paper.simulate(df, market="CRYPTO_PERP")
print("with funding   :", with_funding)
print("without funding:", without)
print(f"funding paid (fraction of equity, summed): {with_funding.stats['funding']:+.4%}")
print(with_funding.daily.tail())
